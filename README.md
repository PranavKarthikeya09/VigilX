# vigilX — Digital Risk Protection Platform

**Detect. Analyse. Protect.**

vigilX is a Digital Risk Protection (DRP) platform designed to identify
potential brand impersonation across social media and mobile application
stores.

As businesses establish their online presence, malicious actors can create
lookalike social profiles, fraudulent applications, and misleading accounts
to impersonate legitimate brands. These threats can damage brand reputation,
mislead customers, and potentially facilitate phishing and other scams.

vigilX aims to help identify these threats by analysing brand names, visual
similarities, account information, and application metadata to calculate
explainable risk scores.

The project is being developed as a student-built MVP, with an emphasis on
modular architecture, deterministic detection algorithms, and testable
risk-scoring logic.

---

## Table of Contents

- [Overview](#overview)
- [Key Capabilities](#key-capabilities)
- [How It Works](#how-it-works)
- [Technology Stack](#technology-stack)
- [Architecture](#architecture)
- [Repository Structure](#repository-structure)
- [Getting Started](#getting-started)
- [Running the Backend](#running-the-backend)
- [Running the Frontend](#running-the-frontend)
- [Testing](#testing)
- [API Endpoints](#api-endpoints)
- [Team and Development Workflow](#team-and-development-workflow)
- [Project Roadmap](#project-roadmap)
- [Security Considerations](#security-considerations)
- [Limitations](#limitations)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

vigilX focuses on two primary threat categories.

### 1. Social Media Impersonation

Identifies potentially suspicious social profiles that imitate legitimate
brands through similar names, suspicious account identifiers, and visual
similarities.

Examples include:
- Lookalike brand names.
- Suspicious combinations of brand names and impersonation-related terms.
- Profiles with logos resembling those of legitimate brands.
- Accounts requiring further investigation based on combined risk signals.

### 2. Mobile Application Impersonation

Evaluates mobile applications that may be impersonating legitimate brands.

Potential indicators include:
- Similar application titles.
- Similar application icons.
- Mismatched developer or publisher information.
- Suspicious application descriptions.
- Combinations of multiple impersonation signals.

The goal is to provide structured, explainable risk assessments that help
prioritise suspicious candidates for further investigation.

---

## Key Capabilities

The project is being developed around the following capabilities.

| Capability | Description |
|---|---|
| Brand registration | Register a brand and manage its identifying information. |
| Official asset management | Associate legitimate social accounts and mobile applications with a brand. |
| Lookalike name analysis | Generate and evaluate potentially deceptive brand-name variations. |
| String similarity | Compare candidate names against official brand names. |
| Logo similarity | Compare perceptual hashes of candidate and official logos. |
| Risk scoring | Combine detection signals into a normalised risk score. |
| Risk classification | Categorise evaluated candidates as low, medium, or high risk. |
| Authentication | Verify Supabase-issued JWTs on protected backend routes. |
| API health monitoring | Expose health and readiness endpoints for service monitoring. |
| Automated testing | Test backend behaviour, detection algorithms, and scoring rules. |

**Implementation note:** The capabilities above describe the project's
overall scope. Individual features may reside on separate development
branches and should not be assumed to be integrated into the default branch
until verified.

---

## How It Works

The intended detection workflow is organised into several stages.

### Step 1 — Register a Brand

A user registers a brand and supplies relevant identifying information,
including its name and official assets.

### Step 2 — Establish Official Assets

Official social accounts and mobile applications provide reference
information against which potential impersonators can be evaluated.

### Step 3 — Generate and Evaluate Candidates

Candidate profiles and applications are evaluated using the detection
signals available to the system.

The initial MVP supports deterministic algorithmic evaluation and can use
mock candidate data for testing.

### Step 4 — Calculate Similarity Signals

The detection engine evaluates relevant attributes, including:

- Name similarity.
- Logo perceptual-hash similarity.
- Bio or description similarity.
- Lookalike-name indicators.
- Application publisher mismatch.

### Step 5 — Calculate Risk Scores

Individual signals are combined using predefined weights to calculate
a score between 0 and 100.

### Step 6 — Classify Risk

Candidates are assigned a risk level based on their calculated score.

| Risk Level | Score |
|---|---:|
| High | 75–100 |
| Medium | 50–74.99 |
| Low | 0–49.99 |

A high score indicates stronger similarity or suspicion under the configured
rules. It does not, by itself, establish that an account or application is
malicious.

### Step 7 — Support Further Investigation

The intended system uses detection results and supporting signals to help
users prioritise candidates for review.

Official-asset exclusion rules are also important: known legitimate accounts
and applications must not be incorrectly classified as impersonators merely
because they share a brand's identity.

---

## Technology Stack

### Frontend

| Technology | Purpose |
|---|---|
| React | User interface |
| TypeScript | Type-safe frontend development |
| Vite | Development server and build tooling |
| Tailwind CSS | Styling |
| Lucide React | Icons |
| Axios | HTTP communication with the backend |
| Supabase JavaScript Client | Supabase integration |

### Backend

| Technology | Purpose |
|---|---|
| Python 3.13 | Backend development |
| FastAPI | REST API framework |
| Pydantic v2 | Request and response validation |
| SQLAlchemy 2.0 | Database access and ORM |
| Alembic | Database migrations |
| PyJWT and Cryptography | JWT verification |
| RapidFuzz | String similarity calculations |
| ImageHash | Perceptual image hashing |
| Pillow | Image processing |

### Infrastructure and Data

| Technology | Purpose |
|---|---|
| Supabase PostgreSQL | Managed relational database |
| Supabase Auth | Authentication and JWT issuance |
| Supabase Storage | Planned official-logo storage integration |

### Testing

- pytest — backend testing.
- Vitest — frontend testing.
- Playwright — end-to-end testing.

---

## Architecture

vigilX follows a frontend/backend architecture.

```text
                    ┌──────────────────────────┐
                    │        User              │
                    └────────────┬─────────────┘
                                 │
                                 ▼
                    ┌──────────────────────────┐
                    │     React Frontend       │
                    │   TypeScript + Vite      │
                    └────────────┬─────────────┘
                                 │
                           HTTP / REST API
                                 │
                                 ▼
                    ┌──────────────────────────┐
                    │      FastAPI Backend     │
                    │                          │
                    │  Authentication          │
                    │  Brand and Asset APIs    │
                    │  Request Validation      │
                    └────────────┬─────────────┘
                                 │
                                 ▼
                    ┌──────────────────────────┐
                    │    Detection Services    │
                    │                          │
                    │  Name Similarity         │
                    │  Lookalike Detection     │
                    │  Logo Similarity         │
                    │  Risk Scoring            │
                    └────────────┬─────────────┘
                                 │
                                 ▼
                    ┌──────────────────────────┐
                    │    Supabase PostgreSQL   │
                    │                          │
                    │  Brands                  │
                    │  Official Assets         │
                    │  Detections              │
                    │  Detection Evidence      │
                    └──────────────────────────┘
```

The diagram represents the intended system architecture. The completeness
of each integration depends on the features available in the branch being
used.

FastAPI owns backend business logic and detection processing. The React
frontend communicates with the backend through HTTP APIs.

---

## Repository Structure

```text
VigilX/
├── backend/
│   ├── alembic/
│   │   └── versions/          # Database migration files
│   ├── app/
│   │   ├── api/
│   │   │   └── v1/             # Versioned API routes
│   │   ├── core/               # Configuration and security
│   │   ├── db/                 # Database configuration
│   │   ├── models/             # SQLAlchemy models
│   │   ├── schemas/            # Pydantic schemas
│   │   ├── services/           # Detection and scoring services
│   │   └── main.py             # FastAPI application
│   ├── tests/                  # Backend tests
│   ├── .env.example            # Backend configuration template
│   ├── pytest.ini
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── services/           # API and Supabase clients
│   │   ├── App.tsx
│   │   └── index.css
│   ├── .env.example            # Frontend configuration template
│   └── package.json
│
├── docs/
│   ├── team/                   # Team briefs and specifications
│   └── BrandGuard_TDD.md       # Technical design reference
│
├── .gitignore
└── README.md
```

Some directories and files may differ between branches as development
continues.

---

## Getting Started

### Prerequisites

Install the following tools before starting development:

- Python 3.13.
- Node.js and npm.
- Git.
- Access to a Supabase project if using the hosted database and authentication
  services.

On macOS, you can install the development tools using Homebrew:

```bash
brew install python@3.13 node git
```

If Python 3.13 is already installed, you do not need to install it again.

Verify the installations:

```bash
python3.13 --version
node --version
npm --version
git --version
```

### 1. Clone the Repository

```bash
git clone https://github.com/PranavKarthikeya09/VigilX.git
cd VigilX
```

### 2. Select a Branch

To work with the integration branch:

```bash
git switch master
git pull origin master
```

To work with the detection-engine implementation:

```bash
git fetch origin
git switch --track origin/feature/engine-similarity-algorithms
```

If the feature branch already exists locally, switch to it with:

```bash
git switch feature/engine-similarity-algorithms
git pull
```

Use the branch that contains the features you intend to test.

---

## Running the Backend

### 1. Enter the Backend Directory

```bash
cd backend
```

### 2. Create a Virtual Environment

```bash
python3.13 -m venv .venv
source .venv/bin/activate
```

Your terminal should now indicate that the virtual environment is active.

### 3. Install Dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a local environment file from the provided template:

```bash
cp .env.example .env
```

The backend uses the following configuration variables:

| Variable | Purpose |
|---|---|
| `PROJECT_NAME` | Application name |
| `ENVIRONMENT` | Execution environment |
| `DATABASE_URL` | Database connection string |
| `SUPABASE_URL` | Supabase project URL |
| `SUPABASE_JWT_ALLOWED_ALGORITHMS` | Allowed JWT signing algorithms |
| `SUPABASE_SERVICE_ROLE_KEY` | Backend-only Supabase service-role credential |
| `SUPABASE_STORAGE_BUCKET` | Storage bucket configuration |
| `CORS_ORIGINS` | Allowed frontend origins |

The supplied template includes an SQLite configuration suitable for local
development and testing. Configure valid Supabase credentials when using
hosted services.

**Never commit your actual `.env` file or expose service-role keys in the
frontend.**

### 5. Run Database Migrations

When the configured database is available:

```bash
alembic upgrade head
```

Use the migration command only after configuring the appropriate database.

### 6. Start the Backend

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

The backend will be available at:

- API base: `http://127.0.0.1:8000`
- Swagger documentation: `http://127.0.0.1:8000/docs`
- ReDoc documentation: `http://127.0.0.1:8000/redoc`
- Health check: `http://127.0.0.1:8000/health`
- Readiness check: `http://127.0.0.1:8000/ready`

The health endpoint checks whether the application is running. The readiness
endpoint also checks database connectivity.

---

## Running the Frontend

Open a second terminal.

### 1. Enter the Frontend Directory

From the repository root:

```bash
cd frontend
```

### 2. Install Dependencies

```bash
npm install
```

### 3. Configure Environment Variables

Create the local environment file:

```bash
cp .env.example .env.local
```

Configure the variables:

```dotenv
VITE_SUPABASE_URL=https://your-project-ref.supabase.co
VITE_SUPABASE_ANON_KEY=your-supabase-anon-key
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

Replace the example values with the appropriate project configuration.

Only public client-side credentials intended for browser use should be
included in frontend environment variables.

Never place a Supabase service-role key or other server-side secret in
a variable prefixed with `VITE_`.

### 4. Start the Development Server

```bash
npm run dev
```

Vite will display the local development URL, normally:

`http://localhost:5173`

Keep the backend running in the other terminal.

---

## Testing

Testing is important for validating both the existing application and
the detection-engine implementation.

### Backend Tests

From the `backend` directory, with the virtual environment activated:

```bash
python -m pytest -v
```

To run the detection-engine tests specifically:

```bash
python -m pytest tests/test_lookalike.py tests/test_scoring.py -v
```

These detection-specific files are available on the feature branch that
implements the corresponding services. Their presence on another branch
must be verified before running the command.

### Frontend Build Validation

From the `frontend` directory:

```bash
npm run build
```

This runs the TypeScript build checks and creates a production build.

### What Should Be Tested?

The detection-engine tests should cover:

- Identical and unrelated names.
- Character substitutions and lookalike variations.
- Empty and missing input values.
- Invalid perceptual hashes.
- Similar and dissimilar logo hashes.
- Risk-scoring weights and calculations.
- Publisher-mismatch behaviour.
- Risk-level threshold boundaries.
- Invalid numeric values, including non-finite numbers.
- Deterministic results across repeated executions.

Run the relevant tests before submitting changes for review.

---

## API Endpoints

The backend currently defines the following health and authentication-related
routes, along with versioned brand routes.

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | Check application liveness |
| GET | `/ready` | Check application and database readiness |
| GET | `/api/v1/auth/me` | Authentication-related user endpoint |

The backend also mounts versioned brand routes under `/api/v1`.

For the exact brand endpoints, request schemas, and authentication
requirements, inspect the route implementation or the generated API
documentation at `/docs`.

This table intentionally lists only selected endpoints; it is not a
complete API specification.

---

## Risk-Scoring Model

The detection engine combines multiple signals into a single score.

### Social Profile Scoring

| Signal | Weight |
|---|---:|
| Name similarity | 40% |
| Logo similarity | 30% |
| Bio similarity | 15% |
| Lookalike signal | 15% |
| **Total** | **100%** |

Formula:

```text
Social Risk Score =
    (0.40 × Name Similarity
   + 0.30 × Logo Similarity
   + 0.15 × Bio Similarity
   + 0.15 × Lookalike Signal) × 100
```

### Mobile Application Scoring

| Signal | Weight |
|---|---:|
| Title similarity | 30% |
| Publisher mismatch | 30% |
| Logo similarity | 20% |
| Description similarity | 10% |
| Lookalike signal | 10% |
| **Total** | **100%** |

Formula:

```text
Application Risk Score =
    (0.30 × Title Similarity
   + 0.30 × Publisher Mismatch
   + 0.20 × Logo Similarity
   + 0.10 × Description Similarity
   + 0.10 × Lookalike Signal) × 100
```

Each input signal is normalised to the range 0–1.

Missing-value rules are part of the scoring contract. For example, missing
logo similarity contributes zero, while a missing candidate developer uses
the configured publisher-mismatch default of 0.75.

Risk scores are rounded to two decimal places before classification.

The scoring model is heuristic and should not be interpreted as a definitive
determination of malicious activity.

---

## Team and Development Workflow

vigilX is developed by a four-person team with separate responsibilities.

| Role | Responsibility | Branch |
|---|---|---|
| Person 1 | Backend APIs and official brand assets | `feature/backend-brand-assets` |
| Person 2 | Similarity algorithms and risk scoring | `feature/engine-similarity-algorithms` |
| Person 3 | Frontend brand onboarding | `feature/frontend-brand-profile` |
| Person 4 | QA, integration, and exclusion invariants | `test/qa-invariance-suite` |

### Development Guidelines

1. Work on your assigned branch.
2. Keep commits focused on the relevant feature.
3. Run the tests associated with your changes.
4. Coordinate interface changes with the responsible team member.
5. Review changes before merging them into `master`.
6. Do not force-push or rewrite shared Git history.
7. Never commit credentials or environment files.

### Suggested Git Workflow

```bash
git status
git switch feature/your-branch
git pull
```

After making changes:

```bash
git status
git add <specific-files>
git commit -m "Describe the change"
git push origin feature/your-branch
```

Submit a pull request for review when the implementation and relevant tests
are ready.

---

## Project Roadmap

The following items describe the intended development direction, not a
guarantee that every item is already implemented.

- [x] Initial frontend and backend project scaffold.
- [x] FastAPI application and versioned route structure.
- [x] Initial database models and migration structure.
- [x] JWT verification and authentication-related backend functionality.
- [x] Health and readiness endpoints.
- [x] Initial deterministic lookalike and risk-scoring services on the
      detection-engine feature branch.
- [ ] Complete integration of detection services with the backend API.
- [ ] Validate official-asset exclusion invariants across the detection
      workflow.
- [ ] Integrate candidate evaluation and persistence.
- [ ] Complete end-to-end verification across frontend and backend.
- [ ] Expand detection coverage and evaluate false positives and false
      negatives.
- [ ] Integrate external data sources where appropriate.
- [ ] Improve deployment, monitoring, and operational reliability.

The checked items describe implementation milestones recorded by the team.
Verify the relevant branch and tests before treating a milestone as part of
a particular release.

---

## Security Considerations

Security is an important part of a brand-protection platform.

- Keep service-role credentials on the backend.
- Never commit `.env` or `.env.local` files.
- Verify authentication tokens before granting access to protected resources.
- Restrict CORS origins to the required frontend domains in deployment.
- Validate incoming request data.
- Avoid exposing stack traces or internal secrets in production responses.
- Ensure that users can access only the brand resources they are authorised
  to manage.
- Never exclude a suspicious candidate based solely on its display name or
  claimed developer identity.

Before deploying publicly, verify authentication, authorisation, database
permissions, CORS configuration, and secret management.

---

## Limitations

vigilX is an evolving MVP, not a production-grade threat intelligence
platform.

Current algorithmic approaches have several limitations:

- Name similarity does not prove malicious intent.
- Perceptual-hash similarity can be affected by image transformations.
- Heuristic lookalike rules may produce false positives or false negatives.
- Risk scores depend on the quality and availability of input signals.
- Mock candidates do not represent comprehensive real-world threat coverage.
- Live social-media and app-store integrations must not be assumed unless
  explicitly implemented and configured.
- Automated tests validate defined behaviours but cannot establish that every
  real-world impersonation attempt will be detected.

The project should be evaluated as an extensible foundation for digital
brand-protection workflows.

---

## Contributing

Contributions and feedback are welcome.

Before submitting changes:

1. Check the relevant team implementation brief.
2. Follow the assigned branch workflow.
3. Keep changes focused and reviewable.
4. Add or update tests where appropriate.
5. Run relevant tests and build checks.
6. Document configuration or interface changes.
7. Submit a pull request for review.

For project-specific development details, refer to the documentation in
[`docs/team/`](docs/team/).

---

## License

No license has been specified in this README.

Please refer to the repository's license file, if present, for the applicable
terms of use and distribution.
