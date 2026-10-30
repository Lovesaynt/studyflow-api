"""Security utilities for password hashing and JWT token handling."""

from datetime import UTC, datetime, timedelta

import jwt
from passlib.hash import argon2
from pydantic import ValidationError

from app.core.config import get_settings


def hash_password(password: str) -> str:
    """Hash a password using Argon2."""
    return argon2.hash(password)  # type: ignore[no-any-return]


def verify_password(password: str, password_hash: str) -> bool:
    """Verify a password against its hash."""
    try:
        return argon2.verify(password, password_hash)  # type: ignore[no-any-return]
    except Exception:
        return False


def create_access_token(
    subject: str,
    expires_delta: timedelta | None = None,
) -> str:
    """Create a JWT access token."""
    settings = get_settings()
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode = {"sub": str(subject), "exp": expire}
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )
    return encoded_jwt


def decode_token(token: str) -> str | None:
    """Decode and validate a JWT token, returning the subject (user_id)."""
    settings = get_settings()
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        return payload.get("sub")  # type: ignore[no-any-return]
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, ValidationError):
        return None
