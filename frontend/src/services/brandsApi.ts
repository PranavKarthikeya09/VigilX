import axios from 'axios'
import api from './api'
import type {
  Brand,
  BrandDetail,
  BrandCreatePayload,
  PaginatedResponse,
  OfficialSocialAccount,
  OfficialSocialCreatePayload,
  OfficialApp,
  OfficialAppCreatePayload,
  StandardErrorResponse,
  ValidationErrorResponse,
} from '../types/brand'

// ============================================================================
// Brand Profile Endpoints
// ============================================================================

/**
 * Lists brands owned by the authenticated user with pagination.
 * Endpoint: GET /api/v1/brands?page={page}&page_size={pageSize}
 */
export const getBrands = async (
  page = 1,
  pageSize = 20,
): Promise<PaginatedResponse<Brand>> => {
  const response = await api.get<PaginatedResponse<Brand>>('/brands', {
    params: {
      page,
      page_size: pageSize,
    },
  })
  return response.data
}

export const listBrands = getBrands

/**
 * Retrieves a single brand profile by ID including asset summary counts.
 * Endpoint: GET /api/v1/brands/{brand_id}
 */
export const getBrandById = async (brandId: string): Promise<BrandDetail> => {
  const response = await api.get<BrandDetail>(`/brands/${brandId}`)
  return response.data
}

/**
 * Creates a new brand profile assigned to the authenticated user.
 * Endpoint: POST /api/v1/brands
 */
export const createBrand = async (payload: BrandCreatePayload): Promise<Brand> => {
  const response = await api.post<Brand>('/brands', payload)
  return response.data
}

// ============================================================================
// Official Social Account Endpoints
// ============================================================================

/**
 * Lists all official social accounts registered for the specified brand.
 * Endpoint: GET /api/v1/brands/{brand_id}/social-accounts
 */
export const getSocialAccounts = async (
  brandId: string,
): Promise<OfficialSocialAccount[]> => {
  const response = await api.get<OfficialSocialAccount[]>(
    `/brands/${brandId}/social-accounts`,
  )
  return response.data
}

export const listSocialAccounts = getSocialAccounts

/**
 * Registers an official social media account for brand impersonation exclusion.
 * Endpoint: POST /api/v1/brands/{brand_id}/social-accounts
 */
export const addSocialAccount = async (
  brandId: string,
  payload: OfficialSocialCreatePayload,
): Promise<OfficialSocialAccount> => {
  const response = await api.post<OfficialSocialAccount>(
    `/brands/${brandId}/social-accounts`,
    payload,
  )
  return response.data
}

export const createSocialAccount = addSocialAccount

/**
 * Deletes an official social account from the brand profile.
 * Endpoint: DELETE /api/v1/brands/{brand_id}/social-accounts/{account_id}
 * Status: 204 No Content
 */
export const deleteSocialAccount = async (
  brandId: string,
  accountId: string,
): Promise<void> => {
  await api.delete(`/brands/${brandId}/social-accounts/${accountId}`)
}

// ============================================================================
// Official Mobile App Endpoints
// ============================================================================

/**
 * Lists all official mobile apps registered for the specified brand.
 * Endpoint: GET /api/v1/brands/{brand_id}/apps
 */
export const getOfficialApps = async (
  brandId: string,
): Promise<OfficialApp[]> => {
  const response = await api.get<OfficialApp[]>(`/brands/${brandId}/apps`)
  return response.data
}

export const listOfficialApps = getOfficialApps

/**
 * Registers an official mobile app store listing for impersonation exclusion.
 * Endpoint: POST /api/v1/brands/{brand_id}/apps
 */
export const addOfficialApp = async (
  brandId: string,
  payload: OfficialAppCreatePayload,
): Promise<OfficialApp> => {
  const response = await api.post<OfficialApp>(
    `/brands/${brandId}/apps`,
    payload,
  )
  return response.data
}

export const createOfficialApp = addOfficialApp

/**
 * Deletes an official mobile app from the brand profile.
 * Endpoint: DELETE /api/v1/brands/{brand_id}/apps/{app_id}
 * Status: 204 No Content
 */
export const deleteOfficialApp = async (
  brandId: string,
  appId: string,
): Promise<void> => {
  await api.delete(`/brands/${brandId}/apps/${appId}`)
}

// ============================================================================
// Error Extraction Helpers
// ============================================================================

/**
 * Extracts a readable error message from Axios errors returned by FastAPI,
 * handling both StandardErrorResponse and validation detail arrays without swallowing errors.
 */
export const getApiErrorMessage = (error: unknown, fallbackMessage = 'An unexpected error occurred'): string => {
  if (axios.isAxiosError(error) && error.response?.data) {
    const data = error.response.data as Partial<StandardErrorResponse> & Partial<ValidationErrorResponse>

    // 1. Standard application error message (HTTP 401, 403, 404, 409)
    if (typeof data.message === 'string' && data.message.trim().length > 0) {
      return data.message
    }

    // 2. FastAPI/Pydantic validation error details (HTTP 422)
    if (Array.isArray(data.detail) && data.detail.length > 0) {
      const firstError = data.detail[0]
      if (typeof firstError.msg === 'string') {
        const field = Array.isArray(firstError.loc) ? firstError.loc[firstError.loc.length - 1] : undefined
        return field ? `${field}: ${firstError.msg}` : firstError.msg
      }
    }
  }

  if (error instanceof Error && error.message) {
    return error.message
  }

  return fallbackMessage
}
