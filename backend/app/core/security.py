import uuid
from datetime import datetime, timezone, timedelta
from typing import Any, Dict
import jwt
from jwt import PyJWKClient, PyJWK
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import get_db
from app.models.user import User

security_scheme = HTTPBearer(auto_error=False)

# In-memory cache for PyJWKClient instances by JWKS URL
_jwks_client_cache: Dict[str, PyJWKClient] = {}


def get_jwks_client(url: str) -> PyJWKClient:
    """Retrieve or create a cached PyJWKClient instance."""
    if url not in _jwks_client_cache:
        _jwks_client_cache[url] = PyJWKClient(
            url,
            cache_jwk_set=True,
            lifespan=3600,
        )
    return _jwks_client_cache[url]


def verify_supabase_jwt(
    token: str,
    public_key: Any = None,
    jwks_url: str | None = None,
    expected_audience: str = "authenticated",
) -> Dict[str, Any]:
    """
    Validate and decode a Supabase asymmetric JWT token (ECC P-256 / ES256).
    
    Security Controls:
    1. Algorithm Allowlist: Only algorithms in settings.allowed_jwt_algorithms_list
       (default: ['ES256']) are accepted.
    2. No Fallback: Never falls back to HS256 or unverified decoding if verification fails.
    3. Asymmetric Verification: Prefers JWKS key resolution or configured public key.
    4. Audience Validation: Requires audience='authenticated'.
    5. Expiration & Claims: Validates exp, sub (as valid UUID), and iss when configured.
    """
    try:
        # 1. Inspect unverified header to validate algorithm allowlist and key ID
        unverified_header = jwt.get_unverified_header(token)
        alg = unverified_header.get("alg")

        if not alg or alg not in settings.allowed_jwt_algorithms_list:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Unsupported or disallowed token algorithm: {alg}. Allowed: {settings.allowed_jwt_algorithms_list}",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # 2. Resolve verification key
        verification_key = None

        if public_key is not None:
            verification_key = public_key
        elif settings.SUPABASE_JWT_PUBLIC_KEY:
            verification_key = settings.SUPABASE_JWT_PUBLIC_KEY
        else:
            resolved_url = jwks_url or settings.resolved_jwks_url
            if resolved_url:
                try:
                    jwks_client = get_jwks_client(resolved_url)
                    signing_key = jwks_client.get_signing_key_from_jwt(token)
                    verification_key = signing_key.key
                except Exception as e:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail=f"Unable to retrieve public signing key from JWKS: {str(e)}",
                        headers={"WWW-Authenticate": "Bearer"},
                    )
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Authentication configuration error: No JWKS URL or public key configured for asymmetric JWT validation",
                )

        # 3. Decode and verify signature, expiration, and audience
        payload = jwt.decode(
            token,
            verification_key,
            algorithms=settings.allowed_jwt_algorithms_list,
            audience=expected_audience,
            options={
                "verify_signature": True,
                "verify_exp": True,
                "verify_aud": True,
                "require": ["sub", "exp", "aud"],
            },
        )

        # 4. Validate issuer if configured with a real Supabase domain
        if settings.SUPABASE_URL and not settings.SUPABASE_URL.startswith("https://placeholder"):
            expected_issuer = f"{settings.SUPABASE_URL.rstrip('/')}/auth/v1"
            token_issuer = payload.get("iss")
            if token_issuer and token_issuer.rstrip("/") != expected_issuer:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token issuer mismatch",
                    headers={"WWW-Authenticate": "Bearer"},
                )

        # 5. Validate subject claim format (must be valid UUID)
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

    except HTTPException:
        raise
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
    1. Extracts and verifies Bearer token using asymmetric verification.
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
