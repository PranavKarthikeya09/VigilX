# Implementation Brief 02: Detection Similarity & Scoring Algorithms

* **Assigned Team Member:** Person 2 (Detection Engine)
* **Assigned Git Branch:** `feature/engine-similarity-algorithms`
* **Parent Branch:** `origin/master` (Commit `8840f59`)

---

## 1. Objective
Implement deterministic similarity algorithms and multi-signal risk calculation functions for the vigilX detection engine. This includes lookalike name variation generation, RapidFuzz token matching, ImageHash perceptual hash distance, and dual platform-specific risk scoring engines for Social Media and Mobile App Stores.

---

## 2. Exact Initial Files to Inspect

1. **[`backend/requirements.txt`](file:///c:/Users/PRANAV%20KARTHIKEYA/OneDrive/Desktop/VigilX/backend/requirements.txt):**
   * Pre-installed dependencies: `rapidfuzz>=3.0.0`, `imagehash>=4.3.0`, `Pillow>=10.0.0`.
2. **[`backend/app/models/brand.py`](file:///c:/Users/PRANAV%20KARTHIKEYA/OneDrive/Desktop/VigilX/backend/app/models/brand.py):**
   * Inspect `logo_phash: String(64)` format (64-bit hexadecimal pHash representation).
3. **[`backend/app/models/detection.py`](file:///c:/Users/PRANAV%20KARTHIKEYA/OneDrive/Desktop/VigilX/backend/app/models/detection.py):**
   * Inspect `raw_signals: JSON` dictionary structure, `risk_score: Float`, and `risk_level: String(20)` (`'high'`, `'medium'`, `'low'`).
4. **[`docs/BrandGuard_TDD.md`](file:///c:/Users/PRANAV%20KARTHIKEYA/OneDrive/Desktop/VigilX/docs/BrandGuard_TDD.md):**
   * Section 3.3 (Detection Engine Pipeline) & Section 4.1 (Detection raw signals).

---

## 3. Expected Files to Create

* **Create:** `backend/app/services/lookalike.py`
* **Create:** `backend/app/services/logo_similarity.py`
* **Create:** `backend/app/services/scoring.py`
* **Create:** `backend/tests/test_lookalike.py`
* **Create:** `backend/tests/test_scoring.py`

---

## 4. Dependencies & Function Interfaces

### 4.1 `backend/app/services/lookalike.py`

```python
from typing import Optional, List
import rapidfuzz.fuzz as fuzz

# Character substitution map for common homoglyphs and leetspeak
HOMOGLYPH_MAP = {
    'o': ['0', 'o', 'q'],
    'l': ['1', 'i', '|', 'l'],
    'i': ['1', 'l', '!'],
    'e': ['3'],
    'a': ['4', '@'],
    's': ['5', '$'],
    't': ['7', '+'],
}

COMMON_AFFIXES = [
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

def compute_name_similarity(candidate_name: Optional[str], brand_name: str) -> float:
    """
    Computes normalized similarity between candidate name and official brand name.
    Uses RapidFuzz token_sort_ratio and ratio.
    Returns a float strictly in [0.0, 1.0]. Returns 0.0 if candidate_name is None or empty.
    """

def compute_lookalike_signal(candidate_name: Optional[str], brand_name: str) -> float:
    """
    Detects if the candidate name contains specific typosquatting or brand impersonation affixes.
    Returns a float in [0.0, 1.0].
    """
```

---

### 4.2 `backend/app/services/logo_similarity.py`

```python
from typing import Optional
import imagehash

def compute_logo_phash_similarity(candidate_phash: Optional[str], brand_phash: Optional[str]) -> float:
    """
    Computes normalized similarity from two 64-bit hexadecimal perceptual hash strings.
    Formula: 1.0 - (hamming_distance / 64.0)
    Rules:
    - If either candidate_phash or brand_phash is None or invalid: returns 0.0.
    - Result is clamped to [0.0, 1.0].
    """
```

---

### 4.3 `backend/app/services/scoring.py`

```python
from typing import Tuple, Dict, Any

# Platform-specific scoring weights (sum exactly to 1.0)
SOCIAL_WEIGHTS = {
    "name_similarity": 0.40,
    "logo_similarity": 0.30,
    "bio_similarity": 0.15,
    "lookalike_signal": 0.15,
}

APP_WEIGHTS = {
    "title_similarity": 0.30,
    "publisher_mismatch": 0.30,
    "logo_similarity": 0.20,
    "description_similarity": 0.10,
    "lookalike_signal": 0.10,
}

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

def calculate_social_risk(
    name_similarity: float,
    logo_similarity: float,
    bio_similarity: float,
    lookalike_signal: float,
) -> Tuple[float, str]:
    """
    Calculates weighted social risk score:
      Score = (0.40 * name + 0.30 * logo + 0.15 * bio + 0.15 * lookalike) * 100.0
    Returns (rounded_score_float, risk_level_str).
    """

def calculate_app_risk(
    title_similarity: float,
    publisher_mismatch: float,
    logo_similarity: float,
    description_similarity: float,
    lookalike_signal: float,
) -> Tuple[float, str]:
    """
    Calculates weighted mobile app risk score:
      Score = (0.30 * title + 0.30 * publisher_mismatch + 0.20 * logo + 0.10 * desc + 0.10 * lookalike) * 100.0
    Returns (rounded_score_float, risk_level_str).
    """
```

---

## 5. Missing & Edge Value Handling Rules

* **Missing Logo:** If either candidate logo or official brand logo is missing (`None`), `logo_similarity = 0.0`.
* **Missing Bio / Description:** If candidate description or bio is empty, `bio_similarity = 0.0` / `description_similarity = 0.0`.
* **Missing Candidate Publisher:** If candidate app has no developer/publisher listed (`None` or empty), `publisher_mismatch = 0.75` (high suspicion for anonymous publishing).
* **Publisher Mismatch Calculation:**
  * If candidate developer exactly matches official developer $\rightarrow 0.0$.
  * If title similarity $> 0.60$ and candidate developer differs $\rightarrow 1.0$.
  * If title similarity $\le 0.60$ $\rightarrow 0.0$.

---

## 6. Acceptance Criteria

1. **Strict Normalization:** All signal inputs to scoring functions must be normalized to $[0.0, 1.0]$.
2. **Formula Adherence:** Output risk scores must strictly evaluate to $\sum (w_i \cdot s_i) \times 100.0$, rounded to 2 decimal places.
3. **Threshold Precision:**
   * Score `75.0` must evaluate to `'high'`.
   * Score `74.99` must evaluate to `'medium'`.
   * Score `50.0` must evaluate to `'medium'`.
   * Score `49.99` must evaluate to `'low'`.
4. **Deterministic Behavior:** Pure functions with zero side effects; identical inputs must produce identical outputs.
5. **Robustness:** Zero `ZeroDivisionError`, `TypeError`, or `AttributeError` when provided `None`, empty strings, or unparseable hash values.

---

## 7. Required Tests to Implement & Run

Create `backend/tests/test_lookalike.py` and `backend/tests/test_scoring.py`:
* `test_generate_lookalikes`: Verify character swaps (`N1ke`), affixes (`Nike Support`), and case variations.
* `test_name_similarity_identical`: Exact match returns `1.0`.
* `test_name_similarity_unrelated`: `"Adidas"` vs `"Nike"` returns $< 0.3$.
* `test_logo_phash_identical`: Identical hex string returns `1.0`.
* `test_logo_phash_missing`: `None` input returns `0.0`.
* `test_social_risk_calculation`: Known vector (`0.9, 0.8, 0.5, 0.7`) yields expected score and `'high'` tier.
* `test_app_risk_calculation`: Known vector with publisher mismatch yields expected score.
* `test_app_risk_missing_developer_default`: Missing developer assigns `0.75` mismatch penalty.

### Test Execution Command:
```powershell
.\backend\.venv\Scripts\pytest backend\tests\test_lookalike.py backend\tests\test_scoring.py -v
```

---

## 8. Explicitly Out-of-Scope Work for This Task

* Do **not** write live scrapers or make external HTTP network calls.
* Do **not** write database models, SQL queries, or Alembic migrations.
* Do **not** create FastAPI router endpoints or modify `main.py`.
