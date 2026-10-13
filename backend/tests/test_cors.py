import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_cors_preflight_post_brands_port_5174(client: AsyncClient):
    """Browser preflight OPTIONS request for POST /api/v1/brands from port 5174."""
    response = await client.options(
        "/api/v1/brands",
        headers={
            "Origin": "http://localhost:5174",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "authorization,content-type",
        },
    )
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "http://localhost:5174"
    assert response.headers.get("access-control-allow-credentials") == "true"
    assert "POST" in response.headers.get("access-control-allow-methods", "")
    assert "authorization" in response.headers.get("access-control-allow-headers", "").lower()


@pytest.mark.asyncio
async def test_cors_preflight_post_brands_port_5173(client: AsyncClient):
    """Browser preflight OPTIONS request for POST /api/v1/brands from port 5173."""
    response = await client.options(
        "/api/v1/brands",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "authorization,content-type",
        },
    )
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "http://localhost:5173"
    assert response.headers.get("access-control-allow-credentials") == "true"


@pytest.mark.asyncio
async def test_cors_post_brand_success_headers(client: AsyncClient, valid_auth_headers: dict):
    """Successful POST /api/v1/brands from http://localhost:5174 receives CORS headers."""
    response = await client.post(
        "/api/v1/brands",
        json={"name": "CorsTestBrand", "website": "https://corstest.com"},
        headers={
            "Origin": "http://localhost:5174",
            **valid_auth_headers,
        },
    )
    assert response.status_code == 201
    assert response.headers.get("access-control-allow-origin") == "http://localhost:5174"
    assert response.headers.get("access-control-allow-credentials") == "true"
    assert "x-request-id" in response.headers


@pytest.mark.asyncio
async def test_cors_post_brand_from_5173(client: AsyncClient, valid_auth_headers: dict):
    """Successful POST /api/v1/brands from http://localhost:5173 receives CORS headers."""
    response = await client.post(
        "/api/v1/brands",
        json={"name": "CorsTestBrand5173", "website": "https://corstest5173.com"},
        headers={
            "Origin": "http://localhost:5173",
            **valid_auth_headers,
        },
    )
    assert response.status_code == 201
    assert response.headers.get("access-control-allow-origin") == "http://localhost:5173"
    assert response.headers.get("access-control-allow-credentials") == "true"


@pytest.mark.asyncio
async def test_cors_post_brand_unauthorized_preserves_cors(client: AsyncClient):
    """HTTP 401 error on POST /api/v1/brands preserves CORS headers."""
    response = await client.post(
        "/api/v1/brands",
        json={"name": "UnauthorizedBrand"},
        headers={"Origin": "http://localhost:5174"},
    )
    assert response.status_code == 401
    assert response.headers.get("access-control-allow-origin") == "http://localhost:5174"
    assert response.headers.get("access-control-allow-credentials") == "true"
    assert "Bearer" in response.headers.get("www-authenticate", "")


@pytest.mark.asyncio
async def test_cors_post_brand_validation_error_preserves_cors(
    client: AsyncClient, valid_auth_headers: dict
):
    """HTTP 422 validation error on POST /api/v1/brands preserves CORS headers."""
    response = await client.post(
        "/api/v1/brands",
        json={"name": "A"},  # Invalid: min_length is 2
        headers={
            "Origin": "http://localhost:5174",
            **valid_auth_headers,
        },
    )
    assert response.status_code == 422
    assert response.headers.get("access-control-allow-origin") == "http://localhost:5174"
    assert response.headers.get("access-control-allow-credentials") == "true"


@pytest.mark.asyncio
async def test_cors_disallowed_origin_rejected(client: AsyncClient):
    """Disallowed origin does not receive Access-Control-Allow-Origin header."""
    response = await client.post(
        "/api/v1/brands",
        json={"name": "EvilBrand"},
        headers={"Origin": "https://malicious-site.example.com"},
    )
    assert response.headers.get("access-control-allow-origin") is None
