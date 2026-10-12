# Test Strategy & Quality Assurance Plan
## BrandGuard – Digital Risk Protection Platform
### Social & App Monitoring

**Document Version:** 1.0  
**Date:** 12 October 2026  
**Author:** QA Lead / SDET Architect  
**Status:** Draft for Hackathon MVP  
**Related Documents:** BrandGuard PRD v1.0, TDD v1.0, API Spec v1.0

---

## 1. Quality Objectives & Quality Gates

### 1.1 Quality Objectives
- Deliver a reliable, demo-ready MVP that correctly detects brand impersonations while **never** flagging official assets.
- Ensure high confidence in multi-signal risk scoring and look-alike name detection.
- Provide a clean, usable interface with predictable behaviour under normal and edge-case conditions.
- Achieve sufficient automated test coverage so that last-minute changes do not break core flows during the presentation.

### 1.2 Definition of Done (DoD)
A user story / feature is considered **Done** only when:
- [ ] Code is merged to main after peer review
- [ ] Unit tests written and passing (minimum coverage thresholds met)
- [ ] Integration tests covering the happy path and key negative cases are passing
- [ ] API contract tests (against the published OpenAPI spec) are green
- [ ] Manual exploratory testing completed on the critical path
- [ ] No open P0 or P1 defects
- [ ] Documentation (API notes / seed data) updated if required
- [ ] Feature is demonstrable in the staging environment

### 1.3 Quality Gates (Hackathon MVP)

| Gate                        | Minimum Requirement                          | Blocking? |
|-----------------------------|----------------------------------------------|---------|
| Unit Test Coverage          | Backend ≥ 70% line coverage<br>Frontend ≥ 60% statement coverage | Yes |
| Critical Path E2E           | All 5 critical user journeys pass            | Yes |
| Official Asset Exclusion    | 100% of official assets excluded in test suite | Yes |
| API Contract Compliance     | All endpoints match the API Spec             | Yes |
| Open P0/P1 Defects          | Zero                                          | Yes |
| Performance (Dashboard)     | p95 < 2.5 s for typical brand data set       | Soft (demo) |
| Security Smoke              | Auth required on protected routes, no obvious injection | Yes |

---

## 2. Testing Levels & Scope

### 2.1 Unit Testing

**Scope**
- Backend: Business logic (look-alike generation, risk scoring, similarity calculations, ownership checks)
- Frontend: Utility functions, custom hooks, pure components, form validation

**Tools**
| Layer     | Framework              | Assertion / Mocking          |
|-----------|------------------------|------------------------------|
| Backend   | pytest + pytest-cov    | pytest-mock / unittest.mock  |
| Frontend  | Vitest + React Testing Library | vi.mock / MSW (optional) |

**Standards**
- Every pure function in `services/lookalike.py`, `services/scoring.py`, and `services/logo_similarity.py` must have dedicated unit tests.
- Edge cases for look-alike names (character swaps, added words, spacing, empty strings, very long names) are mandatory.
- Risk score calculation must be tested with known input → expected output tables.
- Mock external dependencies (database, Redis, image loading) at the unit level.
- Coverage reports generated on every CI run; failing under threshold blocks merge.

### 2.2 Integration Testing

**Scope**
- API endpoints + database interactions
- Brand ownership enforcement
- Detection pipeline (with mocked external data sources)
- Official asset exclusion logic end-to-end within the service layer

**Approach**
- Prefer **Testcontainers** (PostgreSQL) for realistic database behaviour.
- For speed in local development, an in-memory SQLite fallback is allowed **only** for pure unit-style integration tests.
- External data sources (Google Play, X search) are always mocked.
- Use FastAPI’s `TestClient` or `httpx.AsyncClient` with dependency overrides.

**Key Scenarios**
- Create brand → add official assets → run detection → verify official assets never appear in results
- Risk score calculation with multi-signal inputs
- Status transitions on detections
- Pagination, filtering, and sorting of detections
- Authentication & authorization failures

### 2.3 End-to-End (E2E) Testing

**Scope – Critical User Paths (Must Pass)**

| # | Critical Path                                      | Priority |
|---|----------------------------------------------------|----------|
| 1 | User logs in → creates Brand Profile → uploads logo → adds official social + apps | P0 |
| 2 | Trigger detection job → view prioritized detections on dashboard | P0 |
| 3 | Open high-risk detection → view evidence & signal breakdown → mark as False Positive / Escalated | P0 |
| 4 | Official assets are never shown in detection results | P0 |
| 5 | Filter detections by risk level / source / status | P1 |

**Edge Cases to Cover**
- Empty brand profile (no official assets)
- Brand with many look-alike candidates
- Network failure / mocked external source unavailable (graceful degradation)
- Concurrent status updates
- Extremely long brand names or special characters

**Tools**
- Playwright (recommended) or Cypress
- Run against a seeded staging / ephemeral environment
- Visual regression optional (Percy / Chromatic) if time permits

### 2.4 Performance & Load Testing Criteria

**Targets (MVP / Demo)**

| Metric                          | Target                          | Measurement |
|---------------------------------|---------------------------------|-------------|
| Dashboard load (typical brand)  | p95 ≤ 2.5 s, p99 ≤ 4 s         | k6 / Playwright |
| Detection job (mock-heavy)      | Completes ≤ 15 s                | Backend timing |
| Concurrent users                | 10 simultaneous analysts        | k6 script |
| API list detections             | p95 ≤ 800 ms                    | k6 |

**Load Test Scenarios**
- 10 virtual users continuously browsing dashboard + filtering
- Burst of 5 concurrent detection triggers on the same brand
- Sustained 30 requests/second on read endpoints for 2 minutes

**Tools:** k6 (preferred for simplicity) or Locust

---

## 3. Test Data Management & Environment Strategy

### 3.1 Environments

| Environment     | Purpose                              | Data Strategy                  | Lifetime |
|-----------------|--------------------------------------|--------------------------------|----------|
| Local           | Developer machines                   | Docker Compose + seed script   | Persistent per developer |
| CI Ephemeral    | Automated test runs                  | Testcontainers + factory data  | Destroyed after job |
| Staging / Demo  | Manual testing & presentation        | Fixed high-quality seed data   | Stable during hackathon |
| Production      | Out of scope for MVP                 | —                              | — |

### 3.2 Test Data Principles
- **Deterministic seed data** for Staging/Demo: 1–2 well-known brands (e.g., Nike, Acme Corp) + 40–60 realistic detections with known risk scores.
- **Factory / Builder pattern** for CI and unit/integration tests (using `factory_boy` or custom builders).
- Official assets are explicitly marked and must be excluded in every relevant test.
- Look-alike variants are generated programmatically in tests so that new rules can be verified quickly.
- No real PII or production credentials in any test data.

### 3.3 Seed Data Requirements (Staging)
- At least one brand with complete official social accounts and apps
- Mix of high / medium / low risk detections
- Examples of character-swap, added-word, and spacing look-alikes
- At least one detection that should be excluded (official asset)
- Pre-calculated expected risk scores for assertion

---

## 4. Defect Life Cycle & Severity / Priority Matrix

### 4.1 Severity Definitions

| Severity | Definition                                                                 | Example |
|----------|----------------------------------------------------------------------------|-------|
| **S1 – Critical** | System unusable or core value proposition broken                           | Official assets appear in detection results; detection job crashes; login completely broken |
| **S2 – Major**    | Major feature impaired; workaround difficult or non-existent               | Risk scores completely wrong; dashboard fails to load; cannot mark status |
| **S3 – Minor**    | Feature works but with noticeable issues; workaround exists                | Incorrect sorting; missing signal breakdown; UI alignment issues |
| **S4 – Trivial**  | Cosmetic or very low impact                                                | Typo, minor styling inconsistency |

### 4.2 Priority Definitions & SLA (Hackathon Context)

| Priority | Meaning                                      | Target Resolution (Hackathon) |
|----------|----------------------------------------------|-------------------------------|
| **P0**   | Blocks demo or core scoring criteria         | Fix within 2–4 hours          |
| **P1**   | High impact on user experience or detection quality | Fix within 8 hours / same day |
| **P2**   | Medium impact; can be deferred if needed     | Best effort before final demo |
| **P3**   | Low impact / nice-to-have                    | Backlog                       |

**Mapping Guidance**
- Any S1 → automatically P0
- Official asset exclusion failure → always P0
- Look-alike detection completely missing → P0/P1
- Cosmetic UI issues → P2/P3

### 4.3 Defect Life Cycle
```
New → Triaged (Severity + Priority assigned) → In Progress → In Review → Resolved → Verified → Closed
```
- All P0/P1 defects must be verified by a second person before closing.
- Regression test case must be added for every P0/P1 bug that is fixed.

---

## 5. CI/CD Automated Test Pipeline Execution Stages

### 5.1 Pipeline Stages (Recommended GitHub Actions)

```
1. Lint & Static Analysis
   - Backend: ruff + mypy
   - Frontend: ESLint + TypeScript check
   - Fail fast on style / type errors

2. Unit Tests
   - Backend: pytest --cov (fail if < 70%)
   - Frontend: vitest --coverage (fail if < 60%)
   - Parallel execution

3. Integration Tests
   - Spin up PostgreSQL via Testcontainers
   - Run API + service integration suite
   - Official asset exclusion tests mandatory

4. Contract / API Schema Tests
   - Validate responses against OpenAPI schema
   - Or use schemathesis / dredd-style checks

5. Build Artifacts
   - Docker image for backend
   - Frontend production build

6. E2E Tests (on staging or ephemeral environment)
   - Playwright suite against critical paths
   - Run only on main branch or release candidates (to save time)

7. Performance Smoke (optional, nightly or pre-demo)
   - Lightweight k6 script
```

### 5.2 Branch Protection Rules
- `main` requires:
  - All unit + integration tests green
  - Coverage thresholds met
  - At least one approving review
- Feature branches can run a lighter suite for speed

### 5.3 Test Reporting
- Coverage reports published as CI artifacts
- Playwright HTML report retained for failed E2E runs
- Slack / Discord notification on pipeline failure (optional)

---

## 6. Risk-Based Testing Focus (Hackathon Priorities)

| Risk Area                        | Testing Emphasis                     | Why |
|----------------------------------|--------------------------------------|-----|
| Official asset exclusion         | Exhaustive automated + manual        | Instant demo failure if broken |
| Look-alike name detection        | Large unit test matrix               | Bonus points + differentiation |
| Risk score correctness           | Table-driven unit + integration      | Core value of the product |
| Dashboard prioritization         | E2E + visual checks                  | First thing judges see |
| Graceful degradation             | Integration with mocked failures     | UX criterion (15%) |
| Auth & ownership                 | Integration + negative tests         | Security baseline |

---

## 7. Entry & Exit Criteria

**Entry Criteria for Testing a Feature**
- Code complete and peer-reviewed
- Unit tests written by developer
- Feature available on a testable environment
- Seed / factory data ready

**Exit Criteria for MVP Release / Demo**
- All P0 and P1 defects closed
- Critical path E2E suite 100% green
- Official asset exclusion verified
- Staging environment stable for at least 2 hours before presentation
- Test summary report shared with the team

---

**Document Control**  
This Test Strategy ensures that the BrandGuard MVP meets the high bar required for Social Media Monitoring (30%), App Store Monitoring (30%), Brand Profile (15%), User Experience (15%), and Presentation (10%) evaluation criteria, while protecting the team from last-minute quality surprises.

**Recommended Next Artifacts**
- Concrete test case spreadsheet / TestRail import for critical paths
- pytest and Playwright starter templates
- Seed data JSON / factory definitions
- k6 performance script skeleton

---
*End of Test Strategy & Quality Assurance Plan*
```
