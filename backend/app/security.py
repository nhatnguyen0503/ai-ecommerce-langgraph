from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from pwdlib import PasswordHash

from app.config import get_settings

# Argon2 with pwdlib's recommended parameters; the salt is generated per hash
# and stored inside the hash string itself.
_password_hasher = PasswordHash.recommended()


class InvalidTokenError(Exception):
    """Raised when a token is malformed, tampered with, or expired."""


def hash_password(plain: str) -> str:
    """Hash a plain password using Argon2 and return the hash string."""
    return _password_hasher.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    """Verify a plain password against a hashed password. Returns True if valid, False otherwise."""
    return _password_hasher.verify(plain, hashed)


def create_access_token(
    subject: str,
    role: str,
    expires_delta: timedelta | None = None,
    now: datetime | None = None,
) -> str:
    """Create a JWT access token with the given subject and role,
    expiring after the specified timedelta."""
    settings = get_settings()
    now = now or datetime.now(UTC)
    expire = now + (expires_delta or timedelta(minutes=settings.access_token_expire_minutes))
    payload = {
        "sub": subject,
        "role": role,
        "exp": expire,
        "iat": now,
    }
    return jwt.encode(
        payload, settings.jwt_secret_key.get_secret_value(), algorithm=settings.jwt_algorithm
    )


def decode_access_token(token: str) -> dict[str, Any]:
    """Decode and verify a JWT. Raises InvalidTokenError on any problem."""
    settings = get_settings()
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key.get_secret_value(),
            algorithms=[settings.jwt_algorithm],
            options={"require": ["exp", "sub"]},
        )
        return payload
    except jwt.InvalidTokenError as exc:
        raise InvalidTokenError("Invalid or expired token") from exc
