import { useState, useEffect } from 'react'
import {
  ShieldCheck,
  Plus,
  RefreshCw,
  AlertCircle,
  CheckCircle2,
  ChevronLeft,
  ChevronRight,
  ArrowRight,
} from 'lucide-react'
import { PageHeading } from '../ui/PageHeading'
import { Card, CardContent } from '../ui/Card'
import { Badge } from '../ui/Badge'
import { Button } from '../ui/Button'
import { BrandCard } from '../brands/BrandCard'
import { BrandCreateModal } from '../brands/BrandCreateModal'
import { BrandDetailView } from '../brands/BrandDetailView'
import { getBrands, getApiErrorMessage } from '../../services/brandsApi'
import type { Brand, PaginationMeta } from '../../types/brand'

export interface BrandsAndAssetsViewProps {
  initialSelectedBrandId?: string | null
  onBrandSelect?: (brand: Brand | null) => void
}

export function BrandsAndAssetsView({
  initialSelectedBrandId = null,
  onBrandSelect,
}: BrandsAndAssetsViewProps) {
  const [brands, setBrands] = useState<Brand[]>([])
  const [pagination, setPagination] = useState<PaginationMeta>({
    page: 1,
    page_size: 20,
    total_items: 0,
    total_pages: 0,
  })
  const [selectedBrand, setSelectedBrand] = useState<Brand | null>(null)
  const [activeDetailBrandId, setActiveDetailBrandId] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)
  const [successBanner, setSuccessBanner] = useState<string | null>(null)
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false)
  const [currentPage, setCurrentPage] = useState(1)
  const [refreshTrigger, setRefreshTrigger] = useState(0)

  // Fetch brands from FastAPI backend synchronized with pagination
  useEffect(() => {
    let isCancelled = false

    const loadBrands = async () => {
      try {
        const response = await getBrands(currentPage, 20)
        if (!isCancelled) {
          setBrands(response.items)
          setPagination(response.pagination)
          setErrorMessage(null)

          // Maintain or sync selected brand
          if (response.items.length > 0) {
            setSelectedBrand((prev) => {
              const currentId = prev?.id || initialSelectedBrandId
              const matched = currentId
                ? response.items.find((b) => b.id === currentId)
                : response.items[0]
              const finalBrand = matched || response.items[0]
              onBrandSelect?.(finalBrand)
              return finalBrand
            })
          } else {
            setSelectedBrand(null)
            onBrandSelect?.(null)
          }
        }
      } catch (err: unknown) {
        if (!isCancelled) {
          const errorMsg = getApiErrorMessage(err, 'Failed to fetch brand registry')
          setErrorMessage(errorMsg)
        }
      } finally {
        if (!isCancelled) {
          setIsLoading(false)
        }
      }
    }

    loadBrands()
    return () => {
      isCancelled = true
    }
  }, [currentPage, initialSelectedBrandId, onBrandSelect, refreshTrigger])

  // Explicit user trigger for refresh button
  const handleManualRefresh = () => {
    setIsLoading(true)
    setErrorMessage(null)
    setRefreshTrigger((prev) => prev + 1)
  }

  // Handle successful brand registration
  const handleBrandCreated = (newBrand: Brand) => {
    setIsCreateModalOpen(false)
    setSuccessBanner(`Brand profile "${newBrand.name}" registered successfully.`)
    setSelectedBrand(newBrand)
    onBrandSelect?.(newBrand)
    setIsLoading(true)
    setCurrentPage(1)
    setRefreshTrigger((prev) => prev + 1)

    // Clear success banner after 6 seconds
    setTimeout(() => {
      setSuccessBanner(null)
    }, 6000)
  }

  const handleSelectBrand = (brand: Brand) => {
    setSelectedBrand(brand)
    setActiveDetailBrandId(brand.id)
    onBrandSelect?.(brand)
  }

  // If a brand is selected for detail inspection, render the full BrandDetailView
  if (activeDetailBrandId) {
    return (
      <BrandDetailView
        brandId={activeDetailBrandId}
        onBack={() => setActiveDetailBrandId(null)}
      />
    )
  }

  return (
    <div className="space-y-8 animate-in fade-in duration-150">
      {/* 1. View Header with Action Button */}
      <PageHeading
        title="Brands & Assets"
        eyebrow="Identity Registry"
        description="Catalog your brand's digital footprints. Official handles and mobile application package IDs registered here establish the whitelist exclusion baseline for the impersonation detection engine."
        badge={
          <Badge variant="dark">
            {pagination.total_items} Enrolled
          </Badge>
        }
        action={
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="md"
              icon={<RefreshCw className={`w-3.5 h-3.5 text-[#525252] ${isLoading ? 'animate-spin' : ''}`} />}
              onClick={handleManualRefresh}
              disabled={isLoading}
              title="Refresh list"
            >
              Refresh
            </Button>
            <Button
              variant="primary"
              size="md"
              icon={<Plus className="w-4 h-4 text-white" />}
              onClick={() => setIsCreateModalOpen(true)}
            >
              Add Brand
            </Button>
          </div>
        }
      />

      {/* 2. Success Banner */}
      {successBanner && (
        <div
          className="p-3.5 rounded-md bg-[#F0FDF4] border border-[#BBF7D0] flex items-center justify-between text-xs text-[#15803D] animate-in fade-in duration-200"
          role="status"
        >
          <div className="flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-[#15803D] flex-shrink-0" />
            <span className="font-medium">{successBanner}</span>
          </div>
          <button
            onClick={() => setSuccessBanner(null)}
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
              <p className="font-semibold">Unable to load brand registry</p>
              <p className="text-[#525252] mt-0.5">{errorMessage}</p>
            </div>
          </div>
          <Button
            variant="outline"
            size="sm"
            onClick={handleManualRefresh}
            className="flex-shrink-0 ml-3"
          >
            Retry
          </Button>
        </div>
      )}

      {/* 4. Brand List Section */}
      <section aria-label="Enrolled Brand Profiles">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-sm font-semibold uppercase tracking-wider font-mono text-[#858585]">
            Protected Brand Entities ({pagination.total_items})
          </h2>
          {selectedBrand && (
            <span className="text-xs text-[#525252]">
              Active Selection: <strong className="text-[#111111]">{selectedBrand.name}</strong>
            </span>
          )}
        </div>

        {/* Loading Skeleton State */}
        {isLoading && brands.length === 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {[1, 2, 3].map((i) => (
              <Card key={i} className="p-5 space-y-3 animate-pulse bg-white">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded bg-[#F0F0ED]" />
                  <div className="space-y-1.5 flex-1">
                    <div className="h-4 bg-[#F0F0ED] rounded w-3/4" />
                    <div className="h-3 bg-[#F0F0ED] rounded w-1/2" />
                  </div>
                </div>
                <div className="h-8 bg-[#F0F0ED] rounded mt-4" />
              </Card>
            ))}
          </div>
        ) : brands.length === 0 && !isLoading && !errorMessage ? (
          /* Empty State */
          <Card className="border-dashed border-[#DCDCD8] bg-white">
            <CardContent className="py-16 text-center space-y-4">
              <div className="w-14 h-14 rounded-full bg-[#F0F0ED] border border-[#E5E5E2] flex items-center justify-center mx-auto text-[#111111]">
                <ShieldCheck className="w-7 h-7 text-[#111111]" />
              </div>
              <div className="space-y-1.5 max-w-md mx-auto">
                <h3 className="text-base font-semibold text-[#111111]">No Protected Brands Enrolled</h3>
                <p className="text-xs text-[#525252] leading-relaxed">
                  Register your canonical brand name and official homepage to initialize impersonation perimeter surveillance.
                </p>
              </div>
              <div className="pt-2">
                <Button
                  variant="primary"
                  size="md"
                  icon={<Plus className="w-4 h-4 text-white" />}
                  onClick={() => setIsCreateModalOpen(true)}
                >
                  Add Your First Brand
                </Button>
              </div>
            </CardContent>
          </Card>
        ) : (
          /* Populated Brand Grid */
          <div className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {brands.map((brand) => (
                <BrandCard
                  key={brand.id}
                  brand={brand}
                  isSelected={selectedBrand?.id === brand.id}
                  onSelect={handleSelectBrand}
                />
              ))}
            </div>

            {/* Pagination Controls */}
            {pagination.total_pages > 1 && (
              <div className="flex items-center justify-between pt-4 border-t border-[#E5E5E2] text-xs text-[#525252]">
                <span>
                  Showing Page {pagination.page} of {pagination.total_pages} ({pagination.total_items} total)
                </span>
                <div className="flex items-center gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setCurrentPage((prev) => Math.max(1, prev - 1))}
                    disabled={currentPage <= 1 || isLoading}
                    icon={<ChevronLeft className="w-3.5 h-3.5" />}
                  >
                    Previous
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setCurrentPage((prev) => Math.min(pagination.total_pages, prev + 1))}
                    disabled={currentPage >= pagination.total_pages || isLoading}
                    icon={<ChevronRight className="w-3.5 h-3.5" />}
                  >
                    Next
                  </Button>
                </div>
              </div>
            )}
          </div>
        )}
      </section>

      {/* 5. Active Selection Action Banner */}
      {selectedBrand && (
        <section aria-label="Selected Brand Whitelist Actions" className="pt-4 border-t border-[#E5E5E2]">
          <div className="p-4 rounded-md bg-[#F0F0ED] border border-[#E5E5E2] flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div className="space-y-0.5">
              <div className="flex items-center gap-2">
                <span className="text-xs font-semibold text-[#111111]">
                  Active Selection: {selectedBrand.name}
                </span>
                <Badge variant="dark" className="text-[10px] font-mono py-0">
                  @{selectedBrand.normalized_name}
                </Badge>
              </div>
              <p className="text-xs text-[#525252]">
                {selectedBrand.website || 'No website registered'} &bull; Inspect canonical identity details, whitelist official social handles, and configure surveillance exclusions.
              </p>
            </div>
            <Button
              variant="primary"
              size="sm"
              icon={<ArrowRight className="w-3.5 h-3.5 text-white" />}
              onClick={() => setActiveDetailBrandId(selectedBrand.id)}
              className="flex-shrink-0"
            >
              Open Brand Details
            </Button>
          </div>
        </section>
      )}

      {/* 6. Accessible Create Brand Modal Dialog */}
      <BrandCreateModal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        onSuccess={handleBrandCreated}
      />
    </div>
  )
}
