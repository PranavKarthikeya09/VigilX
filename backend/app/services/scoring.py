import math
from typing import Optional, Tuple, Dict, Any

# Platform-specific scoring weights (sum exactly to 1.0)
SOCIAL_WEIGHTS: Dict[str, float] = {
    "name_similarity": 0.40,
    "logo_similarity": 0.30,
    "bio_similarity": 0.15,
    "lookalike_signal": 0.15,
}

APP_WEIGHTS: Dict[str, float] = {
    "title_similarity": 0.30,
    "publisher_mismatch": 0.30,
    "logo_similarity": 0.20,
    "description_similarity": 0.10,
    "lookalike_signal": 0.10,
}


def _clean_signal(val: Optional[float], default: float = 0.0) -> float:
    """Defensively cleans, validates finiteness, and clamps signal float to [0.0, 1.0]."""
    if val is None:
        return default
    try:
        f = float(val)
        if not math.isfinite(f):
            return default
        return max(0.0, min(1.0, f))
    except (ValueError, TypeError):
        return default


def determine_risk_level(score: float) -> str:
    """
    Categorizes score into agreed risk tiers:
    - High: score >= 75.0
    - Medium: 50.0 <= score < 75.0
    - Low: score < 50.0
    """
    if score >= 75.0:
        return "high"
    elif score >= 50.0:
        return "medium"
    return "low"


def compute_publisher_mismatch(
    candidate_developer: Optional[str],
    official_developer: Optional[str],
    title_similarity: float,
) -> float:
    """
    Computes publisher/developer mismatch signal:
    - Missing candidate developer (None or empty/whitespace): returns 0.75.
    - Exact normalized developer match: returns 0.0.
    - If candidate developer differs:
        - If title_similarity > 0.60: returns 1.0.
        - If title_similarity <= 0.60: returns 0.0.
    """
    if not candidate_developer or not candidate_developer.strip():
        return 0.75

    c_norm = candidate_developer.strip().lower()
    o_norm = (
        official_developer.strip().lower()
        if official_developer and official_developer.strip()
        else ""
    )

    if o_norm and c_norm == o_norm:
        return 0.0

    # Developer differs
    clean_title_sim = _clean_signal(title_similarity, default=0.0)
    if clean_title_sim > 0.60:
        return 1.0
    return 0.0


def calculate_social_risk(
    name_similarity: Optional[float],
    logo_similarity: Optional[float],
    bio_similarity: Optional[float],
    lookalike_signal: Optional[float],
) -> Tuple[float, str]:
    """
    Calculates weighted social risk score:
      Score = (0.40 * name + 0.30 * logo + 0.15 * bio + 0.15 * lookalike) * 100.0
    Missing signals (None) default to 0.0.
    Returns (rounded_score_float, risk_level_str).
    """
    s_name = _clean_signal(name_similarity, default=0.0)
    s_logo = _clean_signal(logo_similarity, default=0.0)
    s_bio = _clean_signal(bio_similarity, default=0.0)
    s_lookalike = _clean_signal(lookalike_signal, default=0.0)

    score = (
        SOCIAL_WEIGHTS["name_similarity"] * s_name
        + SOCIAL_WEIGHTS["logo_similarity"] * s_logo
        + SOCIAL_WEIGHTS["bio_similarity"] * s_bio
        + SOCIAL_WEIGHTS["lookalike_signal"] * s_lookalike
    ) * 100.0

    rounded_score = round(score, 2)
    risk_level = determine_risk_level(rounded_score)
    return rounded_score, risk_level


def calculate_app_risk(
    title_similarity: Optional[float],
    publisher_mismatch: Optional[float],
    logo_similarity: Optional[float],
    description_similarity: Optional[float],
    lookalike_signal: Optional[float],
) -> Tuple[float, str]:
    """
    Calculates weighted mobile app risk score:
      Score = (0.30 * title + 0.30 * publisher_mismatch + 0.20 * logo + 0.10 * desc + 0.10 * lookalike) * 100.0
    Missing signals default to 0.0, except missing publisher_mismatch defaults to 0.75.
    Returns (rounded_score_float, risk_level_str).
    """
    s_title = _clean_signal(title_similarity, default=0.0)
    s_pub = _clean_signal(publisher_mismatch, default=0.75)
    s_logo = _clean_signal(logo_similarity, default=0.0)
    s_desc = _clean_signal(description_similarity, default=0.0)
    s_lookalike = _clean_signal(lookalike_signal, default=0.0)

    score = (
        APP_WEIGHTS["title_similarity"] * s_title
        + APP_WEIGHTS["publisher_mismatch"] * s_pub
        + APP_WEIGHTS["logo_similarity"] * s_logo
        + APP_WEIGHTS["description_similarity"] * s_desc
        + APP_WEIGHTS["lookalike_signal"] * s_lookalike
    ) * 100.0

    rounded_score = round(score, 2)
    risk_level = determine_risk_level(rounded_score)
    return rounded_score, risk_level
