from typing import Optional, List
import re

try:
    import rapidfuzz.fuzz as fuzz
except ImportError:  # pragma: no cover
    fuzz = None

# Character substitution map for common homoglyphs and leetspeak
HOMOGLYPH_MAP: dict[str, list[str]] = {
    'o': ['0', 'o', 'q'],
    'l': ['1', 'i', '|', 'l'],
    'i': ['1', 'l', '!'],
    'e': ['3'],
    'a': ['4', '@'],
    's': ['5', '$'],
    't': ['7', '+'],
}

COMMON_AFFIXES: list[str] = [
    "official", "support", "help", "care", "service",
    "desk", "login", "auth", "security", "app", "mobile"
]


def generate_lookalikes(brand_name: str) -> List[str]:
    """
    Generates deterministic look-alike variations of a brand name:
    1. Homoglyph / leetspeak character swaps (e.g., 'Nike' -> 'N1ke', 'Nlke', 'Nik3')
    2. Common affix combinations (e.g., 'Nike Support', 'Official Nike', 'Nike-App')
    3. Spacing and hyphenation variations (e.g., 'Ni ke', 'Ni-ke')
    """
    if not brand_name:
        return []

    clean_name = brand_name.strip()
    if not clean_name:
        return []

    variations: List[str] = []
    seen: set[str] = {clean_name}

    def _add_variation(val: str) -> None:
        trimmed = val.strip()
        if trimmed and trimmed not in seen:
            seen.add(trimmed)
            variations.append(trimmed)

    # 1. Homoglyph / leetspeak character swaps
    for i, ch in enumerate(clean_name):
        ch_lower = ch.lower()
        if ch_lower in HOMOGLYPH_MAP:
            for sub in HOMOGLYPH_MAP[ch_lower]:
                if sub.lower() != ch_lower:
                    _add_variation(clean_name[:i] + sub + clean_name[i + 1:])

    # Full homoglyph replacement (e.g. 'N1k3') if multiple substitutable characters exist
    full_sub_chars: list[str] = []
    has_sub = False
    for ch in clean_name:
        ch_lower = ch.lower()
        if ch_lower in HOMOGLYPH_MAP:
            rep = next((s for s in HOMOGLYPH_MAP[ch_lower] if s.lower() != ch_lower), None)
            if rep is not None:
                full_sub_chars.append(rep)
                has_sub = True
            else:
                full_sub_chars.append(ch)
        else:
            full_sub_chars.append(ch)
    if has_sub:
        _add_variation("".join(full_sub_chars))

    # 2. Common affix combinations
    for affix in COMMON_AFFIXES:
        affix_cap = affix.capitalize()
        # Capitalized affixes: 'Nike Support', 'Official Nike', 'Nike-App', 'Official-Nike'
        _add_variation(f"{clean_name} {affix_cap}")
        _add_variation(f"{affix_cap} {clean_name}")
        _add_variation(f"{clean_name}-{affix_cap}")
        _add_variation(f"{affix_cap}-{clean_name}")
        # Lowercase / raw affix combinations
        _add_variation(f"{clean_name} {affix}")
        _add_variation(f"{affix} {clean_name}")
        _add_variation(f"{clean_name}-{affix}")
        _add_variation(f"{affix}-{clean_name}")

    # 3. Spacing and hyphenation variations
    if " " not in clean_name and "-" not in clean_name:
        for k in range(1, len(clean_name)):
            _add_variation(f"{clean_name[:k]} {clean_name[k:]}")
            _add_variation(f"{clean_name[:k]}-{clean_name[k:]}")
    else:
        if " " in clean_name:
            _add_variation(clean_name.replace(" ", "-"))
            _add_variation(clean_name.replace(" ", ""))
        if "-" in clean_name:
            _add_variation(clean_name.replace("-", " "))
            _add_variation(clean_name.replace("-", ""))

    return variations


def compute_name_similarity(candidate_name: Optional[str], brand_name: str) -> float:
    """
    Computes normalized similarity between candidate name and official brand name.
    Uses RapidFuzz token_sort_ratio and ratio.
    Returns a float strictly in [0.0, 1.0]. Returns 0.0 if candidate_name is None or empty.
    """
    if not candidate_name or not candidate_name.strip():
        return 0.0
    if not brand_name or not brand_name.strip():
        return 0.0

    c = candidate_name.strip().lower()
    b = brand_name.strip().lower()

    if c == b:
        return 1.0

    if fuzz is not None:
        r = float(fuzz.ratio(c, b)) / 100.0
        tsr = float(fuzz.token_sort_ratio(c, b)) / 100.0
    else:
        # Fallback when rapidfuzz is not yet installed in local environment
        import difflib
        r = difflib.SequenceMatcher(None, c, b).ratio()
        c_tokens = " ".join(sorted(c.split()))
        b_tokens = " ".join(sorted(b.split()))
        tsr = difflib.SequenceMatcher(None, c_tokens, b_tokens).ratio()

    score = max(r, tsr)
    return round(max(0.0, min(1.0, score)), 4)


def _is_boundary_match(target: str, text: str) -> bool:
    """
    Checks whether target appears in text with boundary/delimiter awareness
    (e.g., spaces, hyphens, underscores, dots, or start/end of string).
    Prevents short brand names like 'x' or 'in' from matching inside unrelated
    words like 'max security' or 'information desk'.
    """
    pattern = r'(?:^|[^a-zA-Z0-9])' + re.escape(target) + r'(?:$|[^a-zA-Z0-9])'
    return bool(re.search(pattern, text))


def compute_lookalike_signal(candidate_name: Optional[str], brand_name: str) -> float:
    """
    Detects if the candidate name contains specific typosquatting or brand impersonation affixes.
    Returns a float in [0.0, 1.0]. Returns 0.0 if candidate_name is None or empty.
    """
    if not candidate_name or not candidate_name.strip():
        return 0.0
    if not brand_name or not brand_name.strip():
        return 0.0

    c_clean = candidate_name.strip()
    b_clean = brand_name.strip()
    c_lower = c_clean.lower()
    b_lower = b_clean.lower()

    # Exact match is not a typosquatted lookalike; it is captured by name_similarity
    if c_lower == b_lower:
        return 0.0

    # 1. Match against generated lookalike variations
    generated = generate_lookalikes(b_clean)
    generated_lower = {v.lower() for v in generated}
    if c_lower in generated_lower:
        has_affix_in_cand = any(
            re.search(r'(?:\b|_|-)' + re.escape(affix) + r'(?:\b|_|-)', c_lower)
            for affix in COMMON_AFFIXES
        )
        if has_affix_in_cand:
            return 0.9
        return 0.8

    # 2. Check for suspicious affix co-occurring with brand name
    has_affix = False
    for affix in COMMON_AFFIXES:
        if re.search(r'(?:\b|_|-)' + re.escape(affix) + r'(?:\b|_|-)', c_lower):
            has_affix = True
            break

    # Reverse homoglyph mapping to detect un-leeted brand name
    reverse_map = {
        '0': 'o',
        '1': 'l',
        '!': 'i',
        '|': 'l',
        '3': 'e',
        '4': 'a',
        '@': 'a',
        '5': 's',
        '$': 's',
        '7': 't',
        '+': 't',
    }
    unleeted_1 = "".join(reverse_map.get(ch, ch) for ch in c_lower)
    reverse_map_alt = dict(reverse_map)
    reverse_map_alt['1'] = 'i'
    unleeted_2 = "".join(reverse_map_alt.get(ch, ch) for ch in c_lower)

    has_brand_in_cand = _is_boundary_match(b_lower, c_lower)
    has_homoglyph_brand = (not has_brand_in_cand) and (
        _is_boundary_match(b_lower, unleeted_1) or _is_boundary_match(b_lower, unleeted_2)
    )

    if has_homoglyph_brand and has_affix:
        return 0.95
    if has_homoglyph_brand:
        return 0.85
    if has_brand_in_cand and has_affix:
        return 0.75

    return 0.0
