import hashlib
import hmac
import secrets
from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from app.core.config import settings
from fastapi import HTTPException, status
from fastapi.security import HTTPBearer

security_bearer = HTTPBearer(auto_error=False)


def hash_password(
    password: str,
    salt: str | None = None,
) -> str:
    """Hash password with PBKDF2-HMAC-SHA256."""
    if not salt:
        salt = secrets.token_hex(16)

    hashed = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        iterations=100_000,
    ).hex()

    return f"{salt}${hashed}"


def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:
    """Verify password against stored hash."""
    try:
        parts = hashed_password.split("$")

        if len(parts) != 2:
            return False

        salt, expected_hash = parts

        candidate_hash = hashlib.pbkdf2_hmac(
            "sha256",
            plain_password.encode("utf-8"),
            salt.encode("utf-8"),
            iterations=100_000,
        ).hex()

        return hmac.compare_digest(
            candidate_hash,
            expected_hash,
        )

    except (TypeError, ValueError, AttributeError):
        return False


def create_access_token(
    subject: str | Any,
    claims: dict[str, Any] | None = None,
    expires_delta: timedelta | None = None,
) -> str:
    """Create signed JWT access token."""
    now = datetime.now(UTC)

    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode = {
        "sub": str(subject),
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
        "type": "access",
    }

    if claims:
        to_encode.update(claims)

    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )

    return encoded_jwt


def create_refresh_token(
    subject: str | Any,
) -> str:
    """Create signed JWT refresh token."""
    now = datetime.now(UTC)

    expire = now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    to_encode = {
        "sub": str(subject),
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
        "type": "refresh",
    }

    return jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )


def decode_token(
    token: str,
) -> dict[str, Any]:
    """Decode and validate a JWT token."""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )

        return payload

    except jwt.ExpiredSignatureError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    except jwt.InvalidTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
