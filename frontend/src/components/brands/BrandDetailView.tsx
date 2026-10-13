import { useState, useEffect, useCallback } from 'react'
import {
  ArrowLeft,
  RefreshCw,
  AlertCircle,
  Globe,
  Layers,
  Smartphone,
  ExternalLink,
  Calendar,
  CheckCircle2,
} from 'lucide-react'
import { Card } from '../ui/Card'
import { Badge } from '../ui/Badge'
import { Button } from '../ui/Button'
import { OfficialSocialList } from '../assets/OfficialSocialList'
import { AddSocialAccountModal } from '../assets/AddSocialAccountModal'
import { DeleteSocialAccountModal } from '../assets/DeleteSocialAccountModal'
import { OfficialAppList } from '../assets/OfficialAppList'
import { AddOfficialAppModal } from '../assets/AddOfficialAppModal'
import { DeleteOfficialAppModal } from '../assets/DeleteOfficialAppModal'
import {
  getBrandById,
  getSocialAccounts,
  getOfficialApps,
  getApiErrorMessage,
} from '../../services/brandsApi'
import type {
  BrandDetail,
  OfficialSocialAccount,
  OfficialApp,
} from '../../types/brand'

export interface BrandDetailViewProps {
  brandId: string
  onBack: () => void
}

export function BrandDetailView({ brandId, onBack }: BrandDetailViewProps) {
  const [brandDetail, setBrandDetail] = useState<BrandDetail | null>(null)
  const [socialAccounts, setSocialAccounts] = useState<OfficialSocialAccount[]>([])
  const [apps, setApps] = useState<OfficialApp[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)
  const [successMessage, setSuccessMessage] = useState<string | null>(null)

  // Social account modals state
  const [isAddSocialModalOpen, setIsAddSocialModalOpen] = useState(false)
  const [accountToDelete, setAccountToDelete] = useState<OfficialSocialAccount | null>(null)
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false)

  // Mobile app modals state
  const [isAddAppModalOpen, setIsAddAppModalOpen] = useState(false)
  const [appToDelete, setAppToDelete] = useState<OfficialApp | null>(null)
  const [isDeleteAppModalOpen, setIsDeleteAppModalOpen] = useState(false)

  // Fetch brand details, social accounts, and mobile apps scoped to current brandId
  const loadBrandData = useCallback(async () => {
    setIsLoading(true)
    setErrorMessage(null)

    try {
      const [detailRes, accountsRes, appsRes] = await Promise.all([
        getBrandById(brandId),
        getSocialAccounts(brandId),
        getOfficialApps(brandId),
      ])

      setBrandDetail(detailRes)
      setSocialAccounts(accountsRes)
      setApps(appsRes)
    } catch (err: unknown) {
      const errorMsg = getApiErrorMessage(err, 'Failed to retrieve brand details')
      setErrorMessage(errorMsg)
    } finally {
      setIsLoading(false)
    }
  }, [brandId])

  // Synchronize loading on brandId change and clear old brand data to prevent leakage
  useEffect(() => {
    let isMounted = true

    const executeLoad = async () => {
      setIsLoading(true)
      setErrorMessage(null)
      // Clear previous brand data immediately
      setBrandDetail(null)
      setSocialAccounts([])
      setApps([])

      try {
        const [detailRes, accountsRes, appsRes] = await Promise.all([
          getBrandById(brandId),
          getSocialAccounts(brandId),
          getOfficialApps(brandId),
        ])

        if (isMounted) {
          setBrandDetail(detailRes)
          setSocialAccounts(accountsRes)
          setApps(appsRes)
        }
      } catch (err: unknown) {
        if (isMounted) {
          const errorMsg = getApiErrorMessage(err, 'Failed to retrieve brand details')
          setErrorMessage(errorMsg)
        }
      } finally {
        if (isMounted) {
          setIsLoading(false)
        }
      }
    }

    void executeLoad()
    return () => {
      isMounted = false
    }
  }, [brandId])

  // Callbacks for social account operations
  const handleAccountAdded = (newAccount: OfficialSocialAccount) => {
    setSocialAccounts((prev) => [...prev, newAccount])
    setBrandDetail((prev) =>
      prev
        ? {
            ...prev,
            official_social_count: prev.official_social_count + 1,
          }
        : null,
    )
    setSuccessMessage(`Account "${newAccount.raw_handle}" registered to official whitelist.`)
    setTimeout(() => setSuccessMessage(null), 5000)
  }

  const handleAccountDeleted = (deletedId: string) => {
    setSocialAccounts((prev) => prev.filter((acc) => acc.id !== deletedId))
    setBrandDetail((prev) =>
      prev
        ? {
            ...prev,
            official_social_count: Math.max(0, prev.official_social_count - 1),
          }
        : null,
    )
    setSuccessMessage('Official social account removed from whitelist.')
    setTimeout(() => setSuccessMessage(null), 5000)
  }

  const handleDeleteRequest = (account: OfficialSocialAccount) => {
    setAccountToDelete(account)
    setIsDeleteModalOpen(true)
  }

  // Callbacks for mobile app operations
  const handleAppAdded = (newApp: OfficialApp) => {
    setApps((prev) => [...prev, newApp])
    setBrandDetail((prev) =>
      prev
        ? {
            ...prev,
            official_app_count: prev.official_app_count + 1,
          }
        : null,
    )
    setSuccessMessage(`Mobile app "${newApp.name}" registered to official whitelist.`)
    setTimeout(() => setSuccessMessage(null), 5000)
  }

  const handleAppDeleted = (deletedId: string) => {
    setApps((prev) => prev.filter((app) => app.id !== deletedId))
    setBrandDetail((prev) =>
      prev
        ? {
            ...prev,
            official_app_count: Math.max(0, prev.official_app_count - 1),
          }
        : null,
    )
    setSuccessMessage('Official mobile app removed from whitelist.')
    setTimeout(() => setSuccessMessage(null), 5000)
  }

  const handleDeleteAppRequest = (app: OfficialApp) => {
    setAppToDelete(app)
    setIsDeleteAppModalOpen(true)
  }

  return (
    <div className="space-y-8 animate-in fade-in duration-150">
      {/* 1. Header with Back Button and Brand Details */}
      <div className="flex flex-col gap-3 pb-6 md:flex-row md:items-start md:justify-between border-b border-[#E5E5E2]">
        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              icon={<ArrowLeft className="w-3.5 h-3.5 text-[#111111]" />}
              onClick={onBack}
              className="text-xs font-mono"
            >
              Back to Brands
            </Button>
            <span className="text-xs font-mono text-[#858585]">/</span>
            <span className="text-xs font-mono text-[#858585] uppercase">
              Brand Profile Details
            </span>
          </div>

          <div className="flex flex-wrap items-center gap-3 pt-1">
            <h1 className="text-2xl font-bold tracking-tight text-[#111111]">
              {brandDetail ? brandDetail.name : 'Loading brand...'}
            </h1>
            {brandDetail && (
              <>
                <Badge variant="dark" dot>
                  @{brandDetail.normalized_name}
                </Badge>
                <span className="flex items-center gap-1.5 text-xs font-mono text-[#858585]">
                  <Calendar className="w-3.5 h-3.5 text-[#525252]" />
                  Enrolled{' '}
                  {new Date(brandDetail.created_at).toLocaleDateString(undefined, {
                    month: 'short',
                    day: 'numeric',
                    year: 'numeric',
                  })}
                </span>
              </>
            )}
          </div>

          <p className="text-xs md:text-sm text-[#525252] max-w-2xl leading-relaxed">
            Official brand identity and verified asset exclusion registry. Entities cataloged here are whitelisted by the detection engine to prevent false impersonation alerts.
          </p>
        </div>

        <div className="flex items-center gap-2 flex-shrink-0 pt-2 md:pt-0">
          <Button
            variant="outline"
            size="md"
            icon={<RefreshCw className={`w-3.5 h-3.5 text-[#525252] ${isLoading ? 'animate-spin' : ''}`} />}
            onClick={() => void loadBrandData()}
            disabled={isLoading}
            title="Refresh details"
          >
            Refresh
          </Button>
        </div>
      </div>

      {/* 2. Success Banner */}
      {successMessage && (
        <div
          className="p-3.5 rounded-md bg-[#F0FDF4] border border-[#BBF7D0] flex items-center justify-between text-xs text-[#15803D] animate-in fade-in duration-200"
          role="status"
        >
          <div className="flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-[#15803D] flex-shrink-0" />
            <span className="font-medium">{successMessage}</span>
          </div>
          <button
            onClick={() => setSuccessMessage(null)}
            className="text-[#15803D] hover:opacity-75 text-xs font-mono"
          >
            Dismiss
          </button>
        </div>
      )}

      {/* 3. Error Banner */}
      {errorMessage && (
        <div
          className="p-4 rounded-md bg-[#FEF2F2] border border-[#FECACA] flex items-start justify-between text-xs text-[#B91C1C]"
          role="alert"
        >
          <div className="flex items-start gap-2.5">
            <AlertCircle className="w-4 h-4 text-[#DC2626] flex-shrink-0 mt-0.5" />
            <div>
              <p className="font-semibold">Failed to load brand data</p>
              <p className="text-[#525252] mt-0.5">{errorMessage}</p>
            </div>
          </div>
          <Button
            variant="outline"
            size="sm"
            onClick={() => void loadBrandData()}
            className="flex-shrink-0 ml-3"
          >
            Retry
          </Button>
        </div>
      )}

      {/* 4. Brand Summary Metadata Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Canonical Identity */}
        <Card className="p-4 space-y-1.5">
          <div className="flex items-center justify-between text-[11px] font-mono uppercase text-[#858585]">
            <span>Canonical Name</span>
            <Layers className="w-3.5 h-3.5 text-[#111111]" />
          </div>
          <p className="text-base font-bold text-[#111111] truncate">
            {brandDetail ? brandDetail.name : '—'}
          </p>
          <p className="text-[11px] font-mono text-[#525252] truncate">
            {brandDetail ? `@${brandDetail.normalized_name}` : '—'}
          </p>
        </Card>

        {/* Canonical Website */}
        <Card className="p-4 space-y-1.5">
          <div className="flex items-center justify-between text-[11px] font-mono uppercase text-[#858585]">
            <span>Domain Link</span>
            <Globe className="w-3.5 h-3.5 text-[#111111]" />
          </div>
          {brandDetail?.website ? (
            <a
              href={brandDetail.website}
              target="_blank"
              rel="noopener noreferrer"
              className="text-xs font-semibold text-[#111111] hover:underline flex items-center gap-1 truncate pt-1"
            >
              <span className="truncate">{brandDetail.website.replace(/^https?:\/\//i, '')}</span>
              <ExternalLink className="w-3 h-3 flex-shrink-0 opacity-70" />
            </a>
          ) : (
            <p className="text-xs text-[#858585] italic pt-1">No domain listed</p>
          )}
          <p className="text-[11px] text-[#858585]">Exclusion reference URL</p>
        </Card>

        {/* Social Accounts Count */}
        <Card className="p-4 space-y-1.5">
          <div className="flex items-center justify-between text-[11px] font-mono uppercase text-[#858585]">
            <span>Social Handles</span>
            <span className="w-2 h-2 rounded-full bg-[#111111]" />
          </div>
          <p className="text-2xl font-bold font-mono text-[#111111]">
            {isLoading && !brandDetail ? '—' : socialAccounts.length}
          </p>
          <p className="text-[11px] text-[#525252]">Whitelisted profiles</p>
        </Card>

        {/* Mobile Apps Count (API Supported) */}
        <Card className="p-4 space-y-1.5">
          <div className="flex items-center justify-between text-[11px] font-mono uppercase text-[#858585]">
            <span>Mobile Apps</span>
            <Smartphone className="w-3.5 h-3.5 text-[#111111]" />
          </div>
          <p className="text-2xl font-bold font-mono text-[#111111]">
            {isLoading && !brandDetail ? '—' : apps.length}
          </p>
          <p className="text-[11px] text-[#525252]">Registered store listings</p>
        </Card>
      </div>

      {/* 5. Official Social Accounts Whitelist Section */}
      <section aria-label="Official Social Media Accounts">
        <OfficialSocialList
          accounts={socialAccounts}
          isLoading={isLoading}
          onAddAccount={() => setIsAddSocialModalOpen(true)}
          onDeleteAccount={handleDeleteRequest}
        />
      </section>

      {/* 6. Official Mobile Applications Whitelist Section */}
      <section aria-label="Official Mobile App Listings">
        <OfficialAppList
          apps={apps}
          isLoading={isLoading}
          onAddApp={() => setIsAddAppModalOpen(true)}
          onDeleteApp={handleDeleteAppRequest}
        />
      </section>

      {/* 7. Modal Dialogs */}
      <AddSocialAccountModal
        brandId={brandId}
        isOpen={isAddSocialModalOpen}
        onClose={() => setIsAddSocialModalOpen(false)}
        onSuccess={handleAccountAdded}
      />

      <DeleteSocialAccountModal
        brandId={brandId}
        account={accountToDelete}
        isOpen={isDeleteModalOpen}
        onClose={() => {
          setIsDeleteModalOpen(false)
          setAccountToDelete(null)
        }}
        onSuccess={handleAccountDeleted}
      />

      <AddOfficialAppModal
        brandId={brandId}
        isOpen={isAddAppModalOpen}
        onClose={() => setIsAddAppModalOpen(false)}
        onSuccess={handleAppAdded}
      />

      <DeleteOfficialAppModal
        brandId={brandId}
        app={appToDelete}
        isOpen={isDeleteAppModalOpen}
        onClose={() => {
          setIsDeleteAppModalOpen(false)
          setAppToDelete(null)
        }}
        onSuccess={handleAppDeleted}
      />
    </div>
  )
}

