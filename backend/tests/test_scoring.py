"""Unit tests for risk-scoring engine, publisher mismatch, and logo similarity."""
try:
    import pytest
except ImportError:
    pytest = None

from app.services.scoring import (
    SOCIAL_WEIGHTS,
    APP_WEIGHTS,
    _clean_signal,
    determine_risk_level,
    compute_publisher_mismatch,
    calculate_social_risk,
    calculate_app_risk,
)
from app.services.logo_similarity import compute_logo_phash_similarity


def test_weights_sum_to_one():
    """Verify social and app scoring weights sum exactly to 1.0."""
    social_sum = sum(SOCIAL_WEIGHTS.values())
    app_sum = sum(APP_WEIGHTS.values())
    assert abs(social_sum - 1.0) < 1e-6
    assert abs(app_sum - 1.0) < 1e-6


def test_social_scoring_known_vector():
    """
    Test social scoring using vector from brief:
      name=0.9, logo=0.8, bio=0.5, lookalike=0.7
      Score = 100 * (0.9*0.40 + 0.8*0.30 + 0.5*0.15 + 0.7*0.15)
            = 100 * (0.36 + 0.24 + 0.075 + 0.105) = 78.0
      Risk Tier: High (>= 75.0)
    Also verify vector yielding 76.5 (lookalike=0.6):
      Score = 100 * (0.36 + 0.24 + 0.075 + 0.09) = 76.5 -> High
    """
    score, level = calculate_social_risk(
        name_similarity=0.9,
        logo_similarity=0.8,
        bio_similarity=0.5,
        lookalike_signal=0.7,
    )
    assert score == 78.0
    assert level == "high"

    # Alternate vector yielding 76.5
    score_76_5, level_76_5 = calculate_social_risk(
        name_similarity=0.9,
        logo_similarity=0.8,
        bio_similarity=0.5,
        lookalike_signal=0.6,
    )
    assert score_76_5 == 76.5
    assert level_76_5 == "high"


def test_app_risk_calculation_with_mismatch():
    """Verify app risk calculation with publisher mismatch flag."""
    # title=0.8, mismatch=1.0, logo=0.6, desc=0.4, lookalike=0.5
    # score = 100 * (0.8*0.3 + 1.0*0.3 + 0.6*0.2 + 0.4*0.1 + 0.5*0.1)
    #       = 100 * (0.24 + 0.30 + 0.12 + 0.04 + 0.05) = 75.0 -> High
    score, level = calculate_app_risk(
        title_similarity=0.8,
        publisher_mismatch=1.0,
        logo_similarity=0.6,
        description_similarity=0.4,
        lookalike_signal=0.5,
    )
    assert score == 75.0
    assert level == "high"


def test_publisher_mismatch_missing_candidate():
    """Missing candidate developer yields default 0.75 mismatch penalty."""
    assert compute_publisher_mismatch(None, "Nike, Inc.", 0.8) == 0.75
    assert compute_publisher_mismatch("", "Nike, Inc.", 0.8) == 0.75
    assert compute_publisher_mismatch("   ", "Nike, Inc.", 0.8) == 0.75


def test_publisher_mismatch_exact_match():
    """Exact normalized developer match yields 0.0 mismatch."""
    assert compute_publisher_mismatch("Nike, Inc.", "Nike, Inc.", 0.8) == 0.0
    assert compute_publisher_mismatch("  nike, inc.  ", "Nike, Inc.", 0.8) == 0.0
    assert compute_publisher_mismatch("NIKE, INC.", "nike, inc.", 0.8) == 0.0


def test_publisher_mismatch_title_above_threshold():
    """If developer differs and title similarity > 0.60, mismatch = 1.0."""
    assert compute_publisher_mismatch("ScamDev", "Nike, Inc.", 0.61) == 1.0
    assert compute_publisher_mismatch("ScamDev", "Nike, Inc.", 0.95) == 1.0


def test_publisher_mismatch_title_at_or_below_threshold():
    """If developer differs but title similarity <= 0.60, mismatch = 0.0."""
    assert compute_publisher_mismatch("ScamDev", "Nike, Inc.", 0.60) == 0.0
    assert compute_publisher_mismatch("ScamDev", "Nike, Inc.", 0.59) == 0.0
    assert compute_publisher_mismatch("ScamDev", "Nike, Inc.", 0.20) == 0.0


def test_missing_signals_default_to_zero():
    """Missing logo, bio, description default to 0.0 without errors."""
    score, level = calculate_social_risk(
        name_similarity=0.8,
        logo_similarity=None,
        bio_similarity=None,
        lookalike_signal=0.5,
    )
    # score = 100 * (0.8*0.40 + 0 + 0 + 0.5*0.15) = 100 * (0.32 + 0.075) = 39.5
    assert score == 39.5
    assert level == "low"

    app_score, app_level = calculate_app_risk(
        title_similarity=0.8,
        publisher_mismatch=0.0,
        logo_similarity=None,
        description_similarity=None,
        lookalike_signal=0.5,
    )
    # score = 100 * (0.8*0.30 + 0 + 0 + 0 + 0.5*0.10) = 100 * (0.24 + 0.05) = 29.0
    assert app_score == 29.0
    assert app_level == "low"


def test_app_risk_missing_publisher_default_in_scoring():
    """When publisher_mismatch signal is None in calculate_app_risk, defaults to 0.75."""
    score, level = calculate_app_risk(
        title_similarity=0.0,
        publisher_mismatch=None,
        logo_similarity=0.0,
        description_similarity=0.0,
        lookalike_signal=0.0,
    )
    # score = 100 * (0.30 * 0.75) = 22.5
    assert score == 22.5
    assert level == "low"


def test_risk_level_boundaries():
    """
    Test exact boundary thresholds:
    - High: score >= 75.0
    - Medium: 50.0 <= score < 75.0
    - Low: score < 50.0
    """
    assert determine_risk_level(75.0) == "high"
    assert determine_risk_level(75.01) == "high"
    assert determine_risk_level(74.99) == "medium"
    assert determine_risk_level(50.0) == "medium"
    assert determine_risk_level(50.01) == "medium"
    assert determine_risk_level(49.99) == "low"
    assert determine_risk_level(0.0) == "low"
    assert determine_risk_level(100.0) == "high"


def test_logo_phash_similarity_suite():
    """Comprehensive logo similarity tests incorporated into test_scoring suite."""
    # 1. Identical hashes
    assert compute_logo_phash_similarity("ffd0c00000000000", "ffd0c00000000000") == 1.0
    assert compute_logo_phash_similarity("ffffffffffffffff", "ffffffffffffffff") == 1.0
    assert compute_logo_phash_similarity("0x1234567890abcdef", "1234567890abcdef") == 1.0

    # 2. One-bit difference (hamming = 1) -> 1 - (1/64) = 0.984375
    assert compute_logo_phash_similarity("0000000000000000", "0000000000000001") == 0.984375

    # 3. Completely different hashes (64 bits different) -> 0.0
    assert compute_logo_phash_similarity("0000000000000000", "ffffffffffffffff") == 0.0

    # 4. Missing / None values -> 0.0
    assert compute_logo_phash_similarity(None, "ffd0c00000000000") == 0.0
    assert compute_logo_phash_similarity("ffd0c00000000000", None) == 0.0
    assert compute_logo_phash_similarity(None, None) == 0.0
    assert compute_logo_phash_similarity("", "ffd0c00000000000") == 0.0
    assert compute_logo_phash_similarity("   ", "ffd0c00000000000") == 0.0

    # 5. Invalid hexadecimal strings -> 0.0
    assert compute_logo_phash_similarity("not_a_hex_string", "ffd0c00000000000") == 0.0
    assert compute_logo_phash_similarity("zzzzzzzzzzzzzzzz", "ffd0c00000000000") == 0.0

    # 6. Incorrect hash lengths -> 0.0
    assert compute_logo_phash_similarity("123", "ffd0c00000000000") == 0.0
    assert compute_logo_phash_similarity("f" * 15, "f" * 16) == 0.0
    assert compute_logo_phash_similarity("f" * 17, "f" * 16) == 0.0
    assert compute_logo_phash_similarity("f" * 64, "f" * 16) == 0.0


def test_none_and_empty_inputs_safety():
    """Verify zero unhandled exceptions on None inputs across all functions."""
    score_soc, lvl_soc = calculate_social_risk(None, None, None, None)
    assert score_soc == 0.0
    assert lvl_soc == "low"

    score_app, lvl_app = calculate_app_risk(None, None, None, None, None)
    assert score_app == 22.5  # Default publisher mismatch 0.75 * 0.30 * 100
    assert lvl_app == "low"


def test_deterministic_scoring_results():
    """Verify identical inputs produce identical scores across multiple calls."""
    res1 = calculate_social_risk(0.85, 0.75, 0.60, 0.40)
    res2 = calculate_social_risk(0.85, 0.75, 0.60, 0.40)
    assert res1 == res2

    app1 = calculate_app_risk(0.70, 0.50, 0.80, 0.30, 0.60)
    app2 = calculate_app_risk(0.70, 0.50, 0.80, 0.30, 0.60)
    assert app1 == app2


def test_clean_signal_non_finite_and_clamping():
    """Verify _clean_signal handles NaN, infinities, non-numeric strings, and out-of-bounds floats."""
    # NaN must not become 1.0 (maximum signal); should return default
    assert _clean_signal(float("nan"), default=0.0) == 0.0
    assert _clean_signal(float("nan"), default=0.75) == 0.75
    assert _clean_signal("nan", default=0.0) == 0.0

    # Infinities must return default
    assert _clean_signal(float("inf"), default=0.0) == 0.0
    assert _clean_signal(float("-inf"), default=0.0) == 0.0
    assert _clean_signal("inf", default=0.0) == 0.0
    assert _clean_signal("-inf", default=0.0) == 0.0

    # None and invalid non-numeric strings return default
    assert _clean_signal(None, default=0.0) == 0.0
    assert _clean_signal(None, default=0.75) == 0.75
    assert _clean_signal("not_a_number", default=0.0) == 0.0

    # Ordinary finite inputs clamped to [0.0, 1.0]
    assert _clean_signal(-0.5, default=0.0) == 0.0
    assert _clean_signal(1.5, default=0.0) == 1.0
    assert _clean_signal(0.42, default=0.0) == 0.42


def test_social_scoring_with_non_finite_inputs():
    """Verify social scoring handles NaN and infinities safely by falling back to default 0.0."""
    score, level = calculate_social_risk(
        name_similarity=float("nan"),
        logo_similarity=0.8,
        bio_similarity=float("inf"),
        lookalike_signal=float("-inf"),
    )
    # NaN and inf signals default to 0.0 -> score = 100 * (0.8 * 0.30) = 24.0
    assert score == 24.0
    assert level == "low"


def test_app_risk_with_non_finite_inputs():
    """Verify app risk scoring handles NaN and infinities safely (publisher mismatch defaults to 0.75)."""
    score, level = calculate_app_risk(
        title_similarity=float("nan"),
        publisher_mismatch=float("nan"),
        logo_similarity=0.5,
        description_similarity=0.2,
        lookalike_signal=0.1,
    )
    # NaN title defaults to 0.0, NaN publisher mismatch defaults to 0.75
    # score = 100 * (0.30*0.75 + 0.20*0.5 + 0.10*0.2 + 0.10*0.1)
    #       = 100 * (0.225 + 0.10 + 0.02 + 0.01) = 35.5
    assert score == 35.5
    assert level == "low"


if __name__ == "__main__":
    import sys

    tests = [
        test_weights_sum_to_one,
        test_social_scoring_known_vector,
        test_app_risk_calculation_with_mismatch,
        test_publisher_mismatch_missing_candidate,
        test_publisher_mismatch_exact_match,
        test_publisher_mismatch_title_above_threshold,
        test_publisher_mismatch_title_at_or_below_threshold,
        test_missing_signals_default_to_zero,
        test_app_risk_missing_publisher_default_in_scoring,
        test_risk_level_boundaries,
        test_logo_phash_similarity_suite,
        test_none_and_empty_inputs_safety,
        test_deterministic_scoring_results,
        test_clean_signal_non_finite_and_clamping,
        test_social_scoring_with_non_finite_inputs,
        test_app_risk_with_non_finite_inputs,
    ]

    passed = 0
    failed = 0
    print(f"Running {len(tests)} tests directly in {__file__}...")
    for t in tests:
        try:
            t()
            passed += 1
            print(f"  PASS: {t.__name__}")
        except Exception as e:
            failed += 1
            print(f"  FAIL: {t.__name__}: {e}")

    print(f"\nResult: {passed} passed, {failed} failed")
    if failed > 0:
        sys.exit(1)
