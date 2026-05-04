"""SQLAlchemy database models for OmniNode."""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, LargeBinary, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.core.database import Base


class User(Base):
    """User model for authentication and session management."""
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    mcp_servers = relationship("MCPServer", back_populates="owner")


class MCPServer(Base):
    """MCP Server configuration model."""
    
    __tablename__ = "mcp_servers"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Server identification
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Transport configuration
    transport_type = Column(String(20), nullable=False)  # 'stdio' or 'sse'
    
    # For stdio transport
    command = Column(String(255), nullable=True)  # e.g., 'npx', 'python', etc.
    args = Column(JSON, nullable=True)  # List of command arguments
    
    # For SSE transport
    url = Column(String(500), nullable=True)  # SSE endpoint URL
    
    # Environment variables (encrypted)
    env_encrypted = Column(LargeBinary, nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    last_connected = Column(DateTime(timezone=True), nullable=True)
    connection_status = Column(String(20), default="pending")  # pending, active, error
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    owner = relationship("User", back_populates="mcp_servers")
    tools = relationship("ToolCache", back_populates="server", cascade="all, delete-orphan")
    resources = relationship("ResourceCache", back_populates="server", cascade="all, delete-orphan")


class ToolCache(Base):
    """Cache of tools discovered from MCP servers."""
    
    __tablename__ = "tool_cache"
    
    id = Column(Integer, primary_key=True, index=True)
    server_id = Column(Integer, ForeignKey("mcp_servers.id"), nullable=False)
    
    # Tool information
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    input_schema = Column(JSON, nullable=True)  # JSON Schema for tool parameters
    
    # Metadata
    last_discovered = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    server = relationship("MCPServer", back_populates="tools")


class ResourceCache(Base):
    """Cache of resources discovered from MCP servers."""
    
    __tablename__ = "resource_cache"
    
    id = Column(Integer, primary_key=True, index=True)
    server_id = Column(Integer, ForeignKey("mcp_servers.id"), nullable=False)
    
    # Resource information
    uri = Column(String(500), nullable=False, index=True)
    name = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    mime_type = Column(String(100), nullable=True)
    
    # Metadata
    last_discovered = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    server = relationship("MCPServer", back_populates="resources")


class ToolExecution(Base):
    """History of tool executions."""
    
    __tablename__ = "tool_executions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    server_id = Column(Integer, ForeignKey("mcp_servers.id"), nullable=False)
    
    # Execution details
    tool_name = Column(String(100), nullable=False)
    input_params = Column(JSON, nullable=True)
    output = Column(JSON, nullable=True)
    status = Column(String(20), default="pending")  # pending, success, error
    error_message = Column(Text, nullable=True)
    
    # Timing
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Metadata
    duration_ms = Column(Integer, nullable=True)
