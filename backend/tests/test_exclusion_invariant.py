"""Official-Asset Exclusion Invariant Tests.

Verifies the foundational invariants of vigilX brand protection:
1. Legitimate official assets are 100% excluded from detection/risk scoring.
2. Impostors and lookalikes (even with identical titles or developers) are never granted immunity.
3. Missing, malformed, or cross-platform identifiers never confer immunity.
"""

import uuid
import pytest

from app.models.official_asset import OfficialApp, OfficialSocialAccount
from app.services.exclusion import (
    is_candidate_excluded,
    normalize_canonical_url,
    normalize_handle,
)
from tests.fixtures.mock_candidates import (
    ALL_TEST_CANDIDATES,
    BOUNDARY_AND_MALFORMED_CANDIDATES,
    IMPOSTOR_CANDIDATES,
    LEGITIMATE_OFFICIAL_CANDIDATES,
    OFFICIAL_APP_ASSETS,
    OFFICIAL_SOCIAL_ASSETS,
    SYNTHETIC_BRAND_ID,
    CandidateThreat,
    MockOfficialApp,
    MockOfficialSocialAccount,
)


# =========================================================================
# Unit Tests: Normalization Helpers
# =========================================================================


class TestNormalizationHelpers:
    """Tests handle and canonical URL normalization contracts."""

    @pytest.mark.parametrize(
        "input_handle,expected",
        [
            ("@nike", "nike"),
            ("nike", "nike"),
            ("  @NIKE  ", "nike"),
            ("@Nike_Official", "nike_official"),
            ("Nike.Support", "nike.support"),
            (None, None),
            ("", None),
            ("   ", None),
            ("@@@", None),
        ],
    )
    def test_normalize_handle(self, input_handle, expected):
        assert normalize_handle(input_handle) == expected

    @pytest.mark.parametrize(
        "input_url,expected",
        [
            ("https://x.com/nike", "https://x.com/nike"),
            ("https://x.com/nike/", "https://x.com/nike"),
            ("http://x.com/nike", "https://x.com/nike"),
            ("HTTP://X.COM/NIKE", "https://x.com/nike"),
            ("https://x.com/nike?utm_source=twitter&ref=feed", "https://x.com/nike"),
            ("https://x.com/nike#profile_section", "https://x.com/nike"),
            ("  https://instagram.com/nike/  ", "https://instagram.com/nike"),
            (None, None),
            ("", None),
            ("   ", None),
            ("not_a_valid_url", None),
        ],
    )
    def test_normalize_canonical_url(self, input_url, expected):
        assert normalize_canonical_url(input_url) == expected


# =========================================================================
# Invariant Test Suite: Social Exclusion
# =========================================================================


class TestSocialExclusionInvariant:
    """Verifies strict invariants for social media candidates."""

    def test_exact_handle_and_platform_match_is_excluded(self):
        candidate = CandidateThreat(
            source_type="social",
            platform="x",
            title="Apex Global Security",
            handle_or_package="apex_official",
            url="https://x.com/apex_official",
        )
        assert is_candidate_excluded(candidate, OFFICIAL_SOCIAL_ASSETS, OFFICIAL_APP_ASSETS) is True

    def test_platform_case_insensitivity(self):
        candidate = CandidateThreat(
            source_type="social",
            platform="X",
            title="Apex Global Security",
            handle_or_package="apex_official",
        )
        assert is_candidate_excluded(candidate, OFFICIAL_SOCIAL_ASSETS, OFFICIAL_APP_ASSETS) is True

    def test_handle_normalization_leading_at_and_whitespace(self):
        candidate = CandidateThreat(
            source_type="social",
            platform="x",
            title="Apex Global Security",
            handle_or_package="  @APEX_OFFICIAL  ",
        )
        assert is_candidate_excluded(candidate, OFFICIAL_SOCIAL_ASSETS, OFFICIAL_APP_ASSETS) is True

    def test_canonical_url_match_excludes_even_if_handle_is_missing(self):
        candidate = CandidateThreat(
            source_type="social",
            platform="x",
            title="Apex Announcements",
            handle_or_package=None,
            url="HTTP://X.COM/apex_official/?utm_source=test",
        )
        assert is_candidate_excluded(candidate, OFFICIAL_SOCIAL_ASSETS, OFFICIAL_APP_ASSETS) is True

    def test_cross_platform_isolation_same_handle_different_platform_not_excluded(self):
        # apex_official is registered on X and Instagram, but NOT on TikTok
        candidate = CandidateThreat(
            source_type="social",
            platform="tiktok",
            title="Apex Global Security",
            handle_or_package="apex_official",
            url="https://tiktok.com/@apex_official",
        )
        assert is_candidate_excluded(candidate, OFFICIAL_SOCIAL_ASSETS, OFFICIAL_APP_ASSETS) is False

    def test_identical_title_with_different_handle_is_never_excluded(self):
        # Impostor using official brand name
        candidate = CandidateThreat(
            source_type="social",
            platform="x",
            title="Apex Global Security",
            handle_or_package="apex_support_help",
            url="https://x.com/apex_support_help",
        )
        assert is_candidate_excluded(candidate, OFFICIAL_SOCIAL_ASSETS, OFFICIAL_APP_ASSETS) is False

    def test_lookalike_handle_homoglyph_not_excluded(self):
        candidate = CandidateThreat(
            source_type="social",
            platform="x",
            title="Apex Global Security",
            handle_or_package="apex_officia1",  # '1' instead of 'l'
        )
        assert is_candidate_excluded(candidate, OFFICIAL_SOCIAL_ASSETS, OFFICIAL_APP_ASSETS) is False

    def test_missing_and_empty_identifiers_never_excluded(self):
        candidate_none = CandidateThreat(
            source_type="social",
            platform="x",
            title="Apex Inc",
            handle_or_package=None,
            url=None,
        )
        candidate_empty = CandidateThreat(
            source_type="social",
            platform="x",
            title="Apex Inc",
            handle_or_package="",
            url="",
        )
        assert is_candidate_excluded(candidate_none, OFFICIAL_SOCIAL_ASSETS, OFFICIAL_APP_ASSETS) is False
        assert is_candidate_excluded(candidate_empty, OFFICIAL_SOCIAL_ASSETS, OFFICIAL_APP_ASSETS) is False


# =========================================================================
# Invariant Test Suite: App Store Exclusion
# =========================================================================


class TestAppStoreExclusionInvariant:
    """Verifies strict invariants for mobile app store candidates."""

    def test_exact_package_and_store_match_is_excluded(self):
        candidate = CandidateThreat(
            source_type="app_store",
            platform="google_play",
            title="Apex Authenticator",
            handle_or_package="com.apex.security.auth",
            developer_or_owner="Apex Global Security Inc.",
        )
        assert is_candidate_excluded(candidate, OFFICIAL_SOCIAL_ASSETS, OFFICIAL_APP_ASSETS) is True

    def test_store_case_insensitivity(self):
        candidate = CandidateThreat(
            source_type="app_store",
            platform="GOOGLE_PLAY",
            title="Apex Authenticator",
            handle_or_package="com.apex.security.auth",
        )
        assert is_candidate_excluded(candidate, OFFICIAL_SOCIAL_ASSETS, OFFICIAL_APP_ASSETS) is True

    def test_same_package_id_different_store_not_excluded(self):
        # com.apex.security.auth is on google_play, but candidate is on app_store (iOS package is auth.ios)
        candidate = CandidateThreat(
            source_type="app_store",
            platform="app_store",
            title="Apex Authenticator",
            handle_or_package="com.apex.security.auth",
        )
        assert is_candidate_excluded(candidate, OFFICIAL_SOCIAL_ASSETS, OFFICIAL_APP_ASSETS) is False

    def test_same_app_name_different_package_not_excluded(self):
        candidate = CandidateThreat(
            source_type="app_store",
            platform="google_play",
            title="Apex Authenticator",
            handle_or_package="com.scam.apex.auth",
            developer_or_owner="Apex Global Security Inc.",
        )
        assert is_candidate_excluded(candidate, OFFICIAL_SOCIAL_ASSETS, OFFICIAL_APP_ASSETS) is False

    def test_same_developer_different_package_not_excluded(self):
        candidate = CandidateThreat(
            source_type="app_store",
            platform="google_play",
            title="Apex Security Scanner",
            handle_or_package="com.apex.unknown.scanner",
            developer_or_owner="Apex Global Security Inc.",
        )
        assert is_candidate_excluded(candidate, OFFICIAL_SOCIAL_ASSETS, OFFICIAL_APP_ASSETS) is False

    def test_missing_or_empty_package_id_never_excluded(self):
        candidate_none = CandidateThreat(
            source_type="app_store",
            platform="google_play",
            title="Apex Authenticator",
            handle_or_package=None,
            developer_or_owner="Apex Global Security Inc.",
        )
        candidate_empty = CandidateThreat(
            source_type="app_store",
            platform="google_play",
            title="Apex Authenticator",
            handle_or_package="",
            developer_or_owner="Apex Global Security Inc.",
        )
        assert is_candidate_excluded(candidate_none, OFFICIAL_SOCIAL_ASSETS, OFFICIAL_APP_ASSETS) is False
        assert is_candidate_excluded(candidate_empty, OFFICIAL_SOCIAL_ASSETS, OFFICIAL_APP_ASSETS) is False

    def test_package_id_case_difference_not_silently_lowercased(self):
        # Package IDs are exact-match; COM.APEX.SECURITY.AUTH != com.apex.security.auth
        candidate = CandidateThreat(
            source_type="app_store",
            platform="google_play",
            title="Apex Authenticator",
            handle_or_package="COM.APEX.SECURITY.AUTH",
            developer_or_owner="Apex Global Security Inc.",
        )
        assert is_candidate_excluded(candidate, OFFICIAL_SOCIAL_ASSETS, OFFICIAL_APP_ASSETS) is False


# =========================================================================
# Invariant Test Suite: Full Fixture Datasets (100% Invariance)
# =========================================================================


class TestDatasetInvariants:
    """Verifies invariants across the comprehensive 30-candidate fixture dataset."""

    @pytest.mark.parametrize("candidate", LEGITIMATE_OFFICIAL_CANDIDATES)
    def test_100_percent_legitimate_official_candidates_excluded(self, candidate: CandidateThreat):
        """Every single legitimate candidate MUST evaluate to True."""
        result = is_candidate_excluded(candidate, OFFICIAL_SOCIAL_ASSETS, OFFICIAL_APP_ASSETS)
        assert result is True, f"Official candidate was wrongly flagged as candidate threat: {candidate}"

    @pytest.mark.parametrize("candidate", IMPOSTOR_CANDIDATES)
    def test_0_percent_impostors_falsely_excluded(self, candidate: CandidateThreat):
        """No impostor or lookalike may ever be granted exclusion immunity."""
        result = is_candidate_excluded(candidate, OFFICIAL_SOCIAL_ASSETS, OFFICIAL_APP_ASSETS)
        assert result is False, f"Impostor was falsely excluded from detection: {candidate}"

    @pytest.mark.parametrize("candidate", BOUNDARY_AND_MALFORMED_CANDIDATES)
    def test_0_percent_boundary_and_malformed_falsely_excluded(self, candidate: CandidateThreat):
        """Missing identifiers or malformed platforms must never grant exclusion immunity."""
        result = is_candidate_excluded(candidate, OFFICIAL_SOCIAL_ASSETS, OFFICIAL_APP_ASSETS)
        assert result is False, f"Malformed candidate was falsely excluded: {candidate}"

    def test_all_candidates_dataset_count_exceeds_brief_requirement(self):
        """Implementation brief 04 requires at least 25 diverse candidate fixtures."""
        assert len(ALL_TEST_CANDIDATES) >= 25
        assert len(ALL_TEST_CANDIDATES) == 30


# =========================================================================
# Integration Test Suite: Real SQLAlchemy Models Compatibility
# =========================================================================


class TestSQLAlchemyModelCompatibility:
    """Verifies that is_candidate_excluded works seamlessly with real SQLAlchemy ORM models."""

    def test_orm_official_assets_exclusion(self):
        brand_id = uuid.uuid4()
        orm_social = OfficialSocialAccount(
            id=uuid.uuid4(),
            brand_id=brand_id,
            platform="x",
            handle="acme_official",
            raw_handle="@Acme_Official",
            url="https://x.com/acme_official",
            is_verified=True,
        )
        orm_app = OfficialApp(
            id=uuid.uuid4(),
            brand_id=brand_id,
            name="Acme Vault",
            package_id="com.acme.vault",
            developer_name="Acme Corporation",
            store="google_play",
            store_url="https://play.google.com/store/apps/details?id=com.acme.vault",
        )

        official_socials = [orm_social]
        official_apps = [orm_app]

        # Official social candidate -> True
        cand_social_official = CandidateThreat(
            source_type="social",
            platform="X",
            title="Acme Official",
            handle_or_package="@acme_official",
        )
        assert is_candidate_excluded(cand_social_official, official_socials, official_apps) is True

        # Official app candidate -> True
        cand_app_official = CandidateThreat(
            source_type="app_store",
            platform="google_play",
            title="Acme Vault",
            handle_or_package="com.acme.vault",
        )
        assert is_candidate_excluded(cand_app_official, official_socials, official_apps) is True

        # Malicious social candidate -> False
        cand_social_fake = CandidateThreat(
            source_type="social",
            platform="x",
            title="Acme Corporation",
            handle_or_package="acme_giveaways",
        )
        assert is_candidate_excluded(cand_social_fake, official_socials, official_apps) is False

        # Malicious app candidate -> False
        cand_app_fake = CandidateThreat(
            source_type="app_store",
            platform="google_play",
            title="Acme Vault",
            handle_or_package="com.fake.acme.vault",
            developer_or_owner="Acme Corporation",
        )
        assert is_candidate_excluded(cand_app_fake, official_socials, official_apps) is False
