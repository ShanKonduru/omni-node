"""MCP Server management API routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import json

from backend.core.database import get_db
from backend.core.security import encrypt_env_vars
from backend.models.models import MCPServer, User
from backend.schemas.schemas import MCPServerCreate, MCPServerResponse, MCPServerUpdate
from backend.services.mcp_client import update_tool_cache, update_resource_cache

router = APIRouter(prefix="/servers", tags=["servers"])


# Mock authentication - replace with real auth
async def get_current_user():
    """Get current authenticated user."""
    # TODO: Implement real JWT authentication
    return User(id=1, username="demo", email="demo@example.com")


@router.post("/", response_model=MCPServerResponse, status_code=status.HTTP_201_CREATED)
async def create_server(
    server_data: MCPServerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new MCP server configuration."""
    
    # Encrypt environment variables if provided
    env_encrypted = None
    if server_data.env:
        env_json = json.dumps(server_data.env)
        env_encrypted = encrypt_env_vars(env_json)
    
    # Create server
    server = MCPServer(
        user_id=current_user.id,
        name=server_data.name,
        description=server_data.description,
        transport_type=server_data.transport_type.value,
        command=server_data.command,
        args=server_data.args,
        url=server_data.url,
        env_encrypted=env_encrypted
    )
    
    db.add(server)
    db.commit()
    db.refresh(server)
    
    # Start background tool discovery
    # Note: In production, use Celery or background tasks
    try:
        await update_tool_cache(db, server)
        await update_resource_cache(db, server)
        server.connection_status = "active"
        db.commit()
    except Exception as e:
        server.connection_status = "error"
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Server created but discovery failed: {str(e)}"
        )
    
    return server


@router.get("/", response_model=List[MCPServerResponse])
async def list_servers(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all MCP servers for the current user."""
    servers = db.query(MCPServer).filter(
        MCPServer.user_id == current_user.id
    ).all()
    return servers


@router.get("/{server_id}", response_model=MCPServerResponse)
async def get_server(
    server_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific MCP server."""
    server = db.query(MCPServer).filter(
        MCPServer.id == server_id,
        MCPServer.user_id == current_user.id
    ).first()
    
    if not server:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Server not found"
        )
    
    return server


@router.put("/{server_id}", response_model=MCPServerResponse)
async def update_server(
    server_id: int,
    server_data: MCPServerUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update an MCP server configuration."""
    server = db.query(MCPServer).filter(
        MCPServer.id == server_id,
        MCPServer.user_id == current_user.id
    ).first()
    
    if not server:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Server not found"
        )
    
    # Update fields
    update_data = server_data.model_dump(exclude_unset=True)
    
    # Handle env encryption
    if "env" in update_data:
        env_json = json.dumps(update_data.pop("env"))
        server.env_encrypted = encrypt_env_vars(env_json)
    
    for field, value in update_data.items():
        setattr(server, field, value)
    
    db.commit()
    db.refresh(server)
    
    return server


@router.delete("/{server_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_server(
    server_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete an MCP server."""
    server = db.query(MCPServer).filter(
        MCPServer.id == server_id,
        MCPServer.user_id == current_user.id
    ).first()
    
    if not server:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Server not found"
        )
    
    db.delete(server)
    db.commit()


@router.post("/{server_id}/refresh", response_model=MCPServerResponse)
async def refresh_server_cache(
    server_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Refresh tool and resource cache for a server."""
    server = db.query(MCPServer).filter(
        MCPServer.id == server_id,
        MCPServer.user_id == current_user.id
    ).first()
    
    if not server:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Server not found"
        )
    
    try:
        await update_tool_cache(db, server)
        await update_resource_cache(db, server)
        server.connection_status = "active"
        db.commit()
    except Exception as e:
        server.connection_status = "error"
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to refresh cache: {str(e)}"
        )
    
    return server
