# Implementation Brief 03: Frontend Brand Onboarding & Asset UI

* **Assigned Team Member:** Person 3 (Frontend)
* **Assigned Git Branch:** `feature/frontend-brand-profile`
* **Parent Branch:** `origin/master` (Commit `8840f59`)

---

## 1. Objective
Create the TypeScript type definitions and user interface components for Brand Onboarding and Official Asset Management. This provides an intuitive workflow for analysts to create a Brand Profile and register official social media handles and mobile app listings, consuming Person 1's backend API contracts.

---

## 2. Exact Initial Files to Inspect

1. **[`frontend/src/App.tsx`](file:///c:/Users/PRANAV%20KARTHIKEYA/OneDrive/Desktop/VigilX/frontend/src/App.tsx):**
   * Inspect current application layout, Tailwind design system, Lucide icons, and state containers.
2. **[`frontend/src/services/api.ts`](file:///c:/Users/PRANAV%20KARTHIKEYA/OneDrive/Desktop/VigilX/frontend/src/services/api.ts):**
   * Inspect Axios client pre-configured with `baseURL` (`http://localhost:8000/api/v1`) and Supabase JWT Bearer token request interceptor.
3. **[`frontend/src/services/supabase.ts`](file:///c:/Users/PRANAV%20KARTHIKEYA/OneDrive/Desktop/VigilX/frontend/src/services/supabase.ts):**
   * Inspect Supabase client initialization.
4. **[`docs/team/01-backend-brand-assets.md`](./01-backend-brand-assets.md):**
   * Source of truth for backend endpoints, field names, and request/response shapes.

---

## 3. Expected Files to Create or Modify

* **Create:** `frontend/src/types/brand.ts`
* **Create:** `frontend/src/components/BrandProfileForm.tsx`
* **Create:** `frontend/src/components/OfficialSocialList.tsx`
* **Create:** `frontend/src/components/OfficialAppList.tsx`
* **Modify:** `frontend/src/services/api.ts` (add typed brand and asset API functions)
* **Modify:** `frontend/src/App.tsx` (embed the Brand onboarding components)

---

## 4. Dependencies & Typed Contracts (`frontend/src/types/brand.ts`)

Must match the backend schema exactly (**note: NO `description` field on Brand**):

```typescript
export interface Brand {
  id: string;
  owner_id: string;
  name: string;
  normalized_name: string;
  website: string | null;
  logo_url: string | null;
  created_at: string;
  updated_at: string;
}

export interface BrandCreatePayload {
  name: string;
  website?: string | null;
  logo_url?: string | null;
}

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
  package_id?: string | null;
  developer_name: string;
  store: AppStore;
  store_url?: string | null;
  logo_url?: string | null;
}
```

---

## 5. API Client Methods (`frontend/src/services/api.ts`)

Export typed helper functions:
```typescript
import api from './api';
import {
  Brand, BrandCreatePayload,
  OfficialSocialAccount, OfficialSocialCreatePayload,
  OfficialApp, OfficialAppCreatePayload
} from '../types/brand';

// Brands
export const createBrand = async (payload: BrandCreatePayload): Promise<Brand> => {
  const res = await api.post<Brand>('/brands', payload);
  return res.data;
};

export const getBrands = async (): Promise<{ items: Brand[] }> => {
  const res = await api.get<{ items: Brand[] }>('/brands');
  return res.data;
};

// Social Accounts
export const addSocialAccount = async (brandId: string, payload: OfficialSocialCreatePayload): Promise<OfficialSocialAccount> => {
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

// Official Apps
export const addOfficialApp = async (brandId: string, payload: OfficialAppCreatePayload): Promise<OfficialApp> => {
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

## 6. UI Component Requirements

### A. `BrandProfileForm.tsx`
* Input for Brand Name (required).
* Input for Website URL (optional, with URL regex validation).
* Input for Logo URL (optional).
* Primary action button with loading spinner state (`"Saving Brand..."`).
* Error banner displaying API error messages (or `StandardErrorResponse.message`).

### B. `OfficialSocialList.tsx`
* Dropdown selector for platform: `X (Twitter)`, `Instagram`, `Facebook`, `LinkedIn`, `TikTok`.
* Handle input with `@` placeholder.
* Profile URL input (optional) and Verified toggle.
* Dynamic table/list rendering registered accounts with platform badges and a Delete button.

### C. `OfficialAppList.tsx`
* Dropdown selector for Store: `Google Play`, `Apple App Store`.
* App Name input (required).
* Package / Bundle ID input (e.g., `com.company.app`).
* Developer Name input (required).
* Dynamic list showing registered apps with a Delete button.

---

## 7. Acceptance Criteria

1. **Type Safety:** Zero `any` types in `brand.ts` and component props.
2. **Field Alignment:** No `description` field exists in form inputs or payload types.
3. **Input Validation:** Prevents form submission if Brand Name or App Developer Name is empty.
4. **Error Handling:** Displays user-friendly notifications if the server returns `409 Conflict` (duplicate social handle) or `401 Unauthorized`.
5. **Clean Production Build:** `npm run build` (`tsc -b && vite build`) executes cleanly with 0 errors or warnings.

---

## 8. Build Verification Command

Run from the `frontend/` directory:
```powershell
npm run build
```

---

## 9. Explicitly Out-of-Scope Work for This Task

* Do **not** build the threat detection dashboard, metrics cards, or review drawer yet (scheduled for Phase B).
* Do **not** build custom authentication screens (relies on active Supabase session in `api.ts`).
* Do **not** edit any backend Python files or database files.
