import React from 'react'
import { cn } from '../../lib/utils'

export interface PageHeadingProps {
  title: string
  description?: string
  eyebrow?: string
  badge?: React.ReactNode
  action?: React.ReactNode
  className?: string
}

export function PageHeading({
  title,
  description,
  eyebrow,
  badge,
  action,
  className,
}: PageHeadingProps) {
  return (
    <div
      className={cn(
        'flex flex-col gap-3 pb-6 md:flex-row md:items-center md:justify-between border-b border-[#E5E5E2]',
        className,
      )}
    >
      <div className="space-y-1">
        {eyebrow && (
          <p className="text-[11px] font-mono tracking-wider text-[#858585] uppercase">
            {eyebrow}
          </p>
        )}
        <div className="flex items-center gap-3">
          <h1 className="text-xl md:text-2xl font-bold tracking-tight text-[#111111]">{title}</h1>
          {badge}
        </div>
        {description && (
          <p className="text-xs md:text-sm text-[#525252] max-w-2xl leading-relaxed">
            {description}
          </p>
        )}
      </div>
      {action && <div className="flex items-center gap-2 flex-shrink-0">{action}</div>}
    </div>
  )
}
