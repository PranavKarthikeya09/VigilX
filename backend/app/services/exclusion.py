"""Official-Asset Exclusion Invariant Service for vigilX.

Enforces strict exclusion invariants to ensure verified official assets
are 100% excluded from being flagged as threats, while ensuring lookalikes,
impostors, and unverified assets are never granted false immunity.
"""

from typing import Any, Optional, Sequence
import urllib.parse


def normalize_handle(handle: Optional[str]) -> Optional[str]:
    """Normalize a social media handle.

    Strips leading '@', trims surrounding whitespace, and lowercases.
    Returns None if handle is None, empty, or whitespace-only.
    """
    if handle is None:
        return None
    cleaned = handle.strip()
    if not cleaned:
        return None
    return cleaned.lstrip("@").strip().lower() or None


def normalize_canonical_url(url: Optional[str]) -> Optional[str]:
    """Normalize a URL to its canonical form for equivalence comparison.

    - Strips whitespace.
    - Converts scheme to https.
    - Lowercases hostname.
    - Strips tracking parameters, query strings, and fragments.
    - Strips trailing slash from path.
    Returns None if url is None or invalid.
    """
    if url is None:
        return None
    cleaned = url.strip()
    if not cleaned:
        return None

    try:
        parsed = urllib.parse.urlparse(cleaned)
        # Require at least netloc or path to be a valid URL
        if not parsed.netloc and not parsed.path:
            return None

        # Standardize host and path
        host = parsed.netloc.lower()
        path = parsed.path.rstrip("/").lower()
        if not host:
            return None

        return f"https://{host}{path}"
    except Exception:
        return None


def is_candidate_excluded(
    candidate: Any,
    official_socials: Sequence[Any],
    official_apps: Sequence[Any],
) -> bool:
    """Evaluate whether a candidate threat strictly matches a registered official asset.

    Returns True if the candidate MUST be excluded from detection/flagging.
    Returns False if the candidate remains eligible for risk scoring and evaluation.

    Strict Invariant Rules:
    1. SOCIAL CANDIDATE:
       Excluded IF AND ONLY IF:
         - Platform matches registered official account platform (case-insensitive); AND
         - (Normalized handle matches OR Canonical URL matches).
       NEVER excluded by display name/title alone.
       Missing/empty identifiers NEVER confer exclusion.

    2. APP CANDIDATE:
       Excluded IF AND ONLY IF:
         - Store matches registered official app store (case-insensitive); AND
         - Both package IDs are non-null and non-empty; AND
         - Package IDs match EXACTLY (exact match, case-sensitive per app store specification).
       NEVER excluded by app title or developer name alone.
       Missing/empty package ID NEVER confers exclusion.
    """
    if candidate is None:
        return False

    # Extract candidate attributes (supports CandidateThreat dataclass, object, or dict)
    source_type = getattr(candidate, "source_type", None) or (candidate.get("source_type") if isinstance(candidate, dict) else None)
    platform = getattr(candidate, "platform", None) or (candidate.get("platform") if isinstance(candidate, dict) else None)
    handle_or_pkg = getattr(candidate, "handle_or_package", None) or (candidate.get("handle_or_package") if isinstance(candidate, dict) else None)
    cand_url = getattr(candidate, "url", None) or (candidate.get("url") if isinstance(candidate, dict) else None)

    if not platform:
        return False

    cand_platform_lower = platform.strip().lower()

    # --- SOCIAL EVALUATION ---
    if source_type == "social":
        cand_norm_handle = normalize_handle(handle_or_pkg)
        cand_norm_url = normalize_canonical_url(cand_url)

        # If candidate has neither valid handle nor valid URL, never exclude
        if cand_norm_handle is None and cand_norm_url is None:
            return False

        for official in official_socials:
            off_platform = getattr(official, "platform", None) or (official.get("platform") if isinstance(official, dict) else None)
            if not off_platform or off_platform.strip().lower() != cand_platform_lower:
                continue

            # Compare normalized handles
            off_raw_handle = getattr(official, "handle", None) or (official.get("handle") if isinstance(official, dict) else None)
            off_norm_handle = normalize_handle(off_raw_handle)
            if cand_norm_handle is not None and off_norm_handle is not None:
                if cand_norm_handle == off_norm_handle:
                    return True

            # Compare canonical URLs
            off_raw_url = getattr(official, "url", None) or (official.get("url") if isinstance(official, dict) else None)
            off_norm_url = normalize_canonical_url(off_raw_url)
            if cand_norm_url is not None and off_norm_url is not None:
                if cand_norm_url == off_norm_url:
                    return True

        return False

    # --- APP STORE EVALUATION ---
    elif source_type == "app_store":
        # Candidate package ID must be non-null and non-empty
        if handle_or_pkg is None:
            return False
        cand_pkg = handle_or_pkg.strip()
        if not cand_pkg:
            return False

        for official in official_apps:
            off_store = getattr(official, "store", None) or (official.get("store") if isinstance(official, dict) else None)
            if not off_store or off_store.strip().lower() != cand_platform_lower:
                continue

            off_pkg = getattr(official, "package_id", None) or (official.get("package_id") if isinstance(official, dict) else None)
            if off_pkg is None:
                continue
            off_pkg_clean = off_pkg.strip()
            if not off_pkg_clean:
                continue

            # Exact match, case-sensitive
            if cand_pkg == off_pkg_clean:
                return True

        return False

    return False
