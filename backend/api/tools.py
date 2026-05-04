"""Tool execution and autocomplete API routes."""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from backend.core.database import get_db
from backend.models.models import User, ToolExecution, MCPServer
from backend.schemas.schemas import (
    ToolExecuteRequest,
    ToolExecuteResponse,
    AutocompleteResponse,
    AutocompleteResult,
    ToolWithServer
)
from backend.services.namespace_resolver import (
    NamespaceResolver,
    AmbiguityError,
    ToolNotFoundError
)
from backend.services.mcp_client import MCPClient

router = APIRouter(prefix="/tools", tags=["tools"])


# Mock authentication - replace with real auth
async def get_current_user():
    """Get current authenticated user."""
    # TODO: Implement real JWT authentication
    return User(id=1, username="demo", email="demo@example.com")


@router.get("/autocomplete", response_model=AutocompleteResponse)
async def autocomplete_tools(
    prefix: Optional[str] = Query(None, description="Command prefix to filter by"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get autocomplete suggestions for slash commands.
    
    Returns all available tools with namespace information.
    """
    resolver = NamespaceResolver(db, current_user.id)
    tools = resolver.get_all_tools(prefix=prefix)
    
    # Convert to autocomplete results
    results = []
    for tool in tools:
        # Check if this tool name is ambiguous
        is_ambiguous, servers = resolver.check_ambiguity(tool.name)
        
        # Use simple name if unique, otherwise use fully qualified
        command = f"/{tool.name}" if not is_ambiguous else f"/{tool.fully_qualified_name}"
        
        results.append(AutocompleteResult(
            command=command,
            description=tool.description,
            server_name=tool.server_name,
            is_ambiguous=is_ambiguous
        ))
    
    return AutocompleteResponse(
        results=results,
        total=len(results)
    )


@router.get("/", response_model=List[ToolWithServer])
async def list_tools(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all available tools."""
    resolver = NamespaceResolver(db, current_user.id)
    return resolver.get_all_tools()


@router.post("/execute", response_model=ToolExecuteResponse)
async def execute_tool(
    request: ToolExecuteRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Execute a tool via slash command.
    
    Supports both simple names (/tool_name) and fully qualified names (/server.tool_name).
    """
    resolver = NamespaceResolver(db, current_user.id)
    
    try:
        # Resolve the tool path
        tool, server = resolver.resolve_tool(request.tool_path)
    except AmbiguityError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "ambiguous_tool",
                "message": str(e),
                "tool_name": e.tool_name,
                "servers": e.servers
            }
        )
    except ToolNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "tool_not_found",
                "message": str(e),
                "tool_path": e.tool_path
            }
        )
    
    # Create execution record
    execution = ToolExecution(
        user_id=current_user.id,
        server_id=server.id,
        tool_name=tool.name,
        input_params=request.params,
        status="pending",
        started_at=datetime.utcnow()
    )
    db.add(execution)
    db.commit()
    db.refresh(execution)
    
    # Execute the tool
    try:
        client = MCPClient(server)
        result = await client.execute_tool(tool.name, request.params or {})
        
        # Update execution record
        execution.status = "success"
        execution.output = result
        execution.completed_at = datetime.utcnow()
        execution.duration_ms = int(
            (execution.completed_at - execution.started_at).total_seconds() * 1000
        )
        db.commit()
        
    except Exception as e:
        execution.status = "error"
        execution.error_message = str(e)
        execution.completed_at = datetime.utcnow()
        execution.duration_ms = int(
            (execution.completed_at - execution.started_at).total_seconds() * 1000
        )
        db.commit()
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "execution_failed",
                "message": str(e),
                "execution_id": execution.id
            }
        )
    
    return ToolExecuteResponse(
        id=execution.id,
        tool_name=tool.name,
        server_name=server.name,
        status=execution.status,
        output=execution.output,
        error_message=execution.error_message,
        started_at=execution.started_at,
        completed_at=execution.completed_at,
        duration_ms=execution.duration_ms
    )


@router.get("/history", response_model=List[ToolExecuteResponse])
async def get_execution_history(
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get execution history for the current user."""
    executions = (
        db.query(ToolExecution, MCPServer.name)
        .join(MCPServer, ToolExecution.server_id == MCPServer.id)
        .filter(ToolExecution.user_id == current_user.id)
        .order_by(ToolExecution.started_at.desc())
        .limit(limit)
        .all()
    )
    
    results = []
    for execution, server_name in executions:
        results.append(ToolExecuteResponse(
            id=execution.id,
            tool_name=execution.tool_name,
            server_name=server_name,
            status=execution.status,
            output=execution.output,
            error_message=execution.error_message,
            started_at=execution.started_at,
            completed_at=execution.completed_at,
            duration_ms=execution.duration_ms
        ))
    
    return results
