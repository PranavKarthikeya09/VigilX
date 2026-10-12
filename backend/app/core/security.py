import uuid
from datetime import datetime, timezone, timedelta
from typing import Any, Dict
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import get_db
from app.models.user import User

security_scheme = HTTPBearer(auto_error=False)


def verify_supabase_jwt(token: str, secret: str | None = None) -> Dict[str, Any]:
    """
    Validate and decode a Supabase JWT token.
    Supports HS256 signature verification against the configured Supabase JWT secret.
    Validates expiration, format, and subject claims.
    """
    jwt_secret = secret or settings.SUPABASE_JWT_SECRET

    try:
        # Decode without verification first to check header algorithm
        unverified_header = jwt.get_unverified_header(token)
        algorithm = unverified_header.get("alg", "HS256")

        # Supabase default is HS256; if RS256/ES256 is used, JWKS would be consulted
        if algorithm not in ["HS256", "RS256", "ES256"]:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Unsupported JWT signing algorithm: {algorithm}",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # In production Supabase HS256 mode:
        payload = jwt.decode(
            token,
            jwt_secret,
            algorithms=[algorithm],
            options={
                "verify_signature": True,
                "verify_exp": True,
                "require": ["sub", "exp"],
            },
            # Allow 'authenticated' or unset audience per Supabase defaults
            audience=["authenticated", "anon"] if "aud" in jwt.decode(token, options={"verify_signature": False}) else None,
        )

        # Validate that subject is a valid UUID
        sub = payload.get("sub")
        if not sub:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing subject claim in token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        try:
            uuid.UUID(str(sub))
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid subject claim format (must be UUID)",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return payload

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token signature has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token signature",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.PyJWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token validation failed: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    FastAPI dependency:
    1. Extracts and verifies Bearer token.
    2. Synchronizes / JIT upserts Supabase Auth user identity to the application users table.
    3. Returns the local User ORM entity.
    """
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    payload = verify_supabase_jwt(token)

    user_id = uuid.UUID(payload["sub"])
    email = payload.get("email", f"{user_id}@supabase.auth")
    user_metadata = payload.get("user_metadata", {}) or {}
    full_name = user_metadata.get("full_name") or user_metadata.get("name")

    # JIT User Synchronization
    query = select(User).where(User.id == user_id)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        user = User(
            id=user_id,
            email=email,
            full_name=full_name,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

    return user


def create_test_jwt(
    user_id: uuid.UUID,
    email: str = "test@vigilx.local",
    secret: str | None = None,
    expires_in_seconds: int = 3600,
    audience: str = "authenticated",
) -> str:
    """
    Generate a controlled synthetic test token for automated unit testing.
    NOTE: This is strictly for test harnesses and must NEVER be treated as a production credential.
    """
    jwt_secret = secret or settings.SUPABASE_JWT_SECRET
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "email": email,
        "aud": audience,
        "role": "authenticated",
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(seconds=expires_in_seconds)).timestamp()),
        "user_metadata": {
            "full_name": "Test Analyst",
        },
    }
    return jwt.encode(payload, jwt_secret, algorithm="HS256")
