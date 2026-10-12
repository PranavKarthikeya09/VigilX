# API Specification & Contract
## BrandGuard – Digital Risk Protection Platform
### Social & App Monitoring

**Document Version:** 1.0  
**Date:** 12 October 2026  
**Author:** Lead Backend Engineer  
**Status:** Draft for Hackathon MVP  
**Related Documents:** BrandGuard PRD v1.0, BrandGuard TDD v1.0

---

## 1. General API Conventions

### 1.1 Base URL & Versioning
```
Production / Staging : https://api.brandguard.example.com/api/v1
Local Development    : http://localhost:8000/api/v1
```

All endpoints are versioned under `/api/v1`. Breaking changes will be introduced under `/api/v2`.

### 1.2 Standard HTTP Headers

| Header            | Required | Description |
|-------------------|----------|-----------|
| `Authorization`   | Yes*     | `Bearer <JWT access token>` (*except login & health endpoints) |
| `Content-Type`    | Yes      | `application/json` for request bodies |
| `Accept`          | No       | `application/json` (default) |
| `X-Request-ID`    | No       | Client-generated UUID for request tracing. If missing, server generates one. |
| `X-Brand-ID`      | No       | Optional convenience header; brand ownership is still enforced via path/ownership checks |

### 1.3 Standard Error Response Format

All error responses follow this JSON schema:

```json
{
  "status": 400,
  "error_code": "VALIDATION_ERROR",
  "message": "Request validation failed",
  "details": [
    {
      "field": "name",
      "issue": "Field required"
    }
  ],
  "request_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "timestamp": "2026-10-12T07:30:00Z"
}
```

**Common Error Codes**

| HTTP Status | error_code              | When |
|-------------|-------------------------|------|
| 400         | VALIDATION_ERROR        | Invalid request body / query params |
| 401         | UNAUTHORIZED            | Missing or invalid JWT |
| 403         | FORBIDDEN               | Authenticated but not owner of the resource |
| 404         | NOT_FOUND               | Resource does not exist |
| 409         | CONFLICT                | Duplicate official asset, etc. |
| 422         | UNPROCESSABLE_ENTITY    | Semantic validation failed |
| 429         | RATE_LIMIT_EXCEEDED     | Too many requests |
| 500         | INTERNAL_SERVER_ERROR   | Unexpected server error |

---

## 2. Authentication Endpoints

### 2.1 Login
```
POST /api/v1/auth/login
```
**Description:** Authenticate user and obtain JWT tokens.  
**Access:** Public

**Request Body**
```json
{
  "email": "priya@company.com",      // string, required, valid email
  "password": "SecurePass123!"       // string, required, min 8 chars
}
```

**Success Response – 200 OK**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

**Error Responses**
- `401 Unauthorized` – Invalid credentials
- `422 Unprocessable Entity` – Validation error

---

### 2.2 Refresh Token
```
POST /api/v1/auth/refresh
```
**Description:** Obtain a new access token using a valid refresh token.  
**Access:** Public (requires valid refresh token)

**Request Body**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Success Response – 200 OK**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

---

### 2.3 Get Current User
```
GET /api/v1/auth/me
```
**Description:** Return the currently authenticated user.  
**Access:** Authenticated

**Success Response – 200 OK**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "priya@company.com",
  "full_name": "Priya Sharma",
  "is_active": true,
  "created_at": "2026-10-01T10:00:00Z"
}
```

---

## 3. Brand Profile Endpoints

### 3.1 Create Brand
```
POST /api/v1/brands
```
**Description:** Create a new Brand Profile.  
**Access:** Authenticated (`brand:create`)

**Request Body**
```json
{
  "name": "Nike",                          // string, required, 2-255 chars
  "website": "https://www.nike.com",       // string, optional, valid URL
  "logo_url": null                         // string, optional (upload handled separately)
}
```

**Success Response – 201 Created**
```json
{
  "id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
  "name": "Nike",
  "normalized_name": "nike",
  "website": "https://www.nike.com",
  "logo_url": null,
  "owner_id": "550e8400-e29b-41d4-a716-446655440000",
  "created_at": "2026-10-12T08:00:00Z",
  "updated_at": "2026-10-12T08:00:00Z"
}
```

---

### 3.2 List Brands
```
GET /api/v1/brands
```
**Description:** List all brands owned by the current user.  
**Access:** Authenticated

**Query Parameters**
| Name     | Type   | Default | Description |
|----------|--------|---------|-------------|
| page     | int    | 1       | Page number |
| page_size| int    | 20      | Items per page (max 100) |

**Success Response – 200 OK**
```json
{
  "items": [
    {
      "id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
      "name": "Nike",
      "logo_url": "https://storage.example.com/logos/nike.png",
      "created_at": "2026-10-12T08:00:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total_items": 1,
    "total_pages": 1
  }
}
```

---

### 3.3 Get Brand by ID
```
GET /api/v1/brands/{brand_id}
```
**Description:** Retrieve a single brand with summary of official assets.  
**Access:** Authenticated + Owner

**Success Response – 200 OK**
```json
{
  "id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
  "name": "Nike",
  "normalized_name": "nike",
  "website": "https://www.nike.com",
  "logo_url": "https://storage.example.com/logos/nike.png",
  "official_social_count": 3,
  "official_app_count": 2,
  "created_at": "2026-10-12T08:00:00Z",
  "updated_at": "2026-10-12T08:00:00Z"
}
```

---

### 3.4 Update Brand
```
PATCH /api/v1/brands/{brand_id}
```
**Description:** Partially update a brand.  
**Access:** Authenticated + Owner

**Request Body** (all fields optional)
```json
{
  "name": "Nike Inc.",
  "website": "https://www.nike.com",
  "logo_url": "https://storage.example.com/logos/nike-new.png"
}
```

**Success Response – 200 OK** (full brand object)

---

### 3.5 Delete Brand
```
DELETE /api/v1/brands/{brand_id}
```
**Description:** Soft-delete or hard-delete a brand and cascade to assets & detections.  
**Access:** Authenticated + Owner  
**Success Response – 204 No Content**

---

## 4. Official Social Accounts

### 4.1 Add Official Social Account
```
POST /api/v1/brands/{brand_id}/social-accounts
```
**Access:** Authenticated + Owner

**Request Body**
```json
{
  "platform": "x",                     // string, required: x | instagram | facebook | linkedin | tiktok
  "handle": "@Nike",                   // string, required
  "url": "https://x.com/Nike",         // string, optional
  "is_verified": true                  // boolean, optional, default false
}
```

**Success Response – 201 Created**
```json
{
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "brand_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
  "platform": "x",
  "handle": "@Nike",
  "url": "https://x.com/Nike",
  "is_verified": true,
  "created_at": "2026-10-12T08:05:00Z"
}
```

**Error:** `409 Conflict` if the same platform + handle already exists for the brand.

---

### 4.2 List Official Social Accounts
```
GET /api/v1/brands/{brand_id}/social-accounts
```
**Access:** Authenticated + Owner  
**Success Response – 200 OK** (array of social account objects)

---

### 4.3 Delete Official Social Account
```
DELETE /api/v1/brands/{brand_id}/social-accounts/{account_id}
```
**Access:** Authenticated + Owner  
**Success Response – 204 No Content**

---

## 5. Official Apps

### 5.1 Add Official App
```
POST /api/v1/brands/{brand_id}/apps
```
**Access:** Authenticated + Owner

**Request Body**
```json
{
  "name": "Nike",                              // string, required
  "package_id": "com.nike.omega",              // string, optional
  "developer_name": "Nike, Inc.",              // string, required
  "store": "google_play",                      // string, required: google_play | app_store
  "store_url": "https://play.google.com/...",  // string, optional
  "logo_url": null                             // string, optional
}
```

**Success Response – 201 Created** (full official app object)

---

### 5.2 List Official Apps
```
GET /api/v1/brands/{brand_id}/apps
```
**Access:** Authenticated + Owner

---

### 5.3 Delete Official App
```
DELETE /api/v1/brands/{brand_id}/apps/{app_id}
```
**Access:** Authenticated + Owner  
**Success Response – 204 No Content**

---

## 6. Detections

### 6.1 Trigger Detection Job
```
POST /api/v1/brands/{brand_id}/detections/run
```
**Description:** Trigger an on-demand detection scan for the brand.  
**Access:** Authenticated + Owner

**Request Body** (optional)
```json
{
  "sources": ["social", "app_store"],   // array of strings, default both
  "force_refresh": false                // boolean, default false
}
```

**Success Response – 202 Accepted**
```json
{
  "job_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "status": "queued",
  "message": "Detection job accepted"
}
```

---

### 6.2 List Detections
```
GET /api/v1/brands/{brand_id}/detections
```
**Description:** Retrieve prioritized detections for a brand.  
**Access:** Authenticated + Owner

**Query Parameters**
| Name        | Type     | Default     | Description |
|-------------|----------|-------------|-------------|
| page        | int      | 1           | Page number |
| page_size   | int      | 20          | Max 100 |
| risk_level  | string   | -           | `high` \| `medium` \| `low` |
| source_type | string   | -           | `social` \| `app_store` |
| platform    | string   | -           | e.g. `x`, `google_play` |
| status      | string   | -           | `needs_review` \| `reviewed` \| `false_positive` \| `escalated` |
| sort_by     | string   | risk_score  | `risk_score` \| `created_at` |
| sort_order  | string   | desc        | `asc` \| `desc` |
| min_score   | float    | -           | Minimum risk_score filter |

**Success Response – 200 OK**
```json
{
  "items": [
    {
      "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "brand_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
      "source_type": "social",
      "platform": "x",
      "title": "Nike Official Support",
      "url": "https://x.com/NikeSupportFake",
      "handle_or_package": "@NikeSupportFake",
      "developer_or_owner": null,
      "description": "Official customer support for Nike...",
      "logo_url": "https://...",
      "risk_score": 87.5,
      "risk_level": "high",
      "status": "needs_review",
      "raw_signals": {
        "name_similarity": 0.92,
        "logo_similarity": 0.78,
        "description_similarity": 0.65,
        "lookalike_bonus": 0.15,
        "publisher_mismatch": null
      },
      "created_at": "2026-10-12T09:15:00Z",
      "updated_at": "2026-10-12T09:15:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total_items": 47,
    "total_pages": 3
  },
  "summary": {
    "high": 12,
    "medium": 23,
    "low": 12,
    "needs_review": 38
  }
}
```

---

### 6.3 Get Detection Detail
```
GET /api/v1/brands/{brand_id}/detections/{detection_id}
```
**Access:** Authenticated + Owner

**Success Response – 200 OK** (full detection object + optional evidence array)

---

### 6.4 Update Detection Status
```
PATCH /api/v1/brands/{brand_id}/detections/{detection_id}
```
**Access:** Authenticated + Owner

**Request Body**
```json
{
  "status": "false_positive"    // required: needs_review | reviewed | false_positive | escalated
}
```

**Success Response – 200 OK** (updated detection object)

---

## 7. Dashboard / Summary

### 7.1 Brand Risk Summary
```
GET /api/v1/brands/{brand_id}/summary
```
**Description:** High-level metrics for the dashboard.  
**Access:** Authenticated + Owner

**Success Response – 200 OK**
```json
{
  "brand_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
  "total_detections": 47,
  "needs_review": 38,
  "high_risk": 12,
  "medium_risk": 23,
  "low_risk": 12,
  "by_source": {
    "social": 31,
    "app_store": 16
  },
  "by_platform": {
    "x": 14,
    "instagram": 9,
    "facebook": 8,
    "google_play": 11,
    "app_store": 5
  },
  "last_scan_at": "2026-10-12T09:15:00Z"
}
```

---

## 8. Health & Utility Endpoints

```
GET /health
→ 200 {"status": "ok"}

GET /ready
→ 200 {"status": "ready", "database": "ok"} 
   or 503 if database unreachable
```

---

## 9. Pagination, Filtering & Sorting Standards

### Pagination
All list endpoints return:
```json
{
  "items": [ ... ],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total_items": 47,
    "total_pages": 3
  }
}
```
- `page` starts at 1
- `page_size` default 20, maximum 100

### Filtering
- Use query parameters (see List Detections for full list)
- Multiple filters are combined with AND logic

### Sorting
- `sort_by` + `sort_order` query parameters
- Default for detections: `risk_score desc`

---

## 10. Rate Limiting Rules & Headers

| Endpoint Group          | Limit                  | Window |
|-------------------------|------------------------|--------|
| Authentication          | 10 requests            | 1 min  |
| Detection trigger       | 5 requests per brand   | 5 min  |
| All other authenticated | 120 requests           | 1 min  |

**Rate Limit Headers (returned on every response)**
```
X-RateLimit-Limit: 120
X-RateLimit-Remaining: 118
X-RateLimit-Reset: 1728720000
```

When exceeded → `429 Too Many Requests` with standard error body.

---

## 11. Common Response Headers

| Header              | Description |
|---------------------|-----------|
| `X-Request-ID`      | Echoed or generated request identifier |
| `X-RateLimit-*`     | Rate limiting information |
| `Content-Type`      | `application/json` |

---

## Appendix – RBAC Summary (MVP)

| Role / Permission     | Description |
|-----------------------|-----------|
| Authenticated User    | Can manage own brands, assets, and detections |
| Owner check           | Enforced on every brand-scoped endpoint |
| Future roles          | `admin`, `viewer` (out of scope for MVP) |

---

**Document Control**  
This API Specification defines the complete contract between the BrandGuard frontend and backend for the hackathon MVP. It is designed to be directly implementable with FastAPI + Pydantic models and to support clear OpenAPI / Swagger documentation generation.

**Next Recommended Steps**
1. Implement Pydantic request/response schemas matching this contract
2. Generate OpenAPI docs via FastAPI automatically
3. Create integration tests against these contracts
4. Publish Postman / Insomnia collection for the team

---
*End of API Specification & Contract*
```
