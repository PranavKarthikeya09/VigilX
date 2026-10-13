import { useState, useEffect, useCallback } from 'react'
import { AlertTriangle, Loader2, X } from 'lucide-react'
import { Button } from '../ui/Button'
import { deleteOfficialApp, getApiErrorMessage } from '../../services/brandsApi'
import type { OfficialApp, AppStore } from '../../types/brand'

export interface DeleteOfficialAppModalProps {
  brandId: string
  app: OfficialApp | null
  isOpen: boolean
  onClose: () => void
  onSuccess: (deletedAppId: string) => void
}

const STORE_LABELS: Record<AppStore, string> = {
  google_play: 'Google Play',
  app_store: 'Apple App Store',
}

export function DeleteOfficialAppModal({
  brandId,
  app,
  isOpen,
  onClose,
  onSuccess,
}: DeleteOfficialAppModalProps) {
  const [isDeleting, setIsDeleting] = useState(false)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)

  const handleClose = useCallback(() => {
    if (isDeleting) return
    setErrorMessage(null)
    onClose()
  }, [isDeleting, onClose])

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen && !isDeleting) {
        handleClose()
      }
    }
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [isOpen, isDeleting, handleClose])

  if (!isOpen || !app) return null

  const handleDelete = async () => {
    setIsDeleting(true)
    setErrorMessage(null)
    try {
      // DELETE /api/v1/brands/{brand_id}/apps/{app_id} -> returns HTTP 204 No Content
      await deleteOfficialApp(brandId, app.id)
      onSuccess(app.id)
      onClose()
    } catch (err: unknown) {
      const errorMsg = getApiErrorMessage(err, 'Failed to remove mobile application')
      setErrorMessage(errorMsg)
    } finally {
      setIsDeleting(false)
    }
  }

  const storeDisplayName = STORE_LABELS[app.store] || app.store

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6"
      role="dialog"
      aria-modal="true"
      aria-labelledby="delete-app-modal-title"
    >
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black/60 backdrop-blur-sm transition-opacity"
        onClick={handleClose}
        aria-hidden="true"
      />

      {/* Modal Card */}
      <div className="relative w-full max-w-md rounded-md border border-[#E5E5E2] bg-white p-6 shadow-xl transition-all z-10 animate-in fade-in zoom-in-95 duration-150">
        <div className="flex items-start justify-between pb-3">
          <div className="w-10 h-10 rounded-full bg-[#FEF2F2] border border-[#FECACA] flex items-center justify-center text-[#DC2626] flex-shrink-0">
            <AlertTriangle className="w-5 h-5 text-[#DC2626]" />
          </div>
          <button
            type="button"
            onClick={handleClose}
            disabled={isDeleting}
            className="p-1 rounded text-[#858585] hover:text-[#111111] hover:bg-[#F0F0ED] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#111111] disabled:opacity-50"
            aria-label="Cancel deletion"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="mt-2 space-y-2">
          <h2 id="delete-app-modal-title" className="text-base font-semibold text-[#111111]">
            Remove Official Mobile App?
          </h2>
          <p className="text-xs text-[#525252] leading-relaxed">
            Are you sure you want to remove <strong className="text-[#111111]">{app.name}</strong> (by{' '}
            <span className="font-semibold text-[#111111]">{app.developer_name}</span> on{' '}
            <span className="font-semibold text-[#111111]">{storeDisplayName}</span>) from this brand&apos;s registered official assets?
          </p>
          <div className="p-3 rounded-md bg-[#F0F0ED] border border-[#E5E5E2] text-[11px] text-[#525252] leading-snug">
            <strong className="text-[#111111]">Impact: </strong>
            This app listing will no longer be excluded from potential impersonation alerts during store surveillance crawls.
          </div>
        </div>

        {/* Error message */}
        {errorMessage && (
          <div
            className="mt-3 p-3 rounded-md bg-[#FEF2F2] border border-[#FECACA] text-xs text-[#B91C1C]"
            role="alert"
          >
            {errorMessage}
          </div>
        )}

        {/* Actions */}
        <div className="mt-5 pt-3 border-t border-[#E5E5E2] flex items-center justify-end gap-2.5">
          <Button
            type="button"
            variant="outline"
            size="md"
            onClick={handleClose}
            disabled={isDeleting}
          >
            Keep App
          </Button>
          <Button
            type="button"
            variant="destructive"
            size="md"
            onClick={handleDelete}
            disabled={isDeleting}
            icon={isDeleting ? <Loader2 className="w-4 h-4 animate-spin" /> : undefined}
          >
            {isDeleting ? 'Removing...' : 'Remove Whitelist App'}
          </Button>
        </div>
      </div>
    </div>
  )
}
