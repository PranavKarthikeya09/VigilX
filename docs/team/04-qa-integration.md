# Implementation Brief 04: QA Test Specifications & Exclusion Invariants

* **Assigned Team Member:** Person 4 (QA & Integration)
* **Assigned Git Branch:** `test/qa-invariance-suite`
* **Parent Branch:** `origin/master` (Commit `8840f59`)

---

## 1. Objective
Establish comprehensive test fixtures and deterministic test suites verifying the **Official-Asset Exclusion Invariants**. This ensures that official accounts and apps belonging to a brand are 100% excluded from being flagged as threats, while ensuring that malicious lookalikes mimicking official names or developers are never falsely granted immunity.

---

## 2. Exact Initial Files to Inspect

1. **[`backend/tests/conftest.py`](file:///c:/Users/PRANAV%20KARTHIKEYA/OneDrive/Desktop/VigilX/backend/tests/conftest.py):**
   * Inspect existing pytest fixtures (`test_engine`, `test_session`, auth token mocks).
2. **[`backend/tests/test_models.py`](file:///c:/Users/PRANAV%20KARTHIKEYA/OneDrive/Desktop/VigilX/backend/tests/test_models.py):**
   * Inspect existing instantiation of `OfficialSocialAccount` and `OfficialApp` models.
3. **[`backend/app/models/official_asset.py`](file:///c:/Users/PRANAV%20KARTHIKEYA/OneDrive/Desktop/VigilX/backend/app/models/official_asset.py):**
   * Review fields: `OfficialSocialAccount.handle`, `OfficialSocialAccount.url`, `OfficialApp.package_id`, `OfficialApp.store`.
4. **[`docs/team/02-detection-engine.md`](./02-detection-engine.md):**
   * Coordinate candidate data structures and function signatures with Person 2.

---

## 3. Expected Files to Create

* **Create:** `backend/tests/fixtures/mock_candidates.py`
* **Create:** `backend/tests/test_exclusion_invariant.py`
* **Modify:** `backend/tests/conftest.py` (import and expose shared candidate fixtures)

---

## 4. Dependencies & Candidate Threat Structure

Coordinate with Person 2 on the shared `CandidateThreat` dataclass and exclusion checker interface:

```python
# In backend/tests/fixtures/mock_candidates.py (and used across tests)
from dataclasses import dataclass
from typing import Optional, List

@dataclass
class CandidateThreat:
    """Represents an unverified candidate item scraped or ingested for evaluation."""
    source_type: str         # "social" | "app_store"
    platform: str            # "x" | "instagram" | "google_play" | "app_store"
    title: str               # Display name or app title
    handle_or_package: Optional[str] = None  # Normalized social handle or app package ID
    developer_or_owner: Optional[str] = None # App developer name or account owner
    url: Optional[str] = None                # Profile or store URL
    description: Optional[str] = None        # Bio or app description
    logo_url: Optional[str] = None

# Reference function contract implemented in detection engine:
def is_candidate_excluded(
    candidate: CandidateThreat,
    official_socials: List[Any],  # List[OfficialSocialAccount]
    official_apps: List[Any],     # List[OfficialApp]
) -> bool:
    """
    Evaluates whether a candidate strictly matches an official asset.
    Returns True if candidate MUST be excluded from detection results.
    """
```

---

## 5. Strict Official-Asset Exclusion Rules & Invariants

### Rule 1: Social Media Exclusion Invariant
A social candidate is excluded **if and only if**:
* The candidate's `platform` matches the official account's `platform` (case-insensitive); **AND**
* Either:
  1. The candidate's normalized `handle_or_package` (lowercased, stripped of `@` and whitespace) exactly matches the official `handle`; **OR**
  2. The candidate's canonical `url` (normalized scheme, host, path without trailing slashes or query parameters) matches the official `url`.

### Rule 2: Mobile App Store Exclusion Invariant
An app candidate is excluded **if and only if**:
* The candidate's `platform` / `store` matches the official app's `store` (e.g., `'google_play'` or `'app_store'`); **AND**
* The candidate has a **non-null, non-empty** `handle_or_package` (package/bundle ID); **AND**
* That identifier **exactly matches** the official `package_id`.

### Rule 3: Anti-False-Immunity Invariants (CRITICAL)
1. **Never exclude by name alone:** A candidate having the exact official brand name (e.g. title `"Nike"`) must **NOT** be excluded if its handle or package ID differs.
2. **Never exclude by developer name alone:** An app candidate listing developer `"Nike, Inc."` must **NOT** be excluded if its package ID is `com.scam.nike`.
3. **Missing identifier rule:** If a candidate has `handle_or_package = None` or `""`, it must **NEVER** be excluded.
4. **Cross-platform isolation:** An official X handle `@Nike` does **NOT** exclude a TikTok account `@Nike`. An official Google Play app does **NOT** exclude an iOS App Store app unless both are registered.

---

## 6. Canonical URL & Handle Normalization Helper

Implement the normalization utility for test assertion consistency:
```python
import urllib.parse

def normalize_handle(handle: Optional[str]) -> Optional[str]:
    if not handle:
        return None
    return handle.lstrip("@").strip().lower()

def normalize_canonical_url(url: Optional[str]) -> Optional[str]:
    if not url:
        return None
    parsed = urllib.parse.urlparse(url.strip())
    # Normalize scheme to https, lowercase host, strip trailing slash from path
    host = parsed.netloc.lower()
    path = parsed.path.rstrip("/").lower()
    return f"https://{host}{path}"
```

---

## 7. Acceptance Criteria

1. **Deterministic Fixtures:** `mock_candidates.py` provides at least 25 diverse candidate test fixtures:
   * Legitimate official accounts with varying URL formatting.
   * High-risk impersonators with identical names but different handles.
   * Lookalike typo-squatters (`@N1keOfficial`).
   * Malicious apps impersonating legitimate developer names.
   * Candidates with null identifiers.
2. **Full Invariant Coverage in `test_exclusion_invariant.py`:**
   * Test matching social handle $\rightarrow$ `is_candidate_excluded == True`.
   * Test matching canonical URL with different query parameters $\rightarrow$ `is_candidate_excluded == True`.
   * Test matching name with different handle $\rightarrow$ `is_candidate_excluded == False`.
   * Test matching package ID $\rightarrow$ `is_candidate_excluded == True`.
   * Test matching developer name with different package ID $\rightarrow$ `is_candidate_excluded == False`.
   * Test null package ID $\rightarrow$ `is_candidate_excluded == False`.
   * Test platform mismatch (X handle vs Instagram candidate) $\rightarrow$ `is_candidate_excluded == False`.
3. **Privacy & Hygiene:** Zero real user PII in test fixtures (use synthetic brand names like `Nike`, `Acme Security`, `Apex Bank`).
4. **Suite Pass:** Pytest executes all invariant tests with 0 failures or warnings.

---

## 8. Test Execution Commands

Run from the workspace root or `backend/` directory:
```powershell
.\backend\.venv\Scripts\pytest backend\tests\test_exclusion_invariant.py -v
.\backend\.venv\Scripts\pytest backend\tests -v
```

---

## 9. Explicitly Out-of-Scope Work for This Task

* Do **not** implement the full detection engine or RapidFuzz/ImageHash logic (Person 2's focus).
* Do **not** write database seed scripts or demo walkthrough docs yet (Phase C/D).
* Do **not** modify FastAPI routers or Pydantic schemas.
