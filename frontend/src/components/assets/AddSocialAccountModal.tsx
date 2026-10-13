import React, { useState, useEffect, useCallback } from 'react'
import { X, Loader2, AlertCircle, Share2, Check } from 'lucide-react'
import { Button } from '../ui/Button'
import { Input } from '../ui/Input'
import { addSocialAccount, getApiErrorMessage } from '../../services/brandsApi'
import type { OfficialSocialAccount, SocialPlatform } from '../../types/brand'

export interface AddSocialAccountModalProps {
  brandId: string
  isOpen: boolean
  onClose: () => void
  onSuccess: (newAccount: OfficialSocialAccount) => void
}

const SUPPORTED_PLATFORMS: Array<{ value: SocialPlatform; label: string }> = [
  { value: 'x', label: 'X (formerly Twitter)' },
  { value: 'instagram', label: 'Instagram' },
  { value: 'facebook', label: 'Facebook' },
  { value: 'linkedin', label: 'LinkedIn' },
  { value: 'tiktok', label: 'TikTok' },
]

export function AddSocialAccountModal({
  brandId,
  isOpen,
  onClose,
  onSuccess,
}: AddSocialAccountModalProps) {
  const [platform, setPlatform] = useState<SocialPlatform>('x')
  const [rawHandle, setRawHandle] = useState('')
  const [url, setUrl] = useState('')
  const [isVerified, setIsVerified] = useState(false)

  const [handleError, setHandleError] = useState<string | null>(null)
  const [apiError, setApiError] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  const handleClose = useCallback(() => {
    if (isSubmitting) return
    setRawHandle('')
    setUrl('')
    setIsVerified(false)
    setHandleError(null)
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

  // Compute normalized handle preview according to backend contract
  const trimmedHandle = rawHandle.trim()
  const cleanedHandle = trimmedHandle.replace(/^@+/, '').trim()
  const normalizedPreview = cleanedHandle.length > 0 ? cleanedHandle.toLowerCase() : null

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setApiError(null)

    // Backend validation contract:
    // raw_handle must contain at least one non-whitespace character other than '@'
    if (!cleanedHandle) {
      setHandleError("Handle must contain at least one non-whitespace character other than '@'")
      return
    }
    setHandleError(null)

    setIsSubmitting(true)
    try {
      const trimmedUrl = url.trim()
      const newAccount = await addSocialAccount(brandId, {
        platform,
        raw_handle: trimmedHandle,
        url: trimmedUrl.length > 0 ? trimmedUrl : null,
        is_verified: isVerified,
      })

      // Reset form and notify parent
      setRawHandle('')
      setUrl('')
      setIsVerified(false)
      onSuccess(newAccount)
      onClose()
    } catch (err: unknown) {
      // Preserve form input and display meaningful API error message (e.g. 409 duplicate)
      const errorMsg = getApiErrorMessage(err, 'Failed to register official social account')
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
      aria-labelledby="add-social-modal-title"
    >
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black/60 backdrop-blur-sm transition-opacity"
        onClick={handleClose}
        aria-hidden="true"
      />

      {/* Modal Dialog Card */}
      <div className="relative w-full max-w-lg rounded-md border border-[#E5E5E2] bg-white p-6 shadow-xl transition-all z-10 animate-in fade-in zoom-in-95 duration-150">
        {/* Header */}
        <div className="flex items-start justify-between pb-4 border-b border-[#E5E5E2]">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded bg-[#111111] text-white flex items-center justify-center flex-shrink-0">
              <Share2 className="w-4 h-4 text-white" />
            </div>
            <div>
              <h2
                id="add-social-modal-title"
                className="text-base font-semibold text-[#111111] tracking-tight"
              >
                Register Official Social Account
              </h2>
              <p className="text-xs text-[#525252] mt-0.5">
                Add an official profile to whitelist it from impersonation detections.
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

        {/* API Error Banner (Handles 409 Conflict, 422, etc.) */}
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
          {/* Platform Selector */}
          <div className="space-y-1.5">
            <label
              htmlFor="social-platform-select"
              className="block text-xs font-medium text-[#525252] tracking-wide"
            >
              Social Media Platform *
            </label>
            <select
              id="social-platform-select"
              value={platform}
              onChange={(e) => setPlatform(e.target.value as SocialPlatform)}
              disabled={isSubmitting}
              className="flex h-9 w-full rounded-md border border-[#E5E5E2] bg-white px-3 py-1.5 text-xs text-[#111111] focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-[#111111] focus-visible:border-[#111111] disabled:opacity-50"
            >
              {SUPPORTED_PLATFORMS.map((p) => (
                <option key={p.value} value={p.value}>
                  {p.label}
                </option>
              ))}
            </select>
          </div>

          {/* Account Handle */}
          <div>
            <Input
              id="social-handle-input"
              label="Account Handle *"
              placeholder="e.g. @Nike or nike"
              value={rawHandle}
              onChange={(e) => {
                setRawHandle(e.target.value)
                if (handleError) setHandleError(null)
              }}
              error={handleError || undefined}
              disabled={isSubmitting}
              autoFocus
              maxLength={255}
            />
            {normalizedPreview ? (
              <p className="text-[11px] font-mono text-[#525252] mt-1 flex items-center gap-1.5">
                <span className="w-1.5 h-1.5 rounded-full bg-[#111111]" />
                Backend normalized index: <strong className="text-[#111111]">@{normalizedPreview}</strong>
              </p>
            ) : (
              <p className="text-[11px] text-[#858585] mt-1">
                Enter handle with or without &apos;@&apos;. Leading &apos;@&apos; will be normalized by the backend.
              </p>
            )}
          </div>

          {/* Profile URL */}
          <div>
            <Input
              id="social-url-input"
              label="Direct Profile URL (Optional)"
              type="url"
              placeholder="https://x.com/Nike"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              disabled={isSubmitting}
            />
            <p className="text-[11px] text-[#858585] mt-1">
              Direct web address to the legitimate social profile page.
            </p>
          </div>

          {/* Verified Badge Checkbox */}
          <div className="pt-2">
            <label className="flex items-start gap-2.5 cursor-pointer p-3 rounded-md bg-[#F0F0ED] border border-[#E5E5E2]">
              <input
                type="checkbox"
                checked={isVerified}
                onChange={(e) => setIsVerified(e.target.checked)}
                disabled={isSubmitting}
                className="mt-0.5 h-4 w-4 rounded border-[#E5E5E2] text-[#111111] focus:ring-[#111111]"
              />
              <div className="text-xs">
                <span className="font-medium text-[#111111] flex items-center gap-1.5">
                  Platform-Verified Status
                  {isVerified && (
                    <span className="inline-flex items-center gap-0.5 text-[10px] text-[#2563EB] font-mono">
                      <Check className="w-3 h-3" /> Badge active
                    </span>
                  )}
                </span>
                <p className="text-[#525252] text-[11px] mt-0.5 leading-snug">
                  Mark this if the account holds an official verification badge (blue check, gold check) on the platform.
                </p>
              </div>
            </label>
          </div>

          {/* Actions */}
          <div className="pt-4 border-t border-[#E5E5E2] flex items-center justify-end gap-2.5">
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
              disabled={isSubmitting || !cleanedHandle}
              icon={
                isSubmitting ? (
                  <Loader2 className="w-4 h-4 animate-spin text-white" />
                ) : undefined
              }
            >
              {isSubmitting ? 'Registering Account...' : 'Register Social Account'}
            </Button>
          </div>
        </form>
      </div>
    </div>
  )
}
