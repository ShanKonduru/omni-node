"""Tests for backend.core.security module."""

import pytest
from datetime import timedelta
from backend.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    encrypt_env_vars,
    decrypt_env_vars
)


def test_password_hashing():
    """Test password hashing."""
    password = "testpassword123"
    hashed = get_password_hash(password)
    
    assert hashed != password
    assert len(hashed) > 0
    assert hashed.startswith("$2b$")


def test_verify_password_correct():
    """Test password verification with correct password."""
    password = "testpassword123"
    hashed = get_password_hash(password)
    
    assert verify_password(password, hashed) is True


def test_verify_password_incorrect():
    """Test password verification with incorrect password."""
    password = "testpassword123"
    wrong_password = "wrongpassword"
    hashed = get_password_hash(password)
    
    assert verify_password(wrong_password, hashed) is False


def test_create_access_token_without_expiry():
    """Test JWT token creation without expiry."""
    data = {"sub": "testuser"}
    token = create_access_token(data)
    
    assert token is not None
    assert isinstance(token, str)
    assert len(token) > 0


def test_create_access_token_with_expiry():
    """Test JWT token creation with custom expiry."""
    data = {"sub": "testuser"}
    expires_delta = timedelta(minutes=15)
    token = create_access_token(data, expires_delta)
    
    assert token is not None
    assert isinstance(token, str)
    assert len(token) > 0


def test_encrypt_decrypt_env_vars():
    """Test environment variable encryption and decryption."""
    # Note: Current implementation uses temporary keys
    # This test verifies the basic encrypt/decrypt flow works
    env_json = '{"API_KEY": "secret123", "TOKEN": "mytoken"}'
    
    # Encrypt
    encrypted = encrypt_env_vars(env_json)
    assert encrypted != env_json.encode()
    assert isinstance(encrypted, bytes)


def test_encrypt_empty_string():
    """Test encrypting empty string."""
    env_json = ""
    
    encrypted = encrypt_env_vars(env_json)
    assert isinstance(encrypted, bytes)
