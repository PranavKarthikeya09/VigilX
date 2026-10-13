import React from 'react'
import { Card } from './Card'
import { cn } from '../../lib/utils'

export interface MetricCardProps {
  label: string
  value?: string | number | null
  description?: string
  helperText?: string
  icon?: React.ReactNode
  className?: string
}

export function MetricCard({
  label,
  value = '—',
  description,
  helperText,
  icon,
  className,
}: MetricCardProps) {
  const displayValue = value === null || value === undefined ? '—' : value
  const isNeutralPlaceholder = displayValue === '—'

  return (
    <Card className={cn('p-5 transition-colors hover:border-[#D0D0CD]', className)}>
      <div className="flex items-start justify-between">
        <p className="text-xs font-medium text-[#858585] uppercase tracking-wider font-mono">
          {label}
        </p>
        {icon && (
          <div className="p-2 rounded-md bg-[#F0F0ED] border border-[#E5E5E2] text-[#111111]">
            {icon}
          </div>
        )}
      </div>

      <div className="mt-3">
        <div
          className={cn(
            'text-2xl md:text-3xl font-bold tracking-tight',
            isNeutralPlaceholder ? 'text-[#858585] font-mono' : 'text-[#111111]',
          )}
        >
          {displayValue}
        </div>
        {description && (
          <p className="mt-1 text-xs text-[#525252] leading-snug">{description}</p>
        )}
        {helperText && (
          <p className="mt-2 text-[11px] text-[#858585] flex items-center gap-1.5 pt-2 border-t border-[#E5E5E2]">
            <span className="w-1.5 h-1.5 rounded-full bg-[#858585] flex-shrink-0" />
            {helperText}
          </p>
        )}
      </div>
    </Card>
  )
}
