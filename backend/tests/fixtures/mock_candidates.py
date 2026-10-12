"""Deterministic candidate threat fixtures and official asset datasets.

Designed for testing the Official-Asset Exclusion Invariant in vigilX.
Contains zero real user PII; all brands, handles, and URLs are synthetic.
"""

from dataclasses import dataclass
from typing import Any, List, Optional
import uuid

from app.services.exclusion import (
    is_candidate_excluded,
    normalize_canonical_url,
    normalize_handle,
)


@dataclass(frozen=True)
class CandidateThreat:
    """Represents an unverified candidate item scraped or ingested for evaluation."""

    source_type: str  # "social" | "app_store"
    platform: str  # "x", "instagram", "youtube", "google_play", "app_store", etc.
    title: str  # Display name or app title
    handle_or_package: Optional[str] = None  # Normalized social handle or app package ID
    developer_or_owner: Optional[str] = None  # App developer name or account owner
    url: Optional[str] = None  # Profile or store listing URL
    description: Optional[str] = None  # Bio text or app description
    logo_url: Optional[str] = None  # URL to candidate logo
    metadata_notes: Optional[str] = None  # Rationale or test expectation notes


@dataclass(frozen=True)
class MockOfficialSocialAccount:
    """Lightweight representation of an official social media account."""

    id: uuid.UUID
    brand_id: uuid.UUID
    platform: str
    handle: str
    raw_handle: str
    url: Optional[str] = None
    is_verified: bool = True


@dataclass(frozen=True)
class MockOfficialApp:
    """Lightweight representation of an official mobile application."""

    id: uuid.UUID
    brand_id: uuid.UUID
    name: str
    package_id: str
    developer_name: str
    store: str
    store_url: Optional[str] = None
    logo_url: Optional[str] = None


# -------------------------------------------------------------------------
# Synthetic Brand: "Apex Global Security"
# -------------------------------------------------------------------------
SYNTHETIC_BRAND_ID = uuid.UUID("a1111111-2222-3333-4444-555555555555")

OFFICIAL_SOCIAL_ASSETS: List[MockOfficialSocialAccount] = [
    MockOfficialSocialAccount(
        id=uuid.UUID("b1111111-0000-0000-0000-000000000001"),
        brand_id=SYNTHETIC_BRAND_ID,
        platform="x",
        handle="apex_official",
        raw_handle="@Apex_Official",
        url="https://x.com/apex_official",
    ),
    MockOfficialSocialAccount(
        id=uuid.UUID("b1111111-0000-0000-0000-000000000002"),
        brand_id=SYNTHETIC_BRAND_ID,
        platform="instagram",
        handle="apex_official",
        raw_handle="@Apex_Official",
        url="https://instagram.com/apex_official",
    ),
    MockOfficialSocialAccount(
        id=uuid.UUID("b1111111-0000-0000-0000-000000000003"),
        brand_id=SYNTHETIC_BRAND_ID,
        platform="youtube",
        handle="apexbrand",
        raw_handle="ApexBrand",
        url="https://youtube.com/@apexbrand",
    ),
]

OFFICIAL_APP_ASSETS: List[MockOfficialApp] = [
    MockOfficialApp(
        id=uuid.UUID("c1111111-0000-0000-0000-000000000001"),
        brand_id=SYNTHETIC_BRAND_ID,
        name="Apex Authenticator",
        package_id="com.apex.security.auth",
        developer_name="Apex Global Security Inc.",
        store="google_play",
        store_url="https://play.google.com/store/apps/details?id=com.apex.security.auth",
    ),
    MockOfficialApp(
        id=uuid.UUID("c1111111-0000-0000-0000-000000000002"),
        brand_id=SYNTHETIC_BRAND_ID,
        name="Apex Authenticator iOS",
        package_id="com.apex.security.auth.ios",
        developer_name="Apex Global Security Inc.",
        store="app_store",
        store_url="https://apps.apple.com/app/apex-authenticator/id123456789",
    ),
]


# -------------------------------------------------------------------------
# Candidate Dataset 1: Legitimate Official Candidates (MUST BE EXCLUDED: True)
# -------------------------------------------------------------------------
LEGITIMATE_OFFICIAL_CANDIDATES: List[CandidateThreat] = [
    CandidateThreat(
        source_type="social",
        platform="x",
        title="Apex Global Security",
        handle_or_package="apex_official",
        url="https://x.com/apex_official",
        metadata_notes="Exact handle and exact URL match on X",
    ),
    CandidateThreat(
        source_type="social",
        platform="X",  # uppercase platform
        title="Apex Global",
        handle_or_package="@apex_official",  # leading @
        url="https://x.com/apex_official",
        metadata_notes="Platform case-insensitive and handle with leading @",
    ),
    CandidateThreat(
        source_type="social",
        platform="x",
        title="Apex Support",
        handle_or_package="  APEX_OFFICIAL  ",  # uppercase with whitespace
        url="https://x.com/apex_official",
        metadata_notes="Handle with uppercase and surrounding whitespace",
    ),
    CandidateThreat(
        source_type="social",
        platform="x",
        title="Apex Official Feed",
        handle_or_package=None,  # missing handle, matching canonical URL
        url="https://x.com/apex_official/",  # trailing slash
        metadata_notes="Missing handle but matching canonical URL with trailing slash",
    ),
    CandidateThreat(
        source_type="social",
        platform="x",
        title="Apex Announcement",
        handle_or_package=None,
        url="HTTP://X.COM/apex_official?utm_source=twitter&ref=share",  # http, uppercase host, query params
        metadata_notes="Canonical URL match with HTTP scheme and tracking query parameters",
    ),
    CandidateThreat(
        source_type="social",
        platform="instagram",
        title="Apex Security Official",
        handle_or_package="apex_official",
        url="https://instagram.com/apex_official",
        metadata_notes="Exact match on official Instagram",
    ),
    CandidateThreat(
        source_type="social",
        platform="youtube",
        title="Apex Brand Channel",
        handle_or_package="apexbrand",
        url="https://youtube.com/@apexbrand",
        metadata_notes="Exact match on official YouTube channel",
    ),
    CandidateThreat(
        source_type="app_store",
        platform="google_play",
        title="Apex Authenticator",
        handle_or_package="com.apex.security.auth",
        developer_or_owner="Apex Global Security Inc.",
        url="https://play.google.com/store/apps/details?id=com.apex.security.auth",
        metadata_notes="Exact package ID match on Google Play",
    ),
    CandidateThreat(
        source_type="app_store",
        platform="GOOGLE_PLAY",  # uppercase store
        title="Apex 2FA Security",
        handle_or_package="com.apex.security.auth",
        developer_or_owner="Some Other Publisher",  # dev mismatch doesn't prevent valid pkg exclusion
        url=None,
        metadata_notes="Store case-insensitive and exact package ID match",
    ),
    CandidateThreat(
        source_type="app_store",
        platform="app_store",
        title="Apex Authenticator iOS",
        handle_or_package="com.apex.security.auth.ios",
        developer_or_owner="Apex Global Security Inc.",
        url="https://apps.apple.com/app/apex/id123456789",
        metadata_notes="Exact package ID match on iOS App Store",
    ),
]


# -------------------------------------------------------------------------
# Candidate Dataset 2: Malicious / Impostor Candidates (MUST NOT BE EXCLUDED: False)
# -------------------------------------------------------------------------
IMPOSTOR_CANDIDATES: List[CandidateThreat] = [
    CandidateThreat(
        source_type="social",
        platform="x",
        title="Apex Global Security",  # identical brand name!
        handle_or_package="apex_support_help",
        url="https://x.com/apex_support_help",
        metadata_notes="Identical brand title but fraudulent handle; must not be excluded",
    ),
    CandidateThreat(
        source_type="social",
        platform="x",
        title="Apex Security Official",
        handle_or_package="apex_officia1",  # homoglyph '1' for 'l'
        url="https://x.com/apex_officia1",
        metadata_notes="Typo-squatting homoglyph handle; must not be excluded",
    ),
    CandidateThreat(
        source_type="social",
        platform="x",
        title="Apex VIP Club",
        handle_or_package="apex_official_vip",
        url="https://x.com/apex_official_vip",
        metadata_notes="Lookalike affix variation handle; must not be excluded",
    ),
    CandidateThreat(
        source_type="social",
        platform="tiktok",  # platform not registered in official assets!
        title="Apex Global Security",
        handle_or_package="apex_official",  # same handle on unregistered platform
        url="https://tiktok.com/@apex_official",
        metadata_notes="Cross-platform isolation: official on X/IG does not exclude TikTok",
    ),
    CandidateThreat(
        source_type="social",
        platform="threads",
        title="Apex Official",
        handle_or_package="apex_official",
        url="https://threads.net/@apex_official",
        metadata_notes="Cross-platform isolation on Threads",
    ),
    CandidateThreat(
        source_type="app_store",
        platform="google_play",
        title="Apex Authenticator",  # exact official title!
        handle_or_package="com.apex.security.scam",  # malicious package
        developer_or_owner="Apex Global Security Inc.",  # spoofed developer name!
        url="https://play.google.com/store/apps/details?id=com.apex.security.scam",
        metadata_notes="Spoofed app title and developer name with rogue package ID",
    ),
    CandidateThreat(
        source_type="app_store",
        platform="google_play",
        title="Apex Pro Authenticator",
        handle_or_package="com.apex.auth.fake",
        developer_or_owner="Apex Global Security Inc.",
        url=None,
        metadata_notes="Spoofed developer name with rogue package ID",
    ),
    CandidateThreat(
        source_type="app_store",
        platform="app_store",  # wrong store for google_play package
        title="Apex Authenticator",
        handle_or_package="com.apex.security.auth",  # this is the Google Play package ID, not iOS!
        developer_or_owner="Apex Global Security Inc.",
        url=None,
        metadata_notes="Store mismatch: Google Play package ID on Apple App Store",
    ),
    CandidateThreat(
        source_type="social",
        platform="instagram",
        title="Apex Official",
        handle_or_package="apex_official_support",
        url="https://instagram.com/apex_official_support",
        metadata_notes="Instagram impostor support account",
    ),
    CandidateThreat(
        source_type="social",
        platform="youtube",
        title="Apex Brand Live",
        handle_or_package="apexbrand_crypto",
        url="https://youtube.com/@apexbrand_crypto",
        metadata_notes="YouTube crypto scam channel copying brand name",
    ),
]


# -------------------------------------------------------------------------
# Candidate Dataset 3: Boundary & Malformed Candidates (MUST NOT BE EXCLUDED: False)
# -------------------------------------------------------------------------
BOUNDARY_AND_MALFORMED_CANDIDATES: List[CandidateThreat] = [
    CandidateThreat(
        source_type="social",
        platform="x",
        title="Apex Anonymous",
        handle_or_package=None,
        url=None,
        metadata_notes="Social candidate with both handle and URL as None",
    ),
    CandidateThreat(
        source_type="social",
        platform="x",
        title="Apex Empty",
        handle_or_package="",
        url="",
        metadata_notes="Social candidate with empty strings for identifiers",
    ),
    CandidateThreat(
        source_type="social",
        platform="x",
        title="Apex Whitespace",
        handle_or_package="   ",
        url="   ",
        metadata_notes="Social candidate with whitespace-only identifiers",
    ),
    CandidateThreat(
        source_type="social",
        platform="x",
        title="Apex Malformed URL",
        handle_or_package=None,
        url="not_a_valid_url",
        metadata_notes="Social candidate with unparseable URL",
    ),
    CandidateThreat(
        source_type="app_store",
        platform="google_play",
        title="Apex Missing Package",
        handle_or_package=None,
        developer_or_owner="Apex Global Security Inc.",
        metadata_notes="App candidate with None package ID must never be immune",
    ),
    CandidateThreat(
        source_type="app_store",
        platform="google_play",
        title="Apex Empty Package",
        handle_or_package="",
        developer_or_owner="Apex Global Security Inc.",
        metadata_notes="App candidate with empty string package ID",
    ),
    CandidateThreat(
        source_type="app_store",
        platform="google_play",
        title="Apex Whitespace Package",
        handle_or_package="   ",
        developer_or_owner="Apex Global Security Inc.",
        metadata_notes="App candidate with whitespace-only package ID",
    ),
    CandidateThreat(
        source_type="app_store",
        platform="google_play",
        title="Apex Upper Case Package",
        handle_or_package="COM.APEX.SECURITY.AUTH",  # uppercase package ID
        developer_or_owner="Apex Global Security Inc.",
        metadata_notes="Package ID case mismatch: exact match rule prohibits silent lowercasing",
    ),
    CandidateThreat(
        source_type="unknown_type",
        platform="unknown_platform",
        title="Unknown Threat",
        handle_or_package="apex_official",
        metadata_notes="Unknown source_type must not trigger exclusion",
    ),
    CandidateThreat(
        source_type="social",
        platform="",
        title="Missing Platform",
        handle_or_package="apex_official",
        metadata_notes="Empty platform string must never match",
    ),
]


# Combined full test candidate fixture list (30 deterministic candidates)
ALL_TEST_CANDIDATES: List[CandidateThreat] = (
    LEGITIMATE_OFFICIAL_CANDIDATES
    + IMPOSTOR_CANDIDATES
    + BOUNDARY_AND_MALFORMED_CANDIDATES
)
