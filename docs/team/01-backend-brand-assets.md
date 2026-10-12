# Implementation Brief 01: Backend Brand & Official-Asset API

* **Assigned Team Member:** Person 1 (Backend & API)
* **Assigned Git Branch:** `feature/backend-brand-assets`
* **Parent Branch:** `origin/master` (Commit `8840f59`)

---

## 1. Objective
Build the backend Pydantic v2 validation contracts and FastAPI REST endpoints to allow authenticated users to create and manage Brand Profiles and register official assets (Social Accounts and Mobile App Store listings). All records must be persisted to the PostgreSQL database with strict user ownership and input normalization.

---

## 2. Exact Initial Files to Inspect (Source of Truth)

1. **[`backend/app/models/brand.py`](file:///c:/Users/PRANAV%20KARTHIKEYA/OneDrive/Desktop/VigilX/backend/app/models/brand.py):**
   * Columns: `id` (UUID), `owner_id` (UUID FK to `users.id`), `name` (String 255), `normalized_name` (String 255), `logo_url` (Text, nullable), `logo_phash` (String 64, nullable), `website` (String 512, nullable), `created_at`, `updated_at`.
   * **Crucial Schema Reality:** The `Brand` table does **not** have a `description` column. Do not add `description` to request/response schemas or database models.
2. **[`backend/app/models/official_asset.py`](file:///c:/Users/PRANAV%20KARTHIKEYA/OneDrive/Desktop/VigilX/backend/app/models/official_asset.py):**
   * `OfficialSocialAccount`: `id`, `brand_id`, `platform` (String 50), `handle` (String 255), `raw_handle` (String 255), `url` (Text, nullable), `is_verified` (Boolean, default False).
   * **Constraint:** UniqueConstraint `("brand_id", "platform", "handle", name="uq_official_social_brand_platform_handle")`.
   * `OfficialApp`: `id`, `brand_id`, `name` (String 255), `package_id` (String 255, nullable), `developer_name` (String 255, **required**), `store` (String 50, e.g. `'google_play'`, `'app_store'`), `store_url` (Text, nullable), `logo_url` (Text, nullable).
3. **[`backend/app/core/security.py`](file:///c:/Users/PRANAV%20KARTHIKEYA/OneDrive/Desktop/VigilX/backend/app/core/security.py):**
   * Dependency `get_current_user`: Validates Supabase ES256 Bearer JWT and returns the synchronized `User` ORM instance.
4. **[`backend/app/schemas/common.py`](file:///c:/Users/PRANAV%20KARTHIKEYA/OneDrive/Desktop/VigilX/backend/app/schemas/common.py):**
   * Common contracts: `PaginatedResponse[T]`, `PaginationMeta`, `StandardErrorResponse`.
5. **[`backend/app/main.py`](file:///c:/Users/PRANAV%20KARTHIKEYA/OneDrive/Desktop/VigilX/backend/app/main.py):**
   * Router mounting pattern (`app.include_router(..., prefix="/api/v1")`).

---

## 3. Expected Files to Create or Modify

* **Create:** `backend/app/schemas/brand.py`
* **Create:** `backend/app/schemas/official_asset.py`
* **Create:** `backend/app/api/v1/brands.py`
* **Create:** `backend/tests/test_api_brands.py`
* **Modify:** `backend/app/main.py` (mount `brands.router`)

---

## 4. Dependencies & Interfaces

### A. Authentication & DB Sessions
Every brand endpoint must enforce:
```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import get_current_user
from app.db.session import get_db
from app.models.user import User

router = APIRouter(prefix="/brands", tags=["Brand Profiles"])

# Pattern for endpoints
async def my_endpoint(
    brand_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    ...
```

### B. Ownership Helper
Encapsulate ownership validation:
```python
async def get_user_brand(brand_id: uuid.UUID, user_id: uuid.UUID, db: AsyncSession) -> Brand:
    brand = await db.get(Brand, brand_id)
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")
    if brand.owner_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to access this brand")
    return brand
```

### C. Normalization Rules
1. **Brand Normalization:** `normalized_name = name.strip().lower()`.
2. **Social Handle Normalization:**
   * `raw_handle` = user input as provided (e.g., `"@Nike"`).
   * `handle` = normalized identifier: `raw_handle.lstrip("@").strip().lower()`.
   * When checking `uq_official_social_brand_platform_handle`, query by normalized `handle`.

---

## 5. API Request & Response Contracts

### 5.1 Brand Endpoints

#### `POST /api/v1/brands`
* **Request (`BrandCreate`):**
  ```json
  {
    "name": "Nike",
    "website": "https://www.nike.com",
    "logo_url": "https://example.com/logo.png"
  }
  ```
* **Response (`201 Created` — `BrandResponse`):**
  ```json
  {
    "id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
    "owner_id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "Nike",
    "normalized_name": "nike",
    "website": "https://www.nike.com",
    "logo_url": "https://example.com/logo.png",
    "logo_phash": null,
    "created_at": "2026-10-12T08:00:00Z",
    "updated_at": "2026-10-12T08:00:00Z"
  }
  ```

#### `GET /api/v1/brands`
* **Query Parameters:** `page: int = 1`, `page_size: int = 20`
* **Response (`200 OK` — `PaginatedResponse[BrandResponse]`):**
  ```json
  {
    "items": [ ... ],
    "pagination": {
      "page": 1,
      "page_size": 20,
      "total_items": 1,
      "total_pages": 1
    }
  }
  ```

#### `GET /api/v1/brands/{brand_id}`
* **Response (`200 OK` — `BrandDetailResponse`):**
  Includes brand attributes plus count or summary of registered official assets.

---

### 5.2 Official Social Account Endpoints

#### `POST /api/v1/brands/{brand_id}/social-accounts`
* **Request (`OfficialSocialAccountCreate`):**
  ```json
  {
    "platform": "x",
    "raw_handle": "@Nike",
    "url": "https://x.com/Nike",
    "is_verified": true
  }
  ```
* **Validation:**
  * `platform` must be one of: `'x'`, `'instagram'`, `'facebook'`, `'linkedin'`, `'tiktok'`.
  * If `(brand_id, platform, handle)` exists, raise `HTTPException(409, "Official social account already registered for this platform and handle")`.
* **Response (`201 Created` — `OfficialSocialAccountResponse`):**
  ```json
  {
    "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "brand_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
    "platform": "x",
    "handle": "nike",
    "raw_handle": "@Nike",
    "url": "https://x.com/Nike",
    "is_verified": true,
    "created_at": "2026-10-12T08:05:00Z"
  }
  ```

#### `GET /api/v1/brands/{brand_id}/social-accounts`
* **Response (`200 OK`):** `List[OfficialSocialAccountResponse]`

#### `DELETE /api/v1/brands/{brand_id}/social-accounts/{account_id}`
* **Response (`204 No Content`)**

---

### 5.3 Official Mobile App Endpoints

#### `POST /api/v1/brands/{brand_id}/apps`
* **Request (`OfficialAppCreate`):**
  ```json
  {
    "name": "Nike: Shoes & Apparel",
    "package_id": "com.nike.omega",
    "developer_name": "Nike, Inc.",
    "store": "google_play",
    "store_url": "https://play.google.com/store/apps/details?id=com.nike.omega",
    "logo_url": null
  }
  ```
* **Validation:**
  * `store` must be `'google_play'` or `'app_store'`.
  * `developer_name` is mandatory (non-empty string).
* **Response (`201 Created` — `OfficialAppResponse`):**
  ```json
  {
    "id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
    "brand_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
    "name": "Nike: Shoes & Apparel",
    "package_id": "com.nike.omega",
    "developer_name": "Nike, Inc.",
    "store": "google_play",
    "store_url": "https://play.google.com/store/apps/details?id=com.nike.omega",
    "logo_url": null,
    "created_at": "2026-10-12T08:10:00Z"
  }
  ```

#### `GET /api/v1/brands/{brand_id}/apps`
* **Response (`200 OK`):** `List[OfficialAppResponse]`

#### `DELETE /api/v1/brands/{brand_id}/apps/{app_id}`
* **Response (`204 No Content`)**

---

## 6. Acceptance Criteria

1. **Brand Isolation:** User A cannot view, update, or delete Brand B owned by User B (`403 Forbidden`).
2. **Schema Fidelity:** `Brand` schema contains no `description` field.
3. **Handle Normalization:** User inputs `@BrandName` $\rightarrow$ stored as `raw_handle="@BrandName"` and `handle="brandname"`.
4. **App Validation:** Missing `developer_name` or invalid `store` triggers `422 Unprocessable Entity`.
5. **Conflict Handling:** Duplicate social account per `(brand_id, platform, handle)` returns `409 Conflict`.
6. **Error Format:** All errors return JSON matching `StandardErrorResponse`.

---

## 7. Required Tests to Implement & Run

Create `backend/tests/test_api_brands.py` using `httpx.AsyncClient` and authentication override fixtures:
* `test_create_brand_success`: Verify 201 response and DB persistence.
* `test_create_brand_unauthorized`: Missing token returns 401.
* `test_get_brand_forbidden_other_user`: User A gets 403 trying to view User B's brand.
* `test_add_social_account_normalization`: `@Nike` normalizes to `nike`.
* `test_add_social_account_duplicate_conflict`: Returns 409 on second identical post.
* `test_add_official_app_requires_developer_name`: Blank developer name returns 422.
* `test_delete_asset_cascade`: Deleting an asset removes it from the list.

### Test Execution Command:
```powershell
.\backend\.venv\Scripts\pytest backend\tests\test_api_brands.py -v
```

---

## 8. Explicitly Out-of-Scope Work for This Task

* Do **not** create or mount detection routes (`/detections`, `/summary`, `/run`).
* Do **not** alter database tables, SQLAlchemy models, or Alembic migrations.
* Do **not** implement file uploads for logos (use plain URL strings).
