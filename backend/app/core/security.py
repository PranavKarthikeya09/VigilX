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


def verify_supabase_jwt(
    token: str,
    secret: str | None = None,
    expected_audience: str = "authenticated",
) -> Dict[str, Any]:
    """
    Validate and decode a Supabase JWT token.
    Enforces:
    - Algorithm constraint: Strictly HS256 for symmetric key verification.
    - Audience validation: Requires 'authenticated' (rejects 'anon' or missing aud).
    - Expiration validation: Token must be within valid lifetime (exp).
    - Subject validation: Must be present and formatted as a valid UUID (sub).
    - Issuer validation: Verified if SUPABASE_URL is configured (non-placeholder).
    """
    jwt_secret = secret or settings.SUPABASE_JWT_SECRET

    try:
        # 1. Inspect unverified header to ensure valid algorithm
        unverified_header = jwt.get_unverified_header(token)
        alg = unverified_header.get("alg")

        if alg != "HS256":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token algorithm: expected HS256, received {alg}",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # 2. Decode and verify signature, expiration, and required claims
        payload = jwt.decode(
            token,
            jwt_secret,
            algorithms=["HS256"],
            audience=expected_audience,
            options={
                "verify_signature": True,
                "verify_exp": True,
                "verify_aud": True,
                "require": ["sub", "exp", "aud"],
            },
        )

        # 3. Validate issuer if a real Supabase URL is configured
        if settings.SUPABASE_URL and not settings.SUPABASE_URL.startswith("https://placeholder"):
            expected_issuer = f"{settings.SUPABASE_URL.rstrip('/')}/auth/v1"
            token_issuer = payload.get("iss")
            if token_issuer and token_issuer.rstrip("/") != expected_issuer:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"Token issuer mismatch",
                    headers={"WWW-Authenticate": "Bearer"},
                )

        # 4. Validate subject claim format (must be valid UUID)
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
    except jwt.InvalidAudienceError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token audience (must be 'authenticated')",
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
    email: str = "analyst@vigilx.com",
    secret: str | None = None,
    expires_in_seconds: int = 3600,
    audience: str = "authenticated",
    algorithm: str = "HS256",
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
    return jwt.encode(payload, jwt_secret, algorithm=algorithm)
