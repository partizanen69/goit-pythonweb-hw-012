"""Authentication utility functions.

This module provides utility functions for password hashing and verification.
"""

from datetime import datetime, timedelta, UTC
from typing import Optional, Dict
from jose import JWTError, jwt
from passlib.context import CryptContext
from src.conf.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash.

    Args:
        plain_password (str): Plain text password to verify
        hashed_password (str): Hashed password to verify against

    Returns:
        bool: True if password matches hash, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Generate a hash from a password.

    Args:
        password (str): Password to hash

    Returns:
        str: Hashed password
    """
    return pwd_context.hash(password)
