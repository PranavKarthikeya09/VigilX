import React from 'react'
import { cn } from '../../lib/utils'

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string
  error?: string
  hint?: string
}

export const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, type = 'text', label, error, hint, id, disabled, ...props }, ref) => {
    const inputId = id || (label ? label.toLowerCase().replace(/\s+/g, '-') : undefined)

    return (
      <div className="w-full space-y-1.5">
        {label && (
          <label
            htmlFor={inputId}
            className="block text-xs font-medium text-[#525252] tracking-wide"
          >
            {label}
          </label>
        )}
        <input
          id={inputId}
          type={type}
          ref={ref}
          disabled={disabled}
          className={cn(
            'flex h-9 w-full rounded-md border border-[#E5E5E2] bg-white px-3 py-1.5 text-xs text-[#111111]',
            'placeholder:text-[#858585] transition-colors',
            'focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-[#111111] focus-visible:border-[#111111]',
            'disabled:cursor-not-allowed disabled:opacity-50 disabled:bg-[#F0F0ED]',
            error && 'border-[#DC2626] focus-visible:ring-[#DC2626] focus-visible:border-[#DC2626]',
            className,
          )}
          {...props}
        />
        {error ? (
          <p className="text-[11px] text-[#DC2626] font-medium">{error}</p>
        ) : hint ? (
          <p className="text-[11px] text-[#858585]">{hint}</p>
        ) : null}
      </div>
    )
  },
)

Input.displayName = 'Input'
