import React from 'react'
import { cn } from '../../lib/utils'

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'destructive'
  size?: 'sm' | 'md' | 'lg'
  icon?: React.ReactNode
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = 'primary', size = 'md', icon, children, disabled, ...props }, ref) => {
    const baseStyles =
      'inline-flex items-center justify-center font-medium rounded-md transition-colors duration-150 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#111111] focus-visible:ring-offset-2 focus-visible:ring-offset-[#F7F7F5] disabled:pointer-events-none disabled:opacity-40 select-none'

    const variants = {
      primary:
        'bg-[#111111] text-white hover:bg-[#303030] active:bg-[#000000] border border-[#111111]',
      secondary:
        'bg-[#F0F0ED] text-[#111111] border border-[#E5E5E2] hover:bg-[#E5E5E2] active:bg-[#DCDCD8]',
      outline:
        'bg-white text-[#111111] border border-[#E5E5E2] hover:bg-[#F7F7F5] hover:border-[#D0D0CD] active:bg-[#F0F0ED]',
      ghost:
        'bg-transparent text-[#525252] hover:text-[#111111] hover:bg-[#F0F0ED] active:bg-[#E5E5E2]',
      destructive:
        'bg-[#FEF2F2] text-[#B91C1C] border border-[#FECACA] hover:bg-[#FEE2E2] active:bg-[#FCA5A5]/40',
    }

    const sizes = {
      sm: 'h-8 px-3 text-xs gap-1.5',
      md: 'h-9 px-4 text-xs tracking-wide gap-2',
      lg: 'h-10 px-5 text-sm gap-2.5',
    }

    return (
      <button
        ref={ref}
        disabled={disabled}
        className={cn(baseStyles, variants[variant], sizes[size], className)}
        {...props}
      >
        {icon && <span className="flex-shrink-0">{icon}</span>}
        {children}
      </button>
    )
  },
)

Button.displayName = 'Button'
