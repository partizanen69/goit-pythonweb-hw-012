from datetime import datetime, timedelta, UTC
from typing import Optional, Dict
from jose import JWTError, jwt
from passlib.context import CryptContext
from src.conf.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)
