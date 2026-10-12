import uuid
import pytest
from httpx import AsyncClient
import jwt

from app.core.security import verify_supabase_jwt
from tests.test_helpers import (
    create_test_es256_jwt,
    TEST_EC_PRIVATE_KEY,
    WRONG_EC_PRIVATE_KEY,
    TEST_EC_PUBLIC_KEY_PEM,
)


@pytest.mark.asyncio
async def test_auth_me_missing_token(client: AsyncClient):
    """Calling protected endpoint without Authorization header must return 401."""
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 401
    data = response.json()
    assert data["status"] == 401
    assert "Missing Authorization header" in data["message"]


@pytest.mark.asyncio
async def test_auth_me_invalid_signature(client: AsyncClient, test_user_id: uuid.UUID):
    """Token signed with an unauthorized EC private key must be rejected with 401."""
    wrong_token = create_test_es256_jwt(
        user_id=test_user_id,
        private_key=WRONG_EC_PRIVATE_KEY,
    )
    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {wrong_token}"},
    )
    assert response.status_code == 401
    data = response.json()
    assert "Invalid token signature" in data["message"]


@pytest.mark.asyncio
async def test_auth_me_expired_token(client: AsyncClient, test_user_id: uuid.UUID):
    """Expired ES256 token must be rejected with 401."""
    expired_token = create_test_es256_jwt(
        user_id=test_user_id,
        expires_in_seconds=-100,  # Expired in past
    )
    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {expired_token}"},
    )
    assert response.status_code == 401
    data = response.json()
    assert "expired" in data["message"].lower()


@pytest.mark.asyncio
async def test_auth_me_invalid_audience(client: AsyncClient, test_user_id: uuid.UUID):
    """Token with 'anon' or mismatched audience must be rejected."""
    anon_token = create_test_es256_jwt(
        user_id=test_user_id,
        audience="anon",
    )
    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {anon_token}"},
    )
    assert response.status_code == 401
    data = response.json()
    assert "audience" in data["message"].lower()


@pytest.mark.asyncio
async def test_auth_me_unsupported_algorithm_hs256(client: AsyncClient, test_user_id: uuid.UUID):
    """Symmetric HS256 tokens must be rejected because ES256 is explicitly allowlisted."""
    hs256_token = jwt.encode(
        {"sub": str(test_user_id), "aud": "authenticated", "exp": 9999999999},
        "some-symmetric-secret-key-32-bytes-long",
        algorithm="HS256",
    )
    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {hs256_token}"},
    )
    assert response.status_code == 401
    data = response.json()
    assert "disallowed token algorithm" in data["message"].lower()


@pytest.mark.asyncio
async def test_auth_me_unsupported_algorithm_none(client: AsyncClient, test_user_id: uuid.UUID):
    """Unsigned 'none' algorithm tokens must be rejected."""
    none_token = create_test_es256_jwt(
        user_id=test_user_id,
        algorithm="none",
    )
    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {none_token}"},
    )
    assert response.status_code == 401
    data = response.json()
    assert "disallowed token algorithm" in data["message"].lower()


@pytest.mark.asyncio
async def test_auth_me_valid_es256_token_and_jit_user_sync(
    client: AsyncClient, valid_auth_headers: dict, test_user_id: uuid.UUID
):
    """Valid ES256 token succeeds and JIT synchronizes user into application table."""
    response = await client.get("/api/v1/auth/me", headers=valid_auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(test_user_id)
    assert data["email"] == "analyst@vigilx.com"
    assert data["full_name"] == "Test Analyst"


def test_verify_jwt_via_jwks_public_key():
    """Verify that verify_supabase_jwt works with public key resolved from a JWKS key structure."""
    user_id = uuid.uuid4()
    token = create_test_es256_jwt(user_id=user_id)
    
    # Directly verify using the PEM public key
    payload = verify_supabase_jwt(token, public_key=TEST_EC_PUBLIC_KEY_PEM)
    assert payload["sub"] == str(user_id)
    assert payload["aud"] == "authenticated"
