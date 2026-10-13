import React, { useState, useEffect } from 'react'
import { X, Loader2, AlertCircle, Shield } from 'lucide-react'
import { Button } from '../ui/Button'
import { Input } from '../ui/Input'
import { createBrand, getApiErrorMessage } from '../../services/brandsApi'
import type { Brand } from '../../types/brand'

export interface BrandCreateModalProps {
  isOpen: boolean
  onClose: () => void
  onSuccess: (newBrand: Brand) => void
}

export function BrandCreateModal({ isOpen, onClose, onSuccess }: BrandCreateModalProps) {
  const [name, setName] = useState('')
  const [website, setWebsite] = useState('')
  const [nameError, setNameError] = useState<string | null>(null)
  const [apiError, setApiError] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  const handleClose = React.useCallback(() => {
    if (isSubmitting) return
    setName('')
    setWebsite('')
    setNameError(null)
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

    // Validation according to backend contract:
    // Name must be >= 2 characters after trimming whitespace
    const trimmedName = name.trim()
    if (trimmedName.length < 2) {
      setNameError('Brand name must contain at least 2 non-whitespace characters')
      return
    }
    setNameError(null)

    setIsSubmitting(true)
    try {
      const trimmedWebsite = website.trim()
      const newBrand = await createBrand({
        name: trimmedName,
        website: trimmedWebsite.length > 0 ? trimmedWebsite : null,
      })

      // On success, reset form and notify parent
      setName('')
      setWebsite('')
      setNameError(null)
      setApiError(null)
      onSuccess(newBrand)
      onClose()
    } catch (err: unknown) {
      // Preserve form input, display detailed backend error message
      const errorMsg = getApiErrorMessage(err, 'Failed to create brand profile')
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
      aria-labelledby="create-brand-modal-title"
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
              <Shield className="w-4 h-4 text-white" />
            </div>
            <div>
              <h2
                id="create-brand-modal-title"
                className="text-base font-semibold text-[#111111] tracking-tight"
              >
                Register Brand Profile
              </h2>
              <p className="text-xs text-[#525252] mt-0.5">
                Establish an official brand identity for impersonation monitoring.
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

        {/* API Error Banner (if submission fails) */}
        {apiError && (
          <div
            className="mt-4 p-3 rounded-md bg-[#FEF2F2] border border-[#FECACA] flex items-start gap-2.5 text-xs text-[#B91C1C]"
            role="alert"
          >
            <AlertCircle className="w-4 h-4 flex-shrink-0 mt-0.5 text-[#DC2626]" />
            <div className="leading-snug">
              <span className="font-semibold">Creation Error: </span>
              {apiError}
            </div>
          </div>
        )}

        {/* Form Body */}
        <form onSubmit={handleSubmit} className="mt-5 space-y-4">
          <div>
            <Input
              id="brand-name-input"
              label="Brand Name *"
              placeholder="e.g. Acme Corporation"
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
              Minimum 2 characters. Canonical name used for similarity algorithms.
            </p>
          </div>

          <div>
            <Input
              id="brand-website-input"
              label="Official Website (Optional)"
              type="url"
              placeholder="https://www.acme.com"
              value={website}
              onChange={(e) => setWebsite(e.target.value)}
              disabled={isSubmitting}
              maxLength={512}
            />
            <p className="text-[11px] text-[#858585] mt-1">
              Canonical domain used as reference during link and impersonation checks.
            </p>
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
              disabled={isSubmitting || name.trim().length < 2}
              icon={
                isSubmitting ? (
                  <Loader2 className="w-4 h-4 animate-spin text-white" />
                ) : undefined
              }
            >
              {isSubmitting ? 'Creating Profile...' : 'Create Brand Profile'}
            </Button>
          </div>
        </form>
      </div>
    </div>
  )
}
