import uuid
from typing import Any
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings
from app.db.base import Base
from app.db.session import get_db
from app.main import create_app
from tests.test_helpers import (
    TEST_EC_PUBLIC_KEY_PEM,
    create_test_es256_jwt,
)

# Isolated in-memory SQLite database for test suite
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def test_engine():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def test_session(test_engine):
    session_factory = async_sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    async with session_factory() as session:
        yield session


@pytest_asyncio.fixture
async def client(test_session):
    app = create_app()

    async def override_get_db():
        yield test_session

    app.dependency_overrides[get_db] = override_get_db

    # Point public key to our test EC public key
    original_public_key = settings.SUPABASE_JWT_PUBLIC_KEY
    settings.SUPABASE_JWT_PUBLIC_KEY = TEST_EC_PUBLIC_KEY_PEM

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as ac:
        yield ac

    settings.SUPABASE_JWT_PUBLIC_KEY = original_public_key
    app.dependency_overrides.clear()


@pytest.fixture
def test_user_id() -> uuid.UUID:
    return uuid.UUID("11111111-2222-3333-4444-555555555555")


@pytest.fixture
def valid_auth_headers(test_user_id) -> dict:
    token = create_test_es256_jwt(
        user_id=test_user_id,
        email="analyst@vigilx.com",
    )
    return {"Authorization": f"Bearer {token}"}


# -------------------------------------------------------------------------
# Shared QA Candidate & Official Asset Fixtures
# -------------------------------------------------------------------------
from tests.fixtures.mock_candidates import (
    CandidateThreat,
    MockOfficialSocialAccount,
    MockOfficialApp,
    SYNTHETIC_BRAND_ID,
    OFFICIAL_SOCIAL_ASSETS,
    OFFICIAL_APP_ASSETS,
    LEGITIMATE_OFFICIAL_CANDIDATES,
    IMPOSTOR_CANDIDATES,
    BOUNDARY_AND_MALFORMED_CANDIDATES,
    ALL_TEST_CANDIDATES,
)


@pytest.fixture
def mock_official_socials() -> list[MockOfficialSocialAccount]:
    return OFFICIAL_SOCIAL_ASSETS


@pytest.fixture
def mock_official_apps() -> list[MockOfficialApp]:
    return OFFICIAL_APP_ASSETS


@pytest.fixture
def legitimate_candidates() -> list[CandidateThreat]:
    return LEGITIMATE_OFFICIAL_CANDIDATES


@pytest.fixture
def impostor_candidates() -> list[CandidateThreat]:
    return IMPOSTOR_CANDIDATES


@pytest.fixture
def all_mock_candidates() -> list[CandidateThreat]:
    return ALL_TEST_CANDIDATES

