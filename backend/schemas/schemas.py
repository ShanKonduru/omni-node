"""Pydantic schemas for request/response validation."""

from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class TransportType(str, Enum):
    """MCP transport types."""
    STDIO = "stdio"
    SSE = "sse"


class ConnectionStatus(str, Enum):
    """Server connection status."""
    PENDING = "pending"
    ACTIVE = "active"
    ERROR = "error"


# User schemas
class UserBase(BaseModel):
    """Base user schema."""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr


class UserCreate(UserBase):
    """Schema for user creation."""
    password: str = Field(..., min_length=8)


class UserResponse(UserBase):
    """Schema for user response."""
    id: int
    is_active: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# MCP Server schemas
class MCPServerBase(BaseModel):
    """Base MCP server schema."""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    transport_type: TransportType


class MCPServerCreate(MCPServerBase):
    """Schema for creating an MCP server."""
    command: Optional[str] = None
    args: Optional[List[str]] = None
    url: Optional[str] = None
    env: Optional[Dict[str, str]] = None  # Will be encrypted before storage


class MCPServerUpdate(BaseModel):
    """Schema for updating an MCP server."""
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    command: Optional[str] = None
    args: Optional[List[str]] = None
    url: Optional[str] = None
    env: Optional[Dict[str, str]] = None


class MCPServerResponse(MCPServerBase):
    """Schema for MCP server response."""
    id: int
    user_id: int
    command: Optional[str] = None
    args: Optional[List[str]] = None
    url: Optional[str] = None
    is_active: bool
    connection_status: ConnectionStatus
    last_connected: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


# Tool schemas
class ToolCacheBase(BaseModel):
    """Base tool cache schema."""
    name: str
    description: Optional[str] = None
    input_schema: Optional[Dict[str, Any]] = None


class ToolCacheResponse(ToolCacheBase):
    """Schema for tool cache response."""
    id: int
    server_id: int
    last_discovered: datetime
    
    model_config = ConfigDict(from_attributes=True)


class ToolWithServer(ToolCacheResponse):
    """Tool with server information."""
    server_name: str
    fully_qualified_name: str  # e.g., "brave.google_search"


# Tool execution schemas
class ToolExecuteRequest(BaseModel):
    """Schema for tool execution request."""
    tool_path: str = Field(..., description="Tool name or fully qualified path (e.g., /tool_name or /server.tool_name)")
    params: Optional[Dict[str, Any]] = None


class ToolExecuteResponse(BaseModel):
    """Schema for tool execution response."""
    id: int
    tool_name: str
    server_name: str
    status: str
    output: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    started_at: datetime
    completed_at: Optional[datetime] = None
    duration_ms: Optional[int] = None
    
    model_config = ConfigDict(from_attributes=True)


# Resource schemas
class ResourceCacheResponse(BaseModel):
    """Schema for resource cache response."""
    id: int
    server_id: int
    uri: str
    name: Optional[str] = None
    description: Optional[str] = None
    mime_type: Optional[str] = None
    last_discovered: datetime
    
    model_config = ConfigDict(from_attributes=True)


# Token schemas
class Token(BaseModel):
    """JWT token response."""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token payload data."""
    username: Optional[str] = None


# Autocomplete schemas
class AutocompleteResult(BaseModel):
    """Autocomplete result for slash commands."""
    command: str
    description: Optional[str] = None
    server_name: str
    is_ambiguous: bool = False


class AutocompleteResponse(BaseModel):
    """Autocomplete response."""
    results: List[AutocompleteResult]
    total: int
