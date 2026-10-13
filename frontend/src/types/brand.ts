/**
 * vigilX Brand & Official Asset TypeScript Interfaces
 * Corresponds to Backend commit e99c40f and docs/team/05-frontend-api-contract.md
 */

// ==========================================
// Pagination & Common Envelopes
// ==========================================

export interface PaginationMeta {
  page: number
  page_size: number
  total_items: number
  total_pages: number
}

export interface PaginatedResponse<T> {
  items: T[]
  pagination: PaginationMeta
}

export interface StandardErrorDetail {
  field: string
  issue: string
}

export interface StandardErrorResponse {
  status: number
  error_code: string
  message: string
  details: StandardErrorDetail[]
  request_id?: string
  timestamp: string
}

export interface ValidationErrorDetail {
  type: string
  loc: Array<string | number>
  msg: string
  input: unknown
}

export interface ValidationErrorResponse {
  detail: ValidationErrorDetail[]
}

// ==========================================
// Brand Profiles
// ==========================================

export interface Brand {
  id: string
  owner_id: string
  name: string
  normalized_name: string
  website: string | null
  logo_url: string | null
  logo_phash: string | null
  created_at: string
  updated_at: string
}

export interface BrandDetail extends Brand {
  official_social_count: number
  official_app_count: number
}

export interface BrandCreatePayload {
  name: string
  website?: string | null
  logo_url?: string | null
}

// ==========================================
// Official Social Accounts
// ==========================================

export type SocialPlatform = 'x' | 'instagram' | 'facebook' | 'linkedin' | 'tiktok'

export interface OfficialSocialAccount {
  id: string
  brand_id: string
  platform: SocialPlatform
  handle: string
  raw_handle: string
  url: string | null
  is_verified: boolean
  created_at: string
}

export interface OfficialSocialCreatePayload {
  platform: SocialPlatform
  raw_handle: string
  url?: string | null
  is_verified?: boolean
}

// ==========================================
// Official Mobile Apps
// ==========================================

export type AppStore = 'google_play' | 'app_store'

export interface OfficialApp {
  id: string
  brand_id: string
  name: string
  package_id: string | null
  developer_name: string
  store: AppStore
  store_url: string | null
  logo_url: string | null
  created_at: string
}

export interface OfficialAppCreatePayload {
  name: string
  developer_name: string
  store: AppStore
  package_id?: string | null
  store_url?: string | null
  logo_url?: string | null
}
