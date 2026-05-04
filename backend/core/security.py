"""Security utilities for encryption and authentication."""

from cryptography.fernet import Fernet
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import JWTError, jwt
from typing import Optional
from .config import get_settings

settings = get_settings()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt


def encrypt_env_vars(env_json: str) -> bytes:
    """Encrypt environment variables using Fernet."""
    key = settings.encryption_key.encode()
    # Ensure the key is 32 bytes for Fernet (base64 encoded)
    # In production, use a properly generated Fernet key
    fernet = Fernet(Fernet.generate_key())  # TODO: Use persistent key from settings
    return fernet.encrypt(env_json.encode())


def decrypt_env_vars(encrypted_data: bytes) -> str:
    """Decrypt environment variables."""
    key = settings.encryption_key.encode()
    fernet = Fernet(Fernet.generate_key())  # TODO: Use persistent key from settings
    return fernet.decrypt(encrypted_data).decode()
