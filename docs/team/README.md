# vigilX — Team Development & Coordination Guide

Welcome to the **vigilX** development workspace. This guide establishes the team workflow, component ownership, coordination contracts, and testing responsibilities for our four-person engineering team.

---

## 1. Team Allocation Matrix

| Team Member | Core Focus | Dedicated Git Branch | Implementation Brief | Primary First-Task Deliverable |
|---|---|---|---|---|
| **Person 1** | Backend & API | `feature/backend-brand-assets` | [`01-backend-brand-assets.md`](./01-backend-brand-assets.md) | Brand CRUD & Official Asset management endpoints, Pydantic v2 schemas, ownership authorization, async SQLAlchemy queries. |
| **Person 2** | Detection Engine | `feature/engine-similarity-algorithms` | [`02-detection-engine.md`](./02-detection-engine.md) | Lookalike name generation (RapidFuzz), ImageHash perceptual logo comparison, dual-platform risk scoring engine. |
| **Person 3** | Frontend | `feature/frontend-brand-profile` | [`03-frontend-brand-onboarding.md`](./03-frontend-brand-onboarding.md) | Brand onboarding UI, official social and mobile app list management, TypeScript API contracts, form validation. |
| **Person 4** | QA & Integration | `test/qa-invariance-suite` | [`04-qa-integration.md`](./04-qa-integration.md) | Invariant test specifications, deterministic candidate test fixtures, exclusion boundary verification. |

---

## 2. Git Workflow & Collaboration Rules

1. **Master is Protected:** The `master` branch is our single integration branch. No direct commits or unreviewed pushes to `master`.
2. **Dedicated Feature Branches:** All four remote tracking branches have been created from commit `8840f59`:
   * `origin/feature/backend-brand-assets`
   * `origin/feature/engine-similarity-algorithms`
   * `origin/feature/frontend-brand-profile`
   * `origin/test/qa-invariance-suite`
3. **Checking Out Your Branch:**
   ```bash
   git fetch origin
   git checkout <your-branch-name>
   git pull origin <your-branch-name>
   ```
4. **Secret Isolation:** Never commit `.env`, `.env.local`, API keys, private tokens, or database passwords. Verify `.gitignore` rules before staging files.
5. **Database Protection:** The initial database migration (`001_initial_schema.py`) is applied to Supabase PostgreSQL. **Do not modify the database schema, write new migrations, or alter existing models** without explicit team architectural consensus.
6. **Pull Requests & Merge Policy:**
   * Branch merges are **not** driven by a calendar deadline.
   * A branch may only be merged into `master` after:
     1. All self-owned unit/component tests pass cleanly.
     2. Integration verification passes with counterpart components.
     3. A peer review has been completed.
     4. Working tree remains clean with zero regressions.

---

## 3. Required Coordination Touchpoints

To allow all four developers to work independently on Day 1 without blocking each other, two explicit bilateral coordination boundaries are established:

### Coordination Boundary A: Person 1 (Backend) $\longleftrightarrow$ Person 3 (Frontend)
* **Topic:** Brand & Official Asset REST API Contracts.
* **Agreed Standards:**
  * **Brand Entity:** Contains `name` (string), `website` (optional URL string), `logo_url` (optional URL string). **The `Brand` model has NO `description` column.**
  * **Official Social Accounts:** Uses normalized `handle` (lowercase, stripped of `@`) and `raw_handle` (display string with `@`). Supported platforms: `x`, `instagram`, `facebook`, `linkedin`, `tiktok`.
  * **Official Apps:** Uses `name`, `package_id` (bundle identifier), `developer_name` (required), `store` (`'google_play'` | `'app_store'`), `store_url`, and `logo_url`.
  * **Status & Error Responses:** Must conform to `StandardErrorResponse` (`status`, `error_code`, `message`, `details`, `request_id`, `timestamp`).
* **Artifact:** See [`01-backend-brand-assets.md`](./01-backend-brand-assets.md) and [`03-frontend-brand-onboarding.md`](./03-frontend-brand-onboarding.md).

### Coordination Boundary B: Person 2 (Detection Engine) $\longleftrightarrow$ Person 4 (QA & Integration)
* **Topic:** Candidate Threat Dataclass & Official Asset Exclusion Invariants.
* **Agreed Standards:**
  * **Candidate Data Structure:** Shared dataclass `CandidateThreat` defining candidate attributes (`source_type`, `platform`, `title`, `handle_or_package`, `developer_or_owner`, `url`, `description`, `logo_url`).
  * **Exclusion Function Signature:**
    ```python
    def is_candidate_excluded(
        candidate: CandidateThreat,
        official_socials: list,
        official_apps: list,
    ) -> bool:
        ...
    ```
  * **Exclusion Invariants:** Social candidates are excluded only if platform matches AND normalized handle or canonical URL matches. App candidates are excluded only if store matches AND non-null package ID exactly matches. Candidates are **never** excluded by display name or developer name alone.
* **Artifact:** See [`02-detection-engine.md`](./02-detection-engine.md) and [`04-qa-integration.md`](./04-qa-integration.md).

---

## 4. Testing Ownership Policy

* **Every Developer Owns Their Tests:**
  * **Person 1** writes and maintains unit and API endpoint tests for brand and asset routers in `backend/tests/test_api_brands.py`.
  * **Person 2** writes and maintains deterministic algorithmic unit tests for similarity and scoring math in `backend/tests/test_lookalike.py` and `backend/tests/test_scoring.py`.
  * **Person 3** writes and maintains frontend component rendering and form validation tests via TypeScript build checks (`npm run build`).
  * **Person 4** coordinates test fixtures, writes exclusion invariance tests in `backend/tests/test_exclusion_invariant.py`, and orchestrates cross-module integration suites. Person 4 is **not** the sole tester; each teammate must submit passing tests with their PR.

---

## 5. Implementation Sequence & Checkpoints

```
[Day 1 Morning: Independent Parallel Work]
  Person 1: Brand & Asset Schemas + API Routers
  Person 2: Similarity Functions + Lookalike Generators + Scorer
  Person 3: Brand Form + Asset Management Components + Types
  Person 4: Candidate Threat Fixtures + Invariant Test Suite
                           │
                           ▼
[Day 1 Afternoon: Bilateral Verification]
  Checkpoint A: Person 1 & 3 test UI against live API endpoints
  Checkpoint B: Person 2 & 4 run Invariant Tests against Scorer & Exclusion logic
                           │
                           ▼
[Day 1 Evening: Integration & Merge Review]
  Full backend pytest suite (target: >= 25 tests passing)
  Full frontend production build (tsc -b && vite build)
  PR Review & Merge into master
```
