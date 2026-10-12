import uuid
import pytest
from httpx import AsyncClient
from app.core.security import create_test_jwt
from tests.conftest import TEST_JWT_SECRET


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
    """Token signed with the wrong key must be rejected with 401."""
    wrong_token = create_test_jwt(
        user_id=test_user_id,
        secret="completely-wrong-unauthorized-secret-key",
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
    """Expired token must be rejected with 401."""
    expired_token = create_test_jwt(
        user_id=test_user_id,
        secret=TEST_JWT_SECRET,
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
    """Token with anon audience or wrong audience must be rejected."""
    anon_token = create_test_jwt(
        user_id=test_user_id,
        secret=TEST_JWT_SECRET,
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
async def test_auth_me_valid_token_and_jit_user_sync(client: AsyncClient, valid_auth_headers: dict, test_user_id: uuid.UUID):
    """Valid token succeeds and JIT synchronizes user into application table."""
    response = await client.get("/api/v1/auth/me", headers=valid_auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(test_user_id)
    assert data["email"] == "analyst@vigilx.com"
    assert data["full_name"] == "Test Analyst"
