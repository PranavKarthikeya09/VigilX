import { useState, useEffect } from 'react'
import { Shield, CheckCircle2, AlertTriangle, Server, Database } from 'lucide-react'
import { isSupabaseConfigured } from './services/supabase'

export function App() {
  const [backendStatus, setBackendStatus] = useState<'checking' | 'connected' | 'disconnected'>('checking')
  const [backendLatency, setBackendLatency] = useState<number | null>(null)

  useEffect(() => {
    const checkBackend = async () => {
      const start = Date.now()
      try {
        const response = await fetch('http://localhost:8000/health')
        if (response.ok) {
          setBackendLatency(Date.now() - start)
          setBackendStatus('connected')
        } else {
          setBackendStatus('disconnected')
        }
      } catch {
        setBackendStatus('disconnected')
      }
    }

    checkBackend()
  }, [])

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col">
      {/* Header */}
      <header className="border-b border-slate-800 bg-slate-900/60 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-blue-600/20 border border-blue-500/30 flex items-center justify-center text-blue-400">
              <Shield className="w-6 h-6" />
            </div>
            <div>
              <span className="text-xl font-bold tracking-tight bg-gradient-to-r from-blue-400 to-indigo-400 bg-clip-text text-transparent">
                vigilX
              </span>
              <span className="text-xs text-slate-400 block -mt-1 font-mono">
                Digital Risk Protection Platform
              </span>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-xs px-2.5 py-1 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 font-mono">
              Milestone 1 Core
            </span>
          </div>
        </div>
      </header>

      {/* Main Container */}
      <main className="flex-1 max-w-5xl w-full mx-auto px-4 py-12">
        <div className="text-center mb-10">
          <h1 className="text-4xl font-extrabold tracking-tight text-white mb-3">
            System Foundation & Health Status
          </h1>
          <p className="text-slate-400 max-w-2xl mx-auto text-sm leading-relaxed">
            vigilX monitors brand impersonation across social networks and app stores.
            Below is the operational status of the core presentation and application services.
          </p>
        </div>

        {/* Status Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-10">
          {/* Backend Status Card */}
          <div className="rounded-2xl border border-slate-800 bg-slate-900/40 p-6 flex flex-col justify-between">
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center gap-3">
                <div className="p-2.5 rounded-lg bg-indigo-500/10 border border-indigo-500/20 text-indigo-400">
                  <Server className="w-5 h-5" />
                </div>
                <div>
                  <h2 className="text-base font-semibold text-white">FastAPI Application</h2>
                  <p className="text-xs text-slate-400">Python 3.12 • SQLAlchemy 2.0 • Pydantic v2</p>
                </div>
              </div>
              {backendStatus === 'connected' ? (
                <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                  <CheckCircle2 className="w-3.5 h-3.5" /> Online {backendLatency !== null ? `(${backendLatency}ms)` : ''}
                </span>
              ) : backendStatus === 'checking' ? (
                <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-amber-500/10 text-amber-400 border border-amber-500/20">
                  Probing...
                </span>
              ) : (
                <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-rose-500/10 text-rose-400 border border-rose-500/20">
                  <AlertTriangle className="w-3.5 h-3.5" /> Offline
                </span>
              )}
            </div>
            <p className="text-xs text-slate-400 border-t border-slate-800/80 pt-3">
              Endpoints exposed: <code className="text-slate-300 font-mono">/health</code>, <code className="text-slate-300 font-mono">/ready</code>, <code className="text-slate-300 font-mono">/api/v1/auth/me</code>
            </p>
          </div>

          {/* Supabase Status Card */}
          <div className="rounded-2xl border border-slate-800 bg-slate-900/40 p-6 flex flex-col justify-between">
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center gap-3">
                <div className="p-2.5 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-400">
                  <Database className="w-5 h-5" />
                </div>
                <div>
                  <h2 className="text-base font-semibold text-white">Supabase Infrastructure</h2>
                  <p className="text-xs text-slate-400">PostgreSQL • Auth (JWT) • Storage</p>
                </div>
              </div>
              {isSupabaseConfigured ? (
                <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                  <CheckCircle2 className="w-3.5 h-3.5" /> Configured
                </span>
              ) : (
                <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-amber-500/10 text-amber-400 border border-amber-500/20">
                  <AlertTriangle className="w-3.5 h-3.5" /> Pending .env
                </span>
              )}
            </div>
            <p className="text-xs text-slate-400 border-t border-slate-800/80 pt-3">
              Configure credentials in <code className="text-slate-300 font-mono">frontend/.env.local</code> to activate live Supabase Auth.
            </p>
          </div>
        </div>

        {/* Architectural Boundaries Summary */}
        <div className="rounded-2xl border border-slate-800 bg-slate-900/20 p-6">
          <h2 className="text-sm font-semibold text-slate-200 mb-3 uppercase tracking-wider text-xs">
            Architectural Guarantees
          </h2>
          <ul className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs text-slate-400">
            <li className="flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-blue-400 flex-shrink-0" />
              <span>Strict secret isolation (no service keys in frontend)</span>
            </li>
            <li className="flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-blue-400 flex-shrink-0" />
              <span>Stateless Supabase JWT verification on backend</span>
            </li>
            <li className="flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-blue-400 flex-shrink-0" />
              <span>Alembic ownership of PostgreSQL schema migrations</span>
            </li>
            <li className="flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-blue-400 flex-shrink-0" />
              <span>100% known official asset exclusion boundary</span>
            </li>
          </ul>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800/80 py-4 text-center text-xs text-slate-500 font-mono">
        vigilX Platform • Milestone 1 Foundation Verified
      </footer>
    </div>
  )
}

export default App
