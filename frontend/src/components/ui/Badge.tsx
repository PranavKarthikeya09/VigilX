import React from 'react'
import { cn } from '../../lib/utils'

export interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: 'neutral' | 'dark' | 'success' | 'warning' | 'danger' | 'verified' | 'lime'
  dot?: boolean
}

export function Badge({
  className,
  variant = 'neutral',
  dot = false,
  children,
  ...props
}: BadgeProps) {
  const variants = {
    neutral: 'bg-[#F0F0ED] text-[#525252] border-[#E5E5E2]',
    dark: 'bg-[#111111] text-white border-[#111111]',
    lime: 'bg-[#111111] text-white border-[#111111]',
    success: 'bg-[#F0FDF4] text-[#15803D] border-[#BBF7D0]',
    warning: 'bg-[#FFFBEB] text-[#B45309] border-[#FDE68A]',
    danger: 'bg-[#FEF2F2] text-[#DC2626] border-[#FECACA]',
    verified: 'bg-[#EFF6FF] text-[#2563EB] border-[#BFDBFE]',
  }

  const dotColors = {
    neutral: 'bg-[#858585]',
    dark: 'bg-white',
    lime: 'bg-white',
    success: 'bg-[#15803D]',
    warning: 'bg-[#B45309]',
    danger: 'bg-[#DC2626]',
    verified: 'bg-[#2563EB]',
  }

  return (
    <span
      className={cn(
        'inline-flex items-center gap-1.5 px-2 py-0.5 rounded text-[11px] font-medium border tracking-wide uppercase font-mono',
        variants[variant],
        className,
      )}
      {...props}
    >
      {dot && <span className={cn('w-1.5 h-1.5 rounded-full', dotColors[variant])} />}
      {children}
    </span>
  )
}
