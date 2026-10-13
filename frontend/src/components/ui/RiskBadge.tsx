import React from 'react'
import { cn } from '../../lib/utils'

export type RiskLevel = 'low' | 'medium' | 'high' | 'critical' | 'verified' | 'neutral'

export interface RiskBadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  level: RiskLevel
  score?: number
}

export function RiskBadge({ level, score, className, ...props }: RiskBadgeProps) {
  const styles: Record<RiskLevel, { container: string; dot: string; label: string }> = {
    low: {
      container: 'bg-[#F0FDF4] text-[#15803D] border-[#BBF7D0]',
      dot: 'bg-[#15803D]',
      label: 'Low Risk',
    },
    medium: {
      container: 'bg-[#FFFBEB] text-[#B45309] border-[#FDE68A]',
      dot: 'bg-[#B45309]',
      label: 'Medium Risk',
    },
    high: {
      container: 'bg-[#FEF2F2] text-[#DC2626] border-[#FECACA]',
      dot: 'bg-[#DC2626]',
      label: 'High Risk',
    },
    critical: {
      container: 'bg-[#FEF2F2] text-[#B91C1C] border-[#FCA5A5]',
      dot: 'bg-[#B91C1C]',
      label: 'Critical',
    },
    verified: {
      container: 'bg-[#EFF6FF] text-[#2563EB] border-[#BFDBFE]',
      dot: 'bg-[#2563EB]',
      label: 'Verified',
    },
    neutral: {
      container: 'bg-[#F0F0ED] text-[#737373] border-[#E5E5E2]',
      dot: 'bg-[#737373]',
      label: 'Neutral',
    },
  }

  const current = styles[level]

  return (
    <span
      className={cn(
        'inline-flex items-center gap-1.5 px-2 py-0.5 rounded text-[11px] font-medium border font-mono tracking-wider uppercase',
        current.container,
        className,
      )}
      {...props}
    >
      <span className={cn('w-1.5 h-1.5 rounded-full', current.dot)} />
      <span>{current.label}</span>
      {score !== undefined && (
        <span className="opacity-80 text-[10px] ml-0.5">({score})</span>
      )}
    </span>
  )
}
