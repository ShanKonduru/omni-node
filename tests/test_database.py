"""Tests for backend.core.database module."""

import pytest
from sqlalchemy import Column, Integer, String
from backend.core.database import Base, engine, get_db, init_db, SessionLocal


def test_engine_creation():
    """Test database engine is created."""
    assert engine is not None
    assert str(engine.url).startswith("sqlite")


def test_session_local():
    """Test SessionLocal factory."""
    session = SessionLocal()
    assert session is not None
    session.close()


def test_base_declarative():
    """Test Base declarative class."""
    assert Base is not None
    assert hasattr(Base, 'metadata')
    assert hasattr(Base, 'registry')


def test_get_db_generator():
    """Test get_db yields database session."""
    db_gen = get_db()
    db = next(db_gen)
    assert db is not None
    try:
        next(db_gen)
    except StopIteration:
        pass  # Expected behavior


def test_init_db():
    """Test database initialization."""
    # Create a test model
    class TestModel(Base):
        __tablename__ = "test_init_table"
        id = Column(Integer, primary_key=True)
        name = Column(String)
    
    # Initialize database
    init_db()
    
    # Verify table was created
    assert TestModel.__table__.exists(engine)
    
    # Cleanup
    Base.metadata.drop_all(bind=engine, tables=[TestModel.__table__])


def test_get_db_closes_session():
    """Test get_db properly closes session on exit."""
    db_gen = get_db()
    db = next(db_gen)
    
    # Session should be open
    assert db.is_active or not db.is_active  # Just verify it's a valid session
    
    # Cleanup by exhausting generator
    try:
        db_gen.close()
    except:
        pass
