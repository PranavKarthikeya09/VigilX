import uuid
import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.brand import Brand
from app.models.official_asset import OfficialSocialAccount, OfficialApp
from app.models.detection import Detection, DetectionEvidence


@pytest.mark.asyncio
async def test_create_brand_and_assets(test_session: AsyncSession):
    """Verify that Brand and related assets can be persisted and queried."""
    user = User(
        id=uuid.uuid4(),
        email="owner@vigilx.com",
        full_name="Brand Owner",
    )
    test_session.add(user)
    await test_session.flush()

    brand = Brand(
        id=uuid.uuid4(),
        owner_id=user.id,
        name="Nike",
        normalized_name="nike",
        website="https://nike.com",
    )
    test_session.add(brand)
    await test_session.flush()

    social = OfficialSocialAccount(
        brand_id=brand.id,
        platform="x",
        handle="Nike",
        raw_handle="@Nike",
        url="https://x.com/Nike",
        is_verified=True,
    )
    test_session.add(social)

    app = OfficialApp(
        brand_id=brand.id,
        name="Nike App",
        package_id="com.nike.omega",
        developer_name="Nike, Inc.",
        store="google_play",
    )
    test_session.add(app)
    await test_session.flush()

    # Query back
    result = await test_session.execute(select(Brand).where(Brand.id == brand.id))
    fetched_brand = result.scalar_one()
    assert fetched_brand.name == "Nike"
    assert fetched_brand.normalized_name == "nike"
    assert len(fetched_brand.social_accounts) == 1
    assert fetched_brand.social_accounts[0].handle == "Nike"
    assert len(fetched_brand.official_apps) == 1
    assert fetched_brand.official_apps[0].developer_name == "Nike, Inc."


@pytest.mark.asyncio
async def test_detection_and_evidence_persistence(test_session: AsyncSession):
    """Verify Detection with raw_signals JSON and linked DetectionEvidence."""
    user = User(id=uuid.uuid4(), email="analyst2@vigilx.com")
    test_session.add(user)
    await test_session.flush()

    brand = Brand(id=uuid.uuid4(), owner_id=user.id, name="Acme", normalized_name="acme")
    test_session.add(brand)
    await test_session.flush()

    detection = Detection(
        brand_id=brand.id,
        source_type="social",
        platform="x",
        title="Acme Official Support",
        handle_or_package="@AcmeHelpScam",
        risk_score=85.0,
        risk_level="high",
        status="needs_review",
        is_official_excluded=False,
        raw_signals={
            "name_similarity": 0.95,
            "logo_similarity": 0.80,
            "lookalike_signal": 0.90,
            "bio_similarity": 0.50,
        },
    )
    test_session.add(detection)
    await test_session.flush()

    evidence = DetectionEvidence(
        detection_id=detection.id,
        signal_type="lookalike",
        score=0.90,
        explanation="Detected homoglyph swap and suspicious keyword 'Support'",
    )
    test_session.add(evidence)
    await test_session.flush()

    # Query detection
    res = await test_session.execute(select(Detection).where(Detection.id == detection.id))
    fetched = res.scalar_one()
    assert fetched.risk_score == 85.0
    assert fetched.risk_level == "high"
    assert fetched.raw_signals["name_similarity"] == 0.95
    assert len(fetched.evidence_items) == 1
    assert fetched.evidence_items[0].signal_type == "lookalike"
