from typing import Optional

try:
    import imagehash
except ImportError:  # pragma: no cover
    imagehash = None


def _parse_64bit_phash(val: Optional[str]) -> Optional[int]:
    """
    Parses and validates a 64-bit hexadecimal perceptual hash string.
    A valid 64-bit hash in hexadecimal consists of exactly 16 hex characters
    (optionally prefixed with '0x').
    Returns the parsed integer value, or None if invalid.
    """
    if not val or not isinstance(val, str):
        return None
    s = val.strip()
    if not s:
        return None
    if s.startswith(('0x', '0X')):
        s = s[2:]
    # Exactly 16 hexadecimal characters represents 64 bits (16 * 4 = 64)
    if len(s) != 16:
        return None
    try:
        return int(s, 16)
    except ValueError:
        return None


def compute_logo_phash_similarity(candidate_phash: Optional[str], brand_phash: Optional[str]) -> float:
    """
    Computes normalized similarity from two 64-bit hexadecimal perceptual hash strings.
    Formula: 1.0 - (hamming_distance / 64.0)

    Rules:
    - If either candidate_phash or brand_phash is None, empty, non-hex,
      or not a valid 64-bit hexadecimal hash: returns 0.0.
    - Clamped to strictly [0.0, 1.0].
    - Returns 1.0 for identical valid hashes.
    """
    val1 = _parse_64bit_phash(candidate_phash)
    val2 = _parse_64bit_phash(brand_phash)

    if val1 is None or val2 is None:
        return 0.0

    # Hamming distance is the number of differing bits between the two 64-bit integers
    hamming_distance = (val1 ^ val2).bit_count()
    similarity = 1.0 - (float(hamming_distance) / 64.0)

    return max(0.0, min(1.0, similarity))
