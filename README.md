# vigilX — Digital Risk Protection Platform

**vigilX** is a Digital Risk Protection (DRP) platform designed to discover, evaluate, and prioritize brand impersonation threats across **Social Media** and **Mobile App Stores**.

---

## 1. Architecture Overview

* **Frontend:** React 19, TypeScript, Vite, Tailwind CSS, Lucide Icons.
* **Backend:** Python 3.13 / FastAPI, Pydantic v2, SQLAlchemy 2.0 (Async), Alembic.
* **Managed Infrastructure:** Supabase PostgreSQL, Supabase Auth (JWT), Supabase Storage.
* **Detection Engine:** RapidFuzz, ImageHash (perceptual hashing), Custom Look-alike Rules.
* **Testing:** Pytest (Async backend), Vitest (Frontend), Playwright (E2E).

---

## 2. Repository Structure

```
vigilX/
├── docs/                           # Project requirements, specs, and briefs
├── backend/
│   ├── alembic/                    # Database migrations
│   │   └── versions/001_initial_schema.py
│   ├── app/
│   │   ├── api/v1/                 # Endpoints (/health, /ready, /api/v1/auth/me)
│   │   ├── core/                   # Security, JWT verification, Pydantic Settings
│   │   ├── db/                     # Base and Async Sessionmaker
│   │   ├── models/                 # SQLAlchemy 2.0 models (User, Brand, Assets, Detection)
│   │   ├── schemas/                # Pydantic v2 validation contracts
│   │   └── main.py                 # FastAPI application
│   ├── tests/                      # Pytest test suite (health, security, models)
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── services/               # Supabase JS and Axios API client
│   │   ├── App.tsx                 # Core UI with live health indicators
│   │   └── index.css               # Tailwind design tokens
│   ├── package.json
│   └── .env.example
├── .gitignore                      # Secrets and artifact exclusions
└── README.md
```

---

## 3. Quickstart & Local Setup

### 3.1 Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create and activate Python virtual environment
python -m venv .venv
# On Windows PowerShell:
.\.venv\Scripts\Activate.ps1
# On Linux/macOS:
# source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
copy .env.example .env
# Edit .env with your Supabase credentials or use the local default

# Run schema migrations
alembic upgrade head

# Run unit tests
pytest -v

# Start the development server
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Backend endpoints will be available at:
* Liveness probe: `http://127.0.0.1:8000/health`
* Readiness probe: `http://127.0.0.1:8000/ready`
* Interactive API Documentation (Swagger): `http://127.0.0.1:8000/docs`

---

### 3.2 Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install Node dependencies
npm install

# Configure environment variables
copy .env.example .env.local

# Run production build validation
npm run build

# Start the Vite development server
npm run dev
```

Frontend will run at `http://localhost:5173`.

---

## 4. Milestone 1 Verification Status

* [x] **Monorepo Scaffold:** Created with `backend`, `frontend`, `docs`, `tests`, `.gitignore`, `README.md`.
* [x] **Frontend Production Build:** Verified clean build with zero TypeScript or bundling errors.
* [x] **Backend Architecture:** FastAPI, Pydantic v2, SQLAlchemy 2.0 async session, and Alembic configured.
* [x] **Database Schema:** Initial schema migration (`001_initial_schema.py`) created and verified with all core tables (`users`, `brands`, `official_social_accounts`, `official_apps`, `detections`, `detection_evidence`).
* [x] **Security & Auth:** Supabase JWT verification implemented with claims validation, JIT user synchronization, and secret isolation.
* [x] **Health Endpoints:** `/health` and `/ready` tested live with HTTP 200 responses.
* [x] **Automated Tests:** 8/8 backend tests passing in `pytest` covering health, readiness, JWT authentication (expired, invalid signature, valid), and database model persistence.
* [x] **Secret Protection:** `.env` files, credentials, and local databases strictly excluded in `.gitignore`.
