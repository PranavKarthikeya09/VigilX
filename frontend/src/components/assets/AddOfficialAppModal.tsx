import React, { useState, useEffect, useCallback } from 'react'
import { X, Loader2, AlertCircle, Smartphone } from 'lucide-react'
import { Button } from '../ui/Button'
import { Input } from '../ui/Input'
import { addOfficialApp, getApiErrorMessage } from '../../services/brandsApi'
import type { OfficialApp, OfficialAppCreatePayload, AppStore } from '../../types/brand'

export interface AddOfficialAppModalProps {
  brandId: string
  isOpen: boolean
  onClose: () => void
  onSuccess: (newApp: OfficialApp) => void
}

const SUPPORTED_STORES: Array<{ value: AppStore; label: string }> = [
  { value: 'google_play', label: 'Google Play' },
  { value: 'app_store', label: 'Apple App Store' },
]

export function AddOfficialAppModal({
  brandId,
  isOpen,
  onClose,
  onSuccess,
}: AddOfficialAppModalProps) {
  const [store, setStore] = useState<AppStore>('google_play')
  const [name, setName] = useState('')
  const [developerName, setDeveloperName] = useState('')
  const [packageId, setPackageId] = useState('')
  const [storeUrl, setStoreUrl] = useState('')

  // Field validation errors
  const [nameError, setNameError] = useState<string | null>(null)
  const [developerError, setDeveloperError] = useState<string | null>(null)
  const [urlError, setUrlError] = useState<string | null>(null)
  const [apiError, setApiError] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  const handleClose = useCallback(() => {
    if (isSubmitting) return
    setName('')
    setDeveloperName('')
    setPackageId('')
    setStoreUrl('')
    setStore('google_play')
    setNameError(null)
    setDeveloperError(null)
    setUrlError(null)
    setApiError(null)
    onClose()
  }, [isSubmitting, onClose])

  // Handle Escape key to close
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen && !isSubmitting) {
        handleClose()
      }
    }
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [isOpen, isSubmitting, handleClose])

  if (!isOpen) return null

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setApiError(null)

    const trimmedName = name.trim()
    const trimmedDeveloper = developerName.trim()
    const trimmedPackageId = packageId.trim()
    const trimmedStoreUrl = storeUrl.trim()

    let hasValidationError = false

    // Validate app title (min 1 non-whitespace char, max 255)
    if (!trimmedName) {
      setNameError('Application title is required')
      hasValidationError = true
    } else if (trimmedName.length > 255) {
      setNameError('Application title cannot exceed 255 characters')
      hasValidationError = true
    } else {
      setNameError(null)
    }

    // Validate developer name (min 1 non-whitespace char, max 255)
    if (!trimmedDeveloper) {
      setDeveloperError('Developer or publisher name is required')
      hasValidationError = true
    } else if (trimmedDeveloper.length > 255) {
      setDeveloperError('Developer name cannot exceed 255 characters')
      hasValidationError = true
    } else {
      setDeveloperError(null)
    }

    // Validate store url if provided
    if (trimmedStoreUrl) {
      try {
        const parsed = new URL(trimmedStoreUrl)
        if (!['http:', 'https:'].includes(parsed.protocol)) {
          setUrlError('Store URL must begin with http:// or https://')
          hasValidationError = true
        } else {
          setUrlError(null)
        }
      } catch {
        setUrlError('Please enter a valid URL (e.g. https://play.google.com/store/apps/...)')
        hasValidationError = true
      }
    } else {
      setUrlError(null)
    }

    if (hasValidationError) {
      return
    }

    setIsSubmitting(true)

    try {
      const payload: OfficialAppCreatePayload = {
        name: trimmedName,
        developer_name: trimmedDeveloper,
        store,
        package_id: trimmedPackageId.length > 0 ? trimmedPackageId : null,
        store_url: trimmedStoreUrl.length > 0 ? trimmedStoreUrl : null,
      }

      const createdApp = await addOfficialApp(brandId, payload)
      onSuccess(createdApp)
      handleClose()
    } catch (err: unknown) {
      const errorMsg = getApiErrorMessage(err, 'Failed to register official mobile app')
      setApiError(errorMsg)
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6"
      role="dialog"
      aria-modal="true"
      aria-labelledby="add-app-modal-title"
    >
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black/60 backdrop-blur-sm transition-opacity"
        onClick={handleClose}
        aria-hidden="true"
      />

      {/* Modal Dialog Card */}
      <div className="relative w-full max-w-lg rounded-md border border-[#E5E5E2] bg-white p-6 shadow-xl transition-all z-10 animate-in fade-in zoom-in-95 duration-150 max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-start justify-between pb-3 border-b border-[#E5E5E2]">
          <div className="flex items-center gap-2.5">
            <div className="w-9 h-9 rounded-full bg-[#F0F0ED] border border-[#E5E5E2] flex items-center justify-center text-[#111111]">
              <Smartphone className="w-4 h-4 text-[#111111]" />
            </div>
            <div>
              <h2 id="add-app-modal-title" className="text-base font-semibold text-[#111111]">
                Register Official Mobile App
              </h2>
              <p className="text-xs text-[#525252]">
                Whitelist official store applications for brand impersonation exclusion.
              </p>
            </div>
          </div>
          <button
            type="button"
            onClick={handleClose}
            disabled={isSubmitting}
            className="p-1 rounded text-[#858585] hover:text-[#111111] hover:bg-[#F0F0ED] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#111111] disabled:opacity-50"
            aria-label="Close dialog"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* API Error Banner */}
        {apiError && (
          <div
            className="mt-4 p-3 rounded-md bg-[#FEF2F2] border border-[#FECACA] flex items-start gap-2.5 text-xs text-[#B91C1C]"
            role="alert"
          >
            <AlertCircle className="w-4 h-4 flex-shrink-0 mt-0.5 text-[#DC2626]" />
            <div className="leading-snug">
              <span className="font-semibold">Registration Error: </span>
              {apiError}
            </div>
          </div>
        )}

        {/* Form Body */}
        <form onSubmit={handleSubmit} className="mt-5 space-y-4">
          {/* Store Selector */}
          <div className="space-y-1.5">
            <label
              htmlFor="app-store-select"
              className="block text-xs font-medium text-[#525252] tracking-wide"
            >
              Application Store *
            </label>
            <select
              id="app-store-select"
              value={store}
              onChange={(e) => setStore(e.target.value as AppStore)}
              disabled={isSubmitting}
              className="flex h-9 w-full rounded-md border border-[#E5E5E2] bg-white px-3 py-1.5 text-xs text-[#111111] focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-[#111111] focus-visible:border-[#111111] disabled:opacity-50"
            >
              {SUPPORTED_STORES.map((s) => (
                <option key={s.value} value={s.value}>
                  {s.label}
                </option>
              ))}
            </select>
          </div>

          {/* App Title */}
          <div>
            <Input
              id="app-title-input"
              label="Application Title *"
              placeholder="e.g. Nike: Shoes, Apparel & Stories"
              value={name}
              onChange={(e) => {
                setName(e.target.value)
                if (nameError) setNameError(null)
              }}
              error={nameError || undefined}
              disabled={isSubmitting}
              autoFocus
              maxLength={255}
            />
            <p className="text-[11px] text-[#858585] mt-1">
              Official application display title as cataloged in store listings.
            </p>
          </div>

          {/* Developer / Publisher Name */}
          <div>
            <Input
              id="app-developer-input"
              label="Developer / Publisher Name *"
              placeholder="e.g. Nike, Inc."
              value={developerName}
              onChange={(e) => {
                setDeveloperName(e.target.value)
                if (developerError) setDeveloperError(null)
              }}
              error={developerError || undefined}
              disabled={isSubmitting}
              maxLength={255}
            />
            <p className="text-[11px] text-[#858585] mt-1">
              Authorized publisher name associated with this brand&apos;s store developer account.
            </p>
          </div>

          {/* Package / Bundle Identifier (Optional) */}
          <div>
            <Input
              id="app-package-id-input"
              label="Package / Bundle Identifier (Optional)"
              placeholder={store === 'google_play' ? 'e.g. com.nike.omega' : 'e.g. com.nike.nikeplus'}
              value={packageId}
              onChange={(e) => setPackageId(e.target.value)}
              disabled={isSubmitting}
              maxLength={255}
            />
            <p className="text-[11px] text-[#858585] mt-1">
              Store package identifier for deterministic app exclusion.
            </p>
          </div>

          {/* Store Listing URL (Optional) */}
          <div>
            <Input
              id="app-store-url-input"
              label="Store Listing URL (Optional)"
              type="url"
              placeholder={
                store === 'google_play'
                  ? 'https://play.google.com/store/apps/details?id=com.nike.omega'
                  : 'https://apps.apple.com/app/nike-shoes-apparel-stories/id843466339'
              }
              value={storeUrl}
              onChange={(e) => {
                setStoreUrl(e.target.value)
                if (urlError) setUrlError(null)
              }}
              error={urlError || undefined}
              disabled={isSubmitting}
            />
            <p className="text-[11px] text-[#858585] mt-1">
              Direct store landing page link for verification.
            </p>
          </div>

          {/* Whitelist Note */}
          <div className="p-3 rounded-md bg-[#F0F0ED] border border-[#E5E5E2] text-[11px] text-[#525252] leading-snug">
            <strong className="text-[#111111]">Whitelist Guarantee: </strong>
            Registered applications are cataloged in the exclusion registry so the surveillance collector will not classify them as counterfeit clones.
          </div>

          {/* Action Buttons */}
          <div className="pt-3 border-t border-[#E5E5E2] flex items-center justify-end gap-2.5">
            <Button
              type="button"
              variant="outline"
              size="md"
              onClick={handleClose}
              disabled={isSubmitting}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              variant="primary"
              size="md"
              disabled={isSubmitting}
              icon={isSubmitting ? <Loader2 className="w-4 h-4 animate-spin" /> : undefined}
            >
              {isSubmitting ? 'Registering...' : 'Register Official App'}
            </Button>
          </div>
        </form>
      </div>
    </div>
  )
}
