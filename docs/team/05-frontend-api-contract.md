# Frontend API Integration Contract: Brand Profiles & Official Assets

* **Document Version:** 1.0.0
* **Target Audience:** Person 3 (Frontend), Person 4 (QA & Integration), Person 2 (Detection Engine)
* **Backend Source Branch:** `feature/backend-brand-assets`
* **Backend Commit Baseline:** `e99c40f` (`feat(backend): implement brand and official asset APIs`)
* **API Base URL Path:** `/api/v1`

---

## 1. Architecture & Authentication Overview

### 1.1 Base URL Configuration
The frontend application uses an environment variable to target the FastAPI backend service.

* **Environment Variable:** `VITE_API_BASE_URL` (configured in `frontend/.env.local`, with fallback in `frontend/.env.example`).
* **Default Local Development URL:** `http://localhost:8000/api/v1`
* **Axios Instance Setup:** Pre-configured in [`frontend/src/services/api.ts`](file:///c:/Users/PRANAV%20KARTHIKEYA/OneDrive/Desktop/VigilX/frontend/src/services/api.ts) with `baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'`.

### 1.2 Supabase Token Acquisition & FastAPI Authentication
All brand and official asset endpoints require an authenticated user identity. Authentication is handled using Supabase Auth ES256 JWTs.

1. **Obtaining the Access Token:**
   The frontend obtains the active session JWT from the Supabase client:
   ```typescript
   import { supabase } from './supabase';

   const { data } = await supabase.auth.getSession();
   const accessToken = data.session?.access_token;
   ```

2. **Sending the Token to FastAPI:**
   The JWT must be provided in the HTTP `Authorization` header using the `Bearer` scheme:
   ```http
   Authorization: Bearer <access_token>
   ```

3. **Automatic Request Interceptor:**
   [`frontend/src/services/api.ts`](file:///c:/Users/PRANAV%20KARTHIKEYA/OneDrive/Desktop/VigilX/frontend/src/services/api.ts) contains an Axios interceptor that automatically attaches this header to all outgoing requests if an active Supabase session exists:
   ```typescript
   api.interceptors.request.use(async (config) => {
     const { data } = await supabase.auth.getSession();
     const token = data.session?.access_token;
     if (token) {
       config.headers.Authorization = `Bearer ${token}`;
     }
     return config;
   });
   ```

4. **JIT User Synchronization:**
   Upon the first valid authenticated request, the FastAPI backend automatically synchronizes or provisions the user in the backend PostgreSQL `users` table via `get_current_user`. The user's Supabase UUID becomes their `current_user.id`, used for brand ownership enforcement.

---

## 2. Common Data Structures & Schemas

### 2.1 Enums & Allowed Values
* **Social Platforms (`SocialPlatform`):**
  * `"x"`
  * `"instagram"`
  * `"facebook"`
  * `"linkedin"`
  * `"tiktok"`
* **App Stores (`AppStore`):**
  * `"google_play"`
  * `"app_store"`

### 2.2 Standard Pagination Envelope
Endpoints that return collections (e.g. `GET /api/v1/brands`) return the following paginated envelope:
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

### 2.3 Error Response Schemas
The backend returns errors in two standard formats:

1. **Standard Application HTTP Error (401, 403, 404, 409):**
   ```json
   {
     "status": 404,
     "error_code": "HTTP_ERROR",
     "message": "Brand not found",
     "details": [],
     "request_id": "4b68ff0c-7b95-46aa-a82a-4467d32c0205",
     "timestamp": "2026-10-12T21:00:00.000000+00:00"
   }
   ```
   *Note: For 401 Unauthorized errors, `error_code` is `"AUTHENTICATION_ERROR"`.*

2. **Validation Error (HTTP 422 Unprocessable Entity):**
   Triggered when input validation (length, type, blank checks) fails:
   ```json
   {
     "detail": [
       {
         "type": "value_error",
         "loc": ["body", "name"],
         "msg": "Brand name must contain at least 2 non-whitespace characters",
         "input": "   "
       }
     ]
   }
   ```

---

## 3. Complete Endpoint Reference

### Endpoint 1: Create Brand Profile
* **Method & Path:** `POST /api/v1/brands`
* **Description:** Creates a brand profile owned by the authenticated user.
* **Authentication:** Required (`Authorization: Bearer <token>`).
* **Query Parameters:** None.
* **Request Headers:** `Content-Type: application/json`

#### Request Payload
| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `name` | `string` | **Yes** | Min 2 non-whitespace chars, max 255 chars | Brand display name. Trimming is applied. |
| `website` | `string \| null` | No | Max 512 chars, valid URL format | Official brand homepage URL. |
| `logo_url` | `string \| null` | No | Valid URL string | URL to official high-resolution brand logo. |

*Note: There is NO `description` field on Brand.*

#### Request Example
```json
{
  "name": "Nike",
  "website": "https://www.nike.com",
  "logo_url": "https://example.com/assets/nike-logo.png"
}
```

#### Response: `201 Created`
```json
{
  "id": "7bfa6d98-1e42-45e3-8557-ca59885145b0",
  "owner_id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
  "name": "Nike",
  "normalized_name": "nike",
  "website": "https://www.nike.com",
  "logo_url": "https://example.com/assets/nike-logo.png",
  "logo_phash": null,
  "created_at": "2026-10-12T20:30:00.000000+00:00",
  "updated_at": "2026-10-12T20:30:00.000000+00:00"
}
```

#### Error Responses
* **401 Unauthorized:** Missing or invalid Bearer token.
* **422 Unprocessable Entity:** Brand name is missing, shorter than 2 characters, or whitespace-only (`"   "`).

---

### Endpoint 2: List Brand Profiles
* **Method & Path:** `GET /api/v1/brands`
* **Description:** Retrieves a paginated list of brands owned by the calling user.
* **Authentication:** Required (`Authorization: Bearer <token>`).
* **Query Parameters:**
  | Parameter | Type | Required | Default | Constraints | Description |
  |---|---|---|---|---|---|
  | `page` | `integer` | No | `1` | `ge=1` | Target page number. |
  | `page_size` | `integer` | No | `20` | `ge=1, le=100` | Number of items per page. |

#### Request Example
```http
GET /api/v1/brands?page=1&page_size=20 HTTP/1.1
Authorization: Bearer <token>
```

#### Response: `200 OK`
```json
{
  "items": [
    {
      "id": "7bfa6d98-1e42-45e3-8557-ca59885145b0",
      "owner_id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
      "name": "Nike",
      "normalized_name": "nike",
      "website": "https://www.nike.com",
      "logo_url": "https://example.com/assets/nike-logo.png",
      "logo_phash": null,
      "created_at": "2026-10-12T20:30:00.000000+00:00",
      "updated_at": "2026-10-12T20:30:00.000000+00:00"
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

#### Error Responses
* **401 Unauthorized:** Missing or invalid Bearer token.
* **422 Unprocessable Entity:** `page < 1`, `page_size < 1`, or `page_size > 100`.

---

### Endpoint 3: Get Brand Profile by ID
* **Method & Path:** `GET /api/v1/brands/{brand_id}`
* **Description:** Retrieves detailed brand profile including asset counts.
* **Authentication:** Required (`Authorization: Bearer <token>`).
* **Path Parameters:**
  * `brand_id` (`UUID`): ID of the brand profile.

#### Request Example
```http
GET /api/v1/brands/7bfa6d98-1e42-45e3-8557-ca59885145b0 HTTP/1.1
Authorization: Bearer <token>
```

#### Response: `200 OK`
```json
{
  "id": "7bfa6d98-1e42-45e3-8557-ca59885145b0",
  "owner_id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
  "name": "Nike",
  "normalized_name": "nike",
  "website": "https://www.nike.com",
  "logo_url": "https://example.com/assets/nike-logo.png",
  "logo_phash": null,
  "created_at": "2026-10-12T20:30:00.000000+00:00",
  "updated_at": "2026-10-12T20:30:00.000000+00:00",
  "official_social_count": 2,
  "official_app_count": 1
}
```

#### Error Responses
* **401 Unauthorized:** Missing or invalid Bearer token.
* **403 Forbidden:** The brand exists but belongs to another user.
* **404 Not Found:** Brand profile with specified `brand_id` does not exist.
* **422 Unprocessable Entity:** `brand_id` is not a valid UUID.

---

### Endpoint 4: Register Official Social Account
* **Method & Path:** `POST /api/v1/brands/{brand_id}/social-accounts`
* **Description:** Registers an official social media account to exclude it from impersonation detections.
* **Authentication:** Required (`Authorization: Bearer <token>`).
* **Path Parameters:**
  * `brand_id` (`UUID`): Brand ID.

#### Request Payload
| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `platform` | `string` | **Yes** | One of: `"x"`, `"instagram"`, `"facebook"`, `"linkedin"`, `"tiktok"` | Target social network. |
| `raw_handle` | `string` | **Yes** | Min 1 non-whitespace char other than `@`, max 255 | Display handle (e.g. `"@Nike"`). |
| `url` | `string \| null` | No | Valid URL string | Direct URL to official account profile. |
| `is_verified` | `boolean` | No | Default `false` | Indicates whether account holds verified badge on platform. |

*Normalization Note:* The backend strips any leading `@` symbols, trims whitespace, and converts to lowercase to compute the unique `handle`. Both `raw_handle` and normalized `handle` are preserved.

#### Request Example
```json
{
  "platform": "x",
  "raw_handle": "@Nike",
  "url": "https://x.com/Nike",
  "is_verified": true
}
```

#### Response: `201 Created`
```json
{
  "id": "e4585c5d-3d44-4824-9b2f-77b31043c981",
  "brand_id": "7bfa6d98-1e42-45e3-8557-ca59885145b0",
  "platform": "x",
  "handle": "nike",
  "raw_handle": "@Nike",
  "url": "https://x.com/Nike",
  "is_verified": true,
  "created_at": "2026-10-12T20:35:00.000000+00:00"
}
```

#### Error Responses
* **401 Unauthorized:** Missing or invalid Bearer token.
* **403 Forbidden:** Calling user does not own this brand.
* **404 Not Found:** Brand not found.
* **409 Conflict:** Official social account already registered for this brand, platform, and normalized handle (`"Official social account already registered for this platform and handle"`).
* **422 Unprocessable Entity:** Handle is empty, whitespace-only, or consists solely of `@` symbols (`"@"`, `"@@@"`), or invalid platform enum.

---

### Endpoint 5: List Official Social Accounts
* **Method & Path:** `GET /api/v1/brands/{brand_id}/social-accounts`
* **Description:** Lists all official social accounts registered for the specified brand.
* **Authentication:** Required (`Authorization: Bearer <token>`).
* **Path Parameters:**
  * `brand_id` (`UUID`): Brand ID.

#### Request Example
```http
GET /api/v1/brands/7bfa6d98-1e42-45e3-8557-ca59885145b0/social-accounts HTTP/1.1
Authorization: Bearer <token>
```

#### Response: `200 OK`
```json
[
  {
    "id": "e4585c5d-3d44-4824-9b2f-77b31043c981",
    "brand_id": "7bfa6d98-1e42-45e3-8557-ca59885145b0",
    "platform": "x",
    "handle": "nike",
    "raw_handle": "@Nike",
    "url": "https://x.com/Nike",
    "is_verified": true,
    "created_at": "2026-10-12T20:35:00.000000+00:00"
  }
]
```

#### Error Responses
* **401 Unauthorized:** Missing or invalid Bearer token.
* **403 Forbidden:** Calling user does not own this brand.
* **404 Not Found:** Brand not found.

---

### Endpoint 6: Delete Official Social Account
* **Method & Path:** `DELETE /api/v1/brands/{brand_id}/social-accounts/{account_id}`
* **Description:** Deletes an official social account from the brand profile.
* **Authentication:** Required (`Authorization: Bearer <token>`).
* **Path Parameters:**
  * `brand_id` (`UUID`): Brand ID.
  * `account_id` (`UUID`): Social account ID.

#### Request Example
```http
DELETE /api/v1/brands/7bfa6d98-1e42-45e3-8557-ca59885145b0/social-accounts/e4585c5d-3d44-4824-9b2f-77b31043c981 HTTP/1.1
Authorization: Bearer <token>
```

#### Response: `204 No Content`
*(Empty response body)*

#### Error Responses
* **401 Unauthorized:** Missing or invalid Bearer token.
* **403 Forbidden:** Calling user does not own this brand.
* **404 Not Found:** Brand not found, or account ID does not exist under this brand (`"Official social account not found"`). Cross-brand access returns 404.

---

### Endpoint 7: Register Official Mobile App
* **Method & Path:** `POST /api/v1/brands/{brand_id}/apps`
* **Description:** Registers an official mobile app store listing for impersonation exclusion.
* **Authentication:** Required (`Authorization: Bearer <token>`).
* **Path Parameters:**
  * `brand_id` (`UUID`): Brand ID.

#### Request Payload
| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `name` | `string` | **Yes** | Min 1 non-whitespace char, max 255 | Official application display title. |
| `developer_name` | `string` | **Yes** | Min 1 non-whitespace char, max 255 | Official developer or publisher name. |
| `store` | `string` | **Yes** | One of: `"google_play"`, `"app_store"` | Mobile platform store. |
| `package_id` | `string \| null` | No | Max 255 chars | Bundle or Package identifier (e.g. `com.nike.omega`). |
| `store_url` | `string \| null` | No | Valid URL string | Store listing URL. |
| `logo_url` | `string \| null` | No | Valid URL string | Official app icon image URL. |

#### Request Example
```json
{
  "name": "Nike: Shoes, Apparel & Stories",
  "developer_name": "Nike, Inc.",
  "store": "google_play",
  "package_id": "com.nike.omega",
  "store_url": "https://play.google.com/store/apps/details?id=com.nike.omega",
  "logo_url": "https://example.com/assets/nike-app-icon.png"
}
```

#### Response: `201 Created`
```json
{
  "id": "18cfdfd7-839f-4ae8-80e9-b22da924d5e7",
  "brand_id": "7bfa6d98-1e42-45e3-8557-ca59885145b0",
  "name": "Nike: Shoes, Apparel & Stories",
  "package_id": "com.nike.omega",
  "developer_name": "Nike, Inc.",
  "store": "google_play",
  "store_url": "https://play.google.com/store/apps/details?id=com.nike.omega",
  "logo_url": "https://example.com/assets/nike-app-icon.png",
  "created_at": "2026-10-12T20:40:00.000000+00:00"
}
```

#### Error Responses
* **401 Unauthorized:** Missing or invalid Bearer token.
* **403 Forbidden:** Calling user does not own this brand.
* **404 Not Found:** Brand not found.
* **422 Unprocessable Entity:** App name or developer name is whitespace-only, or invalid store value.

---

### Endpoint 8: List Official Mobile Apps
* **Method & Path:** `GET /api/v1/brands/{brand_id}/apps`
* **Description:** Lists all official mobile apps registered for the specified brand.
* **Authentication:** Required (`Authorization: Bearer <token>`).
* **Path Parameters:**
  * `brand_id` (`UUID`): Brand ID.

#### Request Example
```http
GET /api/v1/brands/7bfa6d98-1e42-45e3-8557-ca59885145b0/apps HTTP/1.1
Authorization: Bearer <token>
```

#### Response: `200 OK`
```json
[
  {
    "id": "18cfdfd7-839f-4ae8-80e9-b22da924d5e7",
    "brand_id": "7bfa6d98-1e42-45e3-8557-ca59885145b0",
    "name": "Nike: Shoes, Apparel & Stories",
    "package_id": "com.nike.omega",
    "developer_name": "Nike, Inc.",
    "store": "google_play",
    "store_url": "https://play.google.com/store/apps/details?id=com.nike.omega",
    "logo_url": "https://example.com/assets/nike-app-icon.png",
    "created_at": "2026-10-12T20:40:00.000000+00:00"
  }
]
```

#### Error Responses
* **401 Unauthorized:** Missing or invalid Bearer token.
* **403 Forbidden:** Calling user does not own this brand.
* **404 Not Found:** Brand not found.

---

### Endpoint 9: Delete Official Mobile App
* **Method & Path:** `DELETE /api/v1/brands/{brand_id}/apps/{app_id}`
* **Description:** Deletes an official mobile app from the brand profile.
* **Authentication:** Required (`Authorization: Bearer <token>`).
* **Path Parameters:**
  * `brand_id` (`UUID`): Brand ID.
  * `app_id` (`UUID`): Mobile app ID.

#### Request Example
```http
DELETE /api/v1/brands/7bfa6d98-1e42-45e3-8557-ca59885145b0/apps/18cfdfd7-839f-4ae8-80e9-b22da924d5e7 HTTP/1.1
Authorization: Bearer <token>
```

#### Response: `204 No Content`
*(Empty response body)*

#### Error Responses
* **401 Unauthorized:** Missing or invalid Bearer token.
* **403 Forbidden:** Calling user does not own this brand.
* **404 Not Found:** Brand not found, or app ID does not exist under this brand (`"Official app not found"`). Cross-brand access returns 404.

---

## 4. TypeScript Definitions (`frontend/src/types/brand.ts`)

Person 3 should place these exact, type-safe definitions in [`frontend/src/types/brand.ts`](file:///c:/Users/PRANAV%20KARTHIKEYA/OneDrive/Desktop/VigilX/frontend/src/types/brand.ts):

```typescript
/**
 * vigilX Brand & Official Asset TypeScript Interfaces
 * Corresponds to Backend commit e99c40f
 */

// ==========================================
// Pagination & Common Envelopes
// ==========================================

export interface PaginationMeta {
  page: number;
  page_size: number;
  total_items: number;
  total_pages: number;
}

export interface PaginatedResponse<T> {
  items: T[];
  pagination: PaginationMeta;
}

export interface StandardErrorResponse {
  status: number;
  error_code: string;
  message: string;
  details: Array<{ field: string; issue: string }>;
  request_id?: string;
  timestamp: string;
}

// ==========================================
// Brand Profiles
// ==========================================

export interface Brand {
  id: string;
  owner_id: string;
  name: string;
  normalized_name: string;
  website: string | null;
  logo_url: string | null;
  logo_phash: string | null;
  created_at: string;
  updated_at: string;
}

export interface BrandDetail extends Brand {
  official_social_count: number;
  official_app_count: number;
}

export interface BrandCreatePayload {
  name: string;
  website?: string | null;
  logo_url?: string | null;
}

// ==========================================
// Official Social Accounts
// ==========================================

export type SocialPlatform = 'x' | 'instagram' | 'facebook' | 'linkedin' | 'tiktok';

export interface OfficialSocialAccount {
  id: string;
  brand_id: string;
  platform: SocialPlatform;
  handle: string;
  raw_handle: string;
  url: string | null;
  is_verified: boolean;
  created_at: string;
}

export interface OfficialSocialCreatePayload {
  platform: SocialPlatform;
  raw_handle: string;
  url?: string | null;
  is_verified?: boolean;
}

// ==========================================
// Official Mobile Apps
// ==========================================

export type AppStore = 'google_play' | 'app_store';

export interface OfficialApp {
  id: string;
  brand_id: string;
  name: string;
  package_id: string | null;
  developer_name: string;
  store: AppStore;
  store_url: string | null;
  logo_url: string | null;
  created_at: string;
}

export interface OfficialAppCreatePayload {
  name: string;
  developer_name: string;
  store: AppStore;
  package_id?: string | null;
  store_url?: string | null;
  logo_url?: string | null;
}
```

---

## 5. API Client Methods (`frontend/src/services/brandsApi.ts`)

Person 3 can integrate these typed functions directly into the frontend service layer:

```typescript
import api from './api';
import {
  Brand,
  BrandDetail,
  BrandCreatePayload,
  PaginatedResponse,
  OfficialSocialAccount,
  OfficialSocialCreatePayload,
  OfficialApp,
  OfficialAppCreatePayload,
} from '../types/brand';

// ------------------------------------------
// Brand Profiles
// ------------------------------------------

export const createBrand = async (payload: BrandCreatePayload): Promise<Brand> => {
  const res = await api.post<Brand>('/brands', payload);
  return res.data;
};

export const getBrands = async (page = 1, pageSize = 20): Promise<PaginatedResponse<Brand>> => {
  const res = await api.get<PaginatedResponse<Brand>>('/brands', {
    params: { page, page_size: pageSize },
  });
  return res.data;
};

export const getBrandById = async (brandId: string): Promise<BrandDetail> => {
  const res = await api.get<BrandDetail>(`/brands/${brandId}`);
  return res.data;
};

// ------------------------------------------
// Official Social Accounts
// ------------------------------------------

export const addSocialAccount = async (
  brandId: string,
  payload: OfficialSocialCreatePayload,
): Promise<OfficialSocialAccount> => {
  const res = await api.post<OfficialSocialAccount>(`/brands/${brandId}/social-accounts`, payload);
  return res.data;
};

export const getSocialAccounts = async (brandId: string): Promise<OfficialSocialAccount[]> => {
  const res = await api.get<OfficialSocialAccount[]>(`/brands/${brandId}/social-accounts`);
  return res.data;
};

export const deleteSocialAccount = async (brandId: string, accountId: string): Promise<void> => {
  await api.delete(`/brands/${brandId}/social-accounts/${accountId}`);
};

// ------------------------------------------
// Official Mobile Apps
// ------------------------------------------

export const addOfficialApp = async (
  brandId: string,
  payload: OfficialAppCreatePayload,
): Promise<OfficialApp> => {
  const res = await api.post<OfficialApp>(`/brands/${brandId}/apps`, payload);
  return res.data;
};

export const getOfficialApps = async (brandId: string): Promise<OfficialApp[]> => {
  const res = await api.get<OfficialApp[]>(`/brands/${brandId}/apps`);
  return res.data;
};

export const deleteOfficialApp = async (brandId: string, appId: string): Promise<void> => {
  await api.delete(`/brands/${brandId}/apps/${appId}`);
};
```

---

## 6. Integration Notes & Team FAQ

1. **Brand Description Field:**
   * Reminder: There is **no `description` field** on the Brand entity or database table. Do not include a description input in `BrandProfileForm.tsx`.
2. **`logo_phash` Field:**
   * The `logo_phash` attribute in `BrandResponse` is nullable and is currently `null` upon initial brand creation. Image perceptual hashing is handled downstream during logo inspection.
3. **`is_verified` Checkbox:**
   * In social account creation, `is_verified` defaults to `false`. When checked in the UI, it informs the detection engine exclusion pipeline that the account possesses platform-verified badge credentials.
4. **Error Handling in UI:**
   * Duplicate social handles return HTTP 409 Conflict with message `"Official social account already registered for this platform and handle"`. The UI should display this as an inline warning under the handle field.
   * Empty or symbol-only handles (e.g. `"@"`, `"@@@"`) return HTTP 422. Form validation should proactively check `handle.replace(/^@+/, '').trim().length > 0` before submission.
5. **Cross-Brand Isolation:**
   * Endpoints strictly enforce that assets belong to the specific `brand_id` in the URL path. Any attempt to modify an asset belonging to another brand returns HTTP 404.
