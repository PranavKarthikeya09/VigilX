import { useState, useEffect } from 'react'
import {
  Shield,
  ShieldCheck,
  AlertTriangle,
  Flame,
  ArrowRight,
  Server,
  Database,
  CheckCircle2,
  Globe,
  Smartphone,
  Info,
} from 'lucide-react'
import { PageHeading } from '../ui/PageHeading'
import { MetricCard } from '../ui/MetricCard'
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '../ui/Card'
import { Badge } from '../ui/Badge'
import { Button } from '../ui/Button'
import { isSupabaseConfigured } from '../../services/supabase'

export interface OverviewViewProps {
  onNavigateToBrands: () => void
}

export function OverviewView({ onNavigateToBrands }: OverviewViewProps) {
  const [backendStatus, setBackendStatus] = useState<'checking' | 'connected' | 'disconnected'>('checking')
  const [backendLatency, setBackendLatency] = useState<number | null>(null)

  useEffect(() => {
    let isMounted = true
    const checkBackend = async () => {
      const start = Date.now()
      try {
        const response = await fetch('http://localhost:8000/health')
        if (isMounted) {
          if (response.ok) {
            setBackendLatency(Date.now() - start)
            setBackendStatus('connected')
          } else {
            setBackendStatus('disconnected')
          }
        }
      } catch {
        if (isMounted) {
          setBackendStatus('disconnected')
        }
      }
    }

    checkBackend()
    return () => {
      isMounted = false
    }
  }, [])

  return (
    <div className="space-y-8 animate-in fade-in duration-150">
      {/* 1. Page Heading */}
      <PageHeading
        title="Security Overview"
        eyebrow="Monitoring Console"
        description="A centralized view of your brand protection workspace. Configure protected brand identities to initiate continuous impersonation surveillance across social platforms and mobile app ecosystems."
        badge={
          <Badge variant="dark" dot>
            Workspace Active
          </Badge>
        }
        action={
          <Button
            variant="primary"
            size="md"
            icon={<ShieldCheck className="w-4 h-4 text-white" />}
            onClick={onNavigateToBrands}
          >
            Configure Brand
          </Button>
        }
      />

      {/* 2. Key Metrics Grid (Explicit Neutral Placeholders per Design Spec) */}
      <section aria-label="Key Security Metrics">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <MetricCard
            label="Protected Brands"
            value="—"
            description="Active brand profiles enrolled in surveillance"
            helperText="Requires brand profile onboarding"
            icon={<Shield className="w-4 h-4 text-[#111111]" />}
          />
          <MetricCard
            label="Official Assets"
            value="—"
            description="Exclusion whitelist (social handles & mobile apps)"
            helperText="Zero assets registered"
            icon={<ShieldCheck className="w-4 h-4 text-[#15803D]" />}
          />
          <MetricCard
            label="Threats Detected"
            value="—"
            description="Potential impersonations flagged for review"
            helperText="Surveillance awaiting target identity"
            icon={<AlertTriangle className="w-4 h-4 text-[#B45309]" />}
          />
          <MetricCard
            label="High-Risk Threats"
            value="—"
            description="Severe impersonation and lookalike alerts"
            helperText="No active threat feeds configured"
            icon={<Flame className="w-4 h-4 text-[#DC2626]" />}
          />
        </div>
      </section>

      {/* 3. Main Operational Sections Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column (2 Cols): Threat Overview & Scope Architecture */}
        <div className="lg:col-span-2 space-y-6">
          {/* Threat Monitoring Scope Placeholder Panel */}
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-3">
              <div>
                <CardTitle>Threat Intelligence Coverage</CardTitle>
                <CardDescription>
                  Multi-vector impersonation detection and perimeter scope.
                </CardDescription>
              </div>
              <Badge variant="neutral" className="text-[10px]">
                Surveillance Channels
              </Badge>
            </CardHeader>

            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {/* Social Media Vectors */}
                <div className="p-4 rounded-md bg-[#F0F0ED] border border-[#E5E5E2] space-y-2.5">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2 text-xs font-semibold text-[#111111]">
                      <Globe className="w-4 h-4 text-[#111111]" />
                      <span>Social Networks</span>
                    </div>
                    <span className="text-[10px] font-mono text-[#858585] uppercase">5 Channels</span>
                  </div>
                  <p className="text-xs text-[#525252] leading-relaxed">
                    Surveillance across X (Twitter), Instagram, Facebook, LinkedIn, and TikTok.
                  </p>
                  <div className="flex flex-wrap gap-1.5 pt-1">
                    {['X', 'Instagram', 'Facebook', 'LinkedIn', 'TikTok'].map((platform) => (
                      <span
                        key={platform}
                        className="text-[10px] font-mono px-2 py-0.5 rounded bg-white text-[#525252] border border-[#E5E5E2]"
                      >
                        {platform}
                      </span>
                    ))}
                  </div>
                </div>

                {/* Mobile App Ecosystem Vectors */}
                <div className="p-4 rounded-md bg-[#F0F0ED] border border-[#E5E5E2] space-y-2.5">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2 text-xs font-semibold text-[#111111]">
                      <Smartphone className="w-4 h-4 text-[#111111]" />
                      <span>App Ecosystems</span>
                    </div>
                    <span className="text-[10px] font-mono text-[#858585] uppercase">2 Stores</span>
                  </div>
                  <p className="text-xs text-[#525252] leading-relaxed">
                    Automated indexing against official store package IDs and developer names.
                  </p>
                  <div className="flex flex-wrap gap-1.5 pt-1">
                    {['Google Play', 'Apple App Store'].map((store) => (
                      <span
                        key={store}
                        className="text-[10px] font-mono px-2 py-0.5 rounded bg-white text-[#525252] border border-[#E5E5E2]"
                      >
                        {store}
                      </span>
                    ))}
                  </div>
                </div>
              </div>

              {/* Informational Guidance Notice */}
              <div className="p-3.5 rounded-md bg-[#F0F0ED] border border-[#E5E5E2] flex items-start gap-3 text-xs text-[#525252]">
                <Info className="w-4 h-4 text-[#111111] flex-shrink-0 mt-0.5" />
                <div className="leading-relaxed">
                  <span className="text-[#111111] font-medium">Pre-Detection Baseline: </span>
                  Impersonation detection triggers automatically once an official brand profile is created and its official social handles and application packages are cataloged.
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Threat Distribution Layout Placeholder */}
          <Card>
            <CardHeader>
              <CardTitle>Risk Severity Distribution</CardTitle>
              <CardDescription>
                Telemetry metrics will classify threats by algorithmically computed risk scores once active.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="p-8 rounded-md bg-[#F0F0ED] border border-[#E5E5E2] text-center space-y-3">
                <div className="w-10 h-10 rounded-full bg-white border border-[#E5E5E2] flex items-center justify-center mx-auto text-[#858585]">
                  <AlertTriangle className="w-5 h-5 text-[#B45309]" />
                </div>
                <div>
                  <h4 className="text-xs font-semibold text-[#111111]">No Risk Telemetry Generated</h4>
                  <p className="text-xs text-[#858585] max-w-sm mx-auto mt-1 leading-relaxed">
                    Threat distributions (Critical, High, Medium, Low) will chart here in real-time as the detection engine scores external entities.
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Right Column (1 Col): Recent Activity Empty State & Infrastructure */}
        <div className="space-y-6">
          {/* Recent Activity Section (Polished Empty State) */}
          <Card>
            <CardHeader>
              <CardTitle>Recent Activity</CardTitle>
              <CardDescription>Audit log of brand detections and asset updates.</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="py-10 px-4 text-center space-y-3">
                <div className="w-12 h-12 rounded-full bg-[#F0F0ED] border border-[#E5E5E2] flex items-center justify-center mx-auto text-[#111111]">
                  <ShieldCheck className="w-6 h-6 text-[#15803D]" />
                </div>
                <div>
                  <h4 className="text-xs font-semibold text-[#111111]">No Activity Logged Yet</h4>
                  <p className="text-xs text-[#525252] mt-1.5 leading-relaxed max-w-xs mx-auto">
                    Security events, engine scans, and lookalike warnings will be recorded here once you enroll your first brand profile.
                  </p>
                </div>
                <div className="pt-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={onNavigateToBrands}
                    className="gap-2"
                  >
                    <span>Go to Brands & Assets</span>
                    <ArrowRight className="w-3.5 h-3.5 text-[#111111]" />
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Infrastructure Health Status */}
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-xs uppercase font-mono tracking-wider text-[#858585]">
                Core Systems Diagnostics
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3 pt-2">
              {/* Backend Status */}
              <div className="p-3 rounded-md bg-[#F0F0ED] border border-[#E5E5E2] flex items-center justify-between">
                <div className="flex items-center gap-2.5">
                  <Server className="w-4 h-4 text-[#525252]" />
                  <div>
                    <p className="text-xs font-medium text-[#111111]">FastAPI Backend</p>
                    <p className="text-[10px] text-[#858585] font-mono">Port 8000 /health</p>
                  </div>
                </div>
                {backendStatus === 'connected' ? (
                  <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-mono bg-[#F0FDF4] text-[#15803D] border border-[#BBF7D0]">
                    <CheckCircle2 className="w-3 h-3 text-[#15803D]" /> Online {backendLatency !== null ? `(${backendLatency}ms)` : ''}
                  </span>
                ) : backendStatus === 'checking' ? (
                  <span className="text-[10px] font-mono text-[#B45309]">Probing...</span>
                ) : (
                  <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-mono bg-[#FEF2F2] text-[#DC2626] border border-[#FECACA]">
                    <AlertTriangle className="w-3 h-3 text-[#DC2626]" /> Offline
                  </span>
                )}
              </div>

              {/* Supabase Status */}
              <div className="p-3 rounded-md bg-[#F0F0ED] border border-[#E5E5E2] flex items-center justify-between">
                <div className="flex items-center gap-2.5">
                  <Database className="w-4 h-4 text-[#525252]" />
                  <div>
                    <p className="text-xs font-medium text-[#111111]">Supabase Auth</p>
                    <p className="text-[10px] text-[#858585] font-mono">JWT Bearer Pipeline</p>
                  </div>
                </div>
                {isSupabaseConfigured ? (
                  <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-mono bg-[#F0FDF4] text-[#15803D] border border-[#BBF7D0]">
                    <CheckCircle2 className="w-3 h-3 text-[#15803D]" /> Configured
                  </span>
                ) : (
                  <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-mono bg-[#FFFBEB] text-[#B45309] border border-[#FDE68A]">
                    <AlertTriangle className="w-3 h-3 text-[#B45309]" /> Pending .env
                  </span>
                )}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
