"""Unit tests for lookalike generation and name similarity services."""
try:
    import pytest
except ImportError:
    pytest = None
from app.services.lookalike import (
    HOMOGLYPH_MAP,
    COMMON_AFFIXES,
    generate_lookalikes,
    compute_name_similarity,
    compute_lookalike_signal,
)


def test_constants_structure():
    """Verify HOMOGLYPH_MAP and COMMON_AFFIXES exist and contain required entries."""
    assert isinstance(HOMOGLYPH_MAP, dict)
    assert 'o' in HOMOGLYPH_MAP and '0' in HOMOGLYPH_MAP['o']
    assert 'l' in HOMOGLYPH_MAP and '1' in HOMOGLYPH_MAP['l']
    assert 'e' in HOMOGLYPH_MAP and '3' in HOMOGLYPH_MAP['e']
    assert 'a' in HOMOGLYPH_MAP and '4' in HOMOGLYPH_MAP['a']
    assert 's' in HOMOGLYPH_MAP and '5' in HOMOGLYPH_MAP['s']
    assert 't' in HOMOGLYPH_MAP and '7' in HOMOGLYPH_MAP['t']

    assert isinstance(COMMON_AFFIXES, list)
    assert "official" in COMMON_AFFIXES
    assert "support" in COMMON_AFFIXES
    assert "app" in COMMON_AFFIXES


def test_generate_lookalikes_nike_expected_variations():
    """Verify Nike generates character swaps, affixes, and spacing variations from brief."""
    results = generate_lookalikes("Nike")
    assert len(results) > 0

    # 1. Homoglyphs
    assert "N1ke" in results
    assert "Nlke" in results
    assert "Nik3" in results

    # 2. Common affixes
    assert "Nike Support" in results
    assert "Official Nike" in results
    assert "Nike-App" in results

    # 3. Spacing and hyphenation
    assert "Ni ke" in results
    assert "Ni-ke" in results


def test_generate_lookalikes_duplicate_prevention_and_determinism():
    """Verify that generate_lookalikes produces deterministic output with zero duplicates."""
    run1 = generate_lookalikes("Nike")
    run2 = generate_lookalikes("Nike")

    assert run1 == run2  # Deterministic order and contents
    assert len(run1) == len(set(run1))  # No duplicates
    assert "Nike" not in run1  # Original brand name excluded


def test_generate_lookalikes_empty_and_whitespace():
    """Verify handling of empty, whitespace, or invalid brand names."""
    assert generate_lookalikes("") == []
    assert generate_lookalikes("   ") == []


def test_generate_lookalikes_different_lengths():
    """Verify generation works across single-letter, two-letter, and multi-word names."""
    # Single letter
    res_x = generate_lookalikes("X")
    assert isinstance(res_x, list)
    assert "X Official" in res_x

    # Two letters
    res_hp = generate_lookalikes("HP")
    assert "H P" in res_hp
    assert "H-P" in res_hp

    # Multi-word brand
    res_multi = generate_lookalikes("Nike Air")
    assert "Nike-Air" in res_multi
    assert "NikeAir" in res_multi


def test_name_similarity_identical():
    """Exact matches must return 1.0."""
    assert compute_name_similarity("Nike", "Nike") == 1.0
    assert compute_name_similarity("nike", "Nike") == 1.0
    assert compute_name_similarity("  NIKE  ", "nike") == 1.0


def test_name_similarity_small_edits():
    """Small edits should have high similarity (> 0.7) but <= 1.0."""
    score = compute_name_similarity("Nikee", "Nike")
    assert 0.70 <= score < 1.0

    score_sub = compute_name_similarity("Niek", "Nike")
    assert 0.60 <= score_sub < 1.0


def test_name_similarity_unrelated():
    """Unrelated names must return < 0.3 as required by the brief."""
    assert compute_name_similarity("Adidas", "Nike") < 0.3
    assert compute_name_similarity("Google", "Nike") < 0.3
    assert compute_name_similarity("Microsoft", "Apple") < 0.3


def test_name_similarity_empty_and_none():
    """Empty, whitespace, or None candidate names must return 0.0."""
    assert compute_name_similarity(None, "Nike") == 0.0
    assert compute_name_similarity("", "Nike") == 0.0
    assert compute_name_similarity("   ", "Nike") == 0.0
    assert compute_name_similarity("Nike", "") == 0.0
    assert compute_name_similarity("Nike", "   ") == 0.0


def test_name_similarity_normalization_bounds():
    """Verify return values are strictly in [0.0, 1.0]."""
    test_cases = [
        ("N1ke", "Nike"),
        ("Official Nike Store", "Nike"),
        ("Random String", "Nike"),
        ("A", "Z"),
    ]
    for cand, brand in test_cases:
        score = compute_name_similarity(cand, brand)
        assert 0.0 <= score <= 1.0


def test_lookalike_signal_empty_and_identical():
    """Empty/None inputs and identical names return 0.0."""
    assert compute_lookalike_signal(None, "Nike") == 0.0
    assert compute_lookalike_signal("", "Nike") == 0.0
    assert compute_lookalike_signal("Nike", "") == 0.0
    assert compute_lookalike_signal("Nike", "Nike") == 0.0
    assert compute_lookalike_signal("nike", "Nike") == 0.0


def test_lookalike_signal_generated_variations():
    """Candidates in generated lookalikes yield non-zero risk signals in [0.0, 1.0]."""
    # Homoglyph lookalike
    sig_homoglyph = compute_lookalike_signal("N1ke", "Nike")
    assert 0.0 < sig_homoglyph <= 1.0

    # Affix lookalike
    sig_affix = compute_lookalike_signal("Nike Support", "Nike")
    assert 0.0 < sig_affix <= 1.0

    # Hyphenated affix
    sig_hyphen = compute_lookalike_signal("Nike-App", "Nike")
    assert 0.0 < sig_hyphen <= 1.0


def test_lookalike_signal_unrelated_and_affix_alone():
    """Unrelated names and generic affix names without brand return 0.0."""
    assert compute_lookalike_signal("Adidas", "Nike") == 0.0
    assert compute_lookalike_signal("Support", "Nike") == 0.0
    assert compute_lookalike_signal("Help Desk", "Nike") == 0.0


def test_lookalike_signal_combined_homoglyph_and_affix():
    """Combination of homoglyph and suspicious affix yields high signal."""
    sig = compute_lookalike_signal("N1ke Support", "Nike")
    assert sig >= 0.85
    assert sig <= 1.0


def test_lookalike_signal_short_brand_substring_immunity():
    """
    Regression test: short brand names must not match as raw substrings inside unrelated words
    merely because a suspicious affix appears elsewhere in the candidate.
    """
    # 'x' inside 'max', affix 'security'
    assert compute_lookalike_signal("Max Security", "X") == 0.0

    # 'in' inside 'information', affix 'desk'
    assert compute_lookalike_signal("Information Desk", "In") == 0.0

    # 'go' inside 'google', affix 'official'
    assert compute_lookalike_signal("Google Official", "Go") == 0.0

    # 'up' inside 'super', affix 'support'
    assert compute_lookalike_signal("Super Support", "Up") == 0.0


def test_lookalike_signal_legitimate_brand_affix_detections():
    """
    Positive test: legitimate brand occurrences with boundary separators
    (space, hyphen, underscore, @) and suspicious affixes must be detected.
    """
    assert compute_lookalike_signal("X Security", "X") >= 0.75
    assert compute_lookalike_signal("X-Security", "X") >= 0.75
    assert compute_lookalike_signal("X_Security", "X") >= 0.75
    assert compute_lookalike_signal("In Support", "In") >= 0.75
    assert compute_lookalike_signal("Nike Official", "Nike") >= 0.75
    assert compute_lookalike_signal("Official_Nike", "Nike") >= 0.75
    assert compute_lookalike_signal("@Nike Support", "Nike") >= 0.75


if __name__ == "__main__":
    import sys

    # Direct test execution when pytest is not installed in the current environment
    tests = [
        test_constants_structure,
        test_generate_lookalikes_nike_expected_variations,
        test_generate_lookalikes_duplicate_prevention_and_determinism,
        test_generate_lookalikes_empty_and_whitespace,
        test_generate_lookalikes_different_lengths,
        test_name_similarity_identical,
        test_name_similarity_small_edits,
        test_name_similarity_unrelated,
        test_name_similarity_empty_and_none,
        test_name_similarity_normalization_bounds,
        test_lookalike_signal_empty_and_identical,
        test_lookalike_signal_generated_variations,
        test_lookalike_signal_unrelated_and_affix_alone,
        test_lookalike_signal_combined_homoglyph_and_affix,
        test_lookalike_signal_short_brand_substring_immunity,
        test_lookalike_signal_legitimate_brand_affix_detections,
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
