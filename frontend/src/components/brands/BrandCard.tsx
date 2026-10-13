import { Globe, Calendar, Check, ExternalLink, Shield, ArrowRight } from 'lucide-react'
import { Card } from '../ui/Card'
import { Badge } from '../ui/Badge'
import { cn } from '../../lib/utils'
import type { Brand } from '../../types/brand'

export interface BrandCardProps {
  brand: Brand
  isSelected?: boolean
  onSelect: (brand: Brand) => void
}

export function BrandCard({ brand, isSelected = false, onSelect }: BrandCardProps) {
  const formattedDate = new Date(brand.created_at).toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })

  return (
    <Card
      className={cn(
        'p-5 transition-all text-left cursor-pointer relative',
        isSelected
          ? 'border-2 border-[#111111] shadow-sm bg-white ring-1 ring-[#111111]/10'
          : 'border border-[#E5E5E2] hover:border-[#D0D0CD] bg-white',
      )}
      onClick={() => onSelect(brand)}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault()
          onSelect(brand)
        }
      }}
      aria-pressed={isSelected}
    >
      {/* Top Header with Avatar & Selection Badge */}
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-md bg-[#F0F0ED] border border-[#E5E5E2] flex items-center justify-center font-bold text-sm text-[#111111] flex-shrink-0">
            {brand.name.slice(0, 2).toUpperCase()}
          </div>
          <div>
            <h3 className="text-sm font-semibold text-[#111111] tracking-tight truncate max-w-[200px] sm:max-w-[260px]">
              {brand.name}
            </h3>
            <p className="text-[11px] font-mono text-[#858585] mt-0.5">
              @{brand.normalized_name}
            </p>
          </div>
        </div>

        {isSelected ? (
          <Badge variant="dark" className="flex items-center gap-1 py-0.5 px-2">
            <Check className="w-3 h-3 text-white" />
            Active
          </Badge>
        ) : (
          <Badge variant="neutral" className="text-[10px]">
            Enrolled
          </Badge>
        )}
      </div>

      {/* Details Row: Website & Created Date */}
      <div className="mt-4 pt-3 border-t border-[#E5E5E2] space-y-2 text-xs">
        {brand.website ? (
          <div className="flex items-center gap-2 text-[#525252] truncate">
            <Globe className="w-3.5 h-3.5 text-[#858585] flex-shrink-0" />
            <a
              href={brand.website}
              target="_blank"
              rel="noopener noreferrer"
              onClick={(e) => e.stopPropagation()}
              className="text-xs hover:text-[#111111] hover:underline flex items-center gap-1 truncate"
            >
              <span className="truncate">{brand.website.replace(/^https?:\/\//i, '')}</span>
              <ExternalLink className="w-3 h-3 flex-shrink-0 opacity-70" />
            </a>
          </div>
        ) : (
          <div className="flex items-center gap-2 text-[#858585]">
            <Globe className="w-3.5 h-3.5 text-[#A3A3A3] flex-shrink-0" />
            <span className="text-[11px] italic">No canonical website</span>
          </div>
        )}

        <div className="flex items-center justify-between text-[11px] font-mono text-[#858585] pt-1">
          <span className="flex items-center gap-1.5">
            <Calendar className="w-3 h-3" />
            {formattedDate}
          </span>
          <span className="flex items-center gap-1 text-[#111111]">
            <Shield className="w-3 h-3 text-[#15803D]" />
            Whitelisted
          </span>
        </div>

        <div className="pt-2 border-t border-[#E5E5E2] flex items-center justify-between text-[11px] font-medium text-[#111111]">
          <span className="text-[#525252]">Whitelist & Assets</span>
          <span className="inline-flex items-center gap-1 font-mono text-[#111111] group-hover:underline">
            Manage Assets <ArrowRight className="w-3 h-3" />
          </span>
        </div>
      </div>
    </Card>
  )
}
