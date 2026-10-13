import React, { useState } from 'react'
import {
  Shield,
  Lock,
  Mail,
  Eye,
  EyeOff,
  Loader2,
  AlertCircle,
  CheckCircle2,
  ArrowRight,
  ShieldCheck,
} from 'lucide-react'
import { supabase } from '../../services/supabase'
import { useAuth } from '../../context/useAuth'
import { Button } from '../ui/Button'

type AuthMode = 'sign-in' | 'sign-up'

export function AuthView() {
  const { isConfigured } = useAuth()
  const [mode, setMode] = useState<AuthMode>('sign-in')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)
  const [successMessage, setSuccessMessage] = useState<string | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setErrorMessage(null)
    setSuccessMessage(null)

    const trimmedEmail = email.trim()
    if (!trimmedEmail) {
      setErrorMessage('Please enter your email address.')
      return
    }

    if (!password) {
      setErrorMessage('Please enter your password.')
      return
    }

    if (password.length < 6) {
      setErrorMessage('Password must be at least 6 characters long.')
      return
    }

    setIsLoading(true)

    try {
      if (mode === 'sign-in') {
        const { error } = await supabase.auth.signInWithPassword({
          email: trimmedEmail,
          password,
        })

        if (error) {
          setErrorMessage(error.message || 'Invalid email or password.')
        }
      } else {
        // Sign-up / Create Account flow
        const { data, error } = await supabase.auth.signUp({
          email: trimmedEmail,
          password,
        })

        if (error) {
          setErrorMessage(error.message || 'Failed to create account.')
        } else if (data.user) {
          if (data.session) {
            // User auto-confirmed and session established
            setSuccessMessage('Account created and authenticated.')
          } else {
            // Email confirmation required by Supabase
            setSuccessMessage(
              'Registration successful! Please check your email to confirm your account before signing in.',
            )
            setMode('sign-in')
          }
        }
      }
    } catch (err: unknown) {
      const errStr = err instanceof Error ? err.message : 'An unexpected authentication error occurred.'
      setErrorMessage(errStr)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-[#F7F7F5] text-[#111111] flex flex-col justify-center items-center p-4 sm:p-6 lg:p-8">
      {/* Brand Header */}
      <div className="w-full max-w-md flex flex-col items-center text-center mb-8">
        <div className="w-12 h-12 rounded-lg bg-[#111111] text-white flex items-center justify-center shadow-md mb-4 ring-1 ring-black/5">
          <Shield className="w-6 h-6 text-white" />
        </div>
        <h1 className="text-2xl font-bold tracking-tight text-[#111111] font-mono">
          vigilX
        </h1>
        <p className="text-xs font-mono uppercase tracking-widest text-[#737373] mt-1">
          Digital Risk Protection Platform
        </p>
        <p className="text-xs text-[#525252] mt-2 max-w-xs leading-relaxed">
          Autonomous Brand Impersonation Detection across Social & App Ecosystems.
        </p>
      </div>

      {/* Auth Card */}
      <div className="w-full max-w-md bg-white rounded-lg border border-[#E5E5E2] shadow-sm p-6 sm:p-8">
        <div className="flex items-center justify-between pb-5 border-b border-[#E5E5E2] mb-6">
          <div>
            <h2 className="text-base font-semibold text-[#111111] tracking-tight">
              {mode === 'sign-in' ? 'Analyst Authentication' : 'Create Analyst Account'}
            </h2>
            <p className="text-xs text-[#737373] mt-0.5">
              {mode === 'sign-in'
                ? 'Sign in to access protected intelligence consoles.'
                : 'Register credentials for workspace monitoring access.'}
            </p>
          </div>
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-[#F0F0ED] text-[10px] font-mono text-[#525252] border border-[#E5E5E2]">
            <Lock className="w-3 h-3 text-[#525252]" />
            ES256
          </span>
        </div>

        {/* Missing Config Alert (if environment is unconfigured) */}
        {!isConfigured && (
          <div
            className="mb-5 p-3 rounded-md bg-[#FFFBEB] border border-[#FDE68A] flex items-start gap-2.5 text-xs text-[#92400E]"
            role="alert"
          >
            <AlertCircle className="w-4 h-4 flex-shrink-0 mt-0.5 text-[#D97706]" />
            <div className="leading-snug">
              <span className="font-semibold">Notice: </span>
              Supabase environment variables (<code className="font-mono">VITE_SUPABASE_URL</code>) are currently unconfigured or using placeholders.
            </div>
          </div>
        )}

        {/* Error Alert */}
        {errorMessage && (
          <div
            className="mb-5 p-3 rounded-md bg-[#FEF2F2] border border-[#FECACA] flex items-start gap-2.5 text-xs text-[#B91C1C] animate-in fade-in duration-150"
            role="alert"
          >
            <AlertCircle className="w-4 h-4 flex-shrink-0 mt-0.5 text-[#DC2626]" />
            <div className="leading-snug">
              <span className="font-semibold">Authentication Error: </span>
              {errorMessage}
            </div>
          </div>
        )}

        {/* Success Alert */}
        {successMessage && (
          <div
            className="mb-5 p-3 rounded-md bg-[#F0FDF4] border border-[#BBF7D0] flex items-start gap-2.5 text-xs text-[#166534] animate-in fade-in duration-150"
            role="status"
          >
            <CheckCircle2 className="w-4 h-4 flex-shrink-0 mt-0.5 text-[#16A34A]" />
            <div className="leading-snug">{successMessage}</div>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label
              htmlFor="auth-email-input"
              className="block text-xs font-medium text-[#525252] tracking-wide mb-1.5"
            >
              Email Address *
            </label>
            <div className="relative">
              <input
                id="auth-email-input"
                type="email"
                autoComplete="email"
                required
                disabled={isLoading}
                placeholder="analyst@vigilx.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="flex h-9 w-full rounded-md border border-[#E5E5E2] bg-white pl-9 pr-3 py-1.5 text-xs text-[#111111] placeholder:text-[#858585] transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-[#111111] focus-visible:border-[#111111] disabled:cursor-not-allowed disabled:opacity-50"
              />
              <Mail className="w-4 h-4 text-[#858585] absolute left-2.5 top-2.5 pointer-events-none" />
            </div>
          </div>

          <div>
            <label
              htmlFor="auth-password-input"
              className="block text-xs font-medium text-[#525252] tracking-wide mb-1.5"
            >
              Password *
            </label>
            <div className="relative">
              <input
                id="auth-password-input"
                type={showPassword ? 'text' : 'password'}
                autoComplete={mode === 'sign-in' ? 'current-password' : 'new-password'}
                required
                disabled={isLoading}
                placeholder="••••••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="flex h-9 w-full rounded-md border border-[#E5E5E2] bg-white pl-9 pr-9 py-1.5 text-xs text-[#111111] placeholder:text-[#858585] transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-[#111111] focus-visible:border-[#111111] disabled:cursor-not-allowed disabled:opacity-50"
              />
              <Lock className="w-4 h-4 text-[#858585] absolute left-2.5 top-2.5 pointer-events-none" />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                tabIndex={-1}
                className="absolute right-2.5 top-2.5 text-[#858585] hover:text-[#111111] focus:outline-none"
                aria-label={showPassword ? 'Hide password' : 'Show password'}
              >
                {showPassword ? (
                  <EyeOff className="w-4 h-4" />
                ) : (
                  <Eye className="w-4 h-4" />
                )}
              </button>
            </div>
            {mode === 'sign-up' && (
              <p className="text-[11px] text-[#858585] mt-1">
                Minimum 6 characters. Handled securely by Supabase Auth.
              </p>
            )}
          </div>

          <div className="pt-2">
            <Button
              type="submit"
              variant="primary"
              size="md"
              className="w-full justify-center"
              disabled={isLoading || !email.trim() || !password}
              icon={
                isLoading ? (
                  <Loader2 className="w-4 h-4 animate-spin text-white" />
                ) : (
                  <ArrowRight className="w-4 h-4 text-white" />
                )
              }
            >
              {isLoading
                ? mode === 'sign-in'
                  ? 'Verifying Credentials...'
                  : 'Registering Account...'
                : mode === 'sign-in'
                  ? 'Sign In to Console'
                  : 'Create Analyst Account'}
            </Button>
          </div>
        </form>

        {/* Toggle between Sign In and Sign Up */}
        <div className="mt-6 pt-5 border-t border-[#E5E5E2] text-center text-xs text-[#737373]">
          {mode === 'sign-in' ? (
            <p>
              Need an analyst account?{' '}
              <button
                type="button"
                onClick={() => {
                  setMode('sign-up')
                  setErrorMessage(null)
                  setSuccessMessage(null)
                }}
                className="font-semibold text-[#111111] hover:underline focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-[#111111] rounded px-1"
              >
                Create Account
              </button>
            </p>
          ) : (
            <p>
              Already have an account?{' '}
              <button
                type="button"
                onClick={() => {
                  setMode('sign-in')
                  setErrorMessage(null)
                  setSuccessMessage(null)
                }}
                className="font-semibold text-[#111111] hover:underline focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-[#111111] rounded px-1"
              >
                Sign In
              </button>
            </p>
          )}
        </div>
      </div>

      {/* Security Footer Notice */}
      <div className="mt-8 text-center text-xs font-mono text-[#858585] flex items-center gap-2">
        <ShieldCheck className="w-3.5 h-3.5 text-[#525252]" />
        <span>End-to-End Cryptographic JWT Session Protection</span>
      </div>
    </div>
  )
}
