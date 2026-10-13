import { Shield, Bell, Key, Lock } from 'lucide-react'
import { PageHeading } from '../ui/PageHeading'
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '../ui/Card'
import { Badge } from '../ui/Badge'

export function SettingsView() {
  return (
    <div className="space-y-8 animate-in fade-in duration-150">
      <PageHeading
        title="Settings"
        eyebrow="Configuration"
        description="Manage workspace preferences, detection thresholds, API integrations, and analyst access controls."
        badge={
          <Badge variant="neutral">
            Workspace Configuration
          </Badge>
        }
      />

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Workspace Security Policies */}
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <Shield className="w-4 h-4 text-[#111111]" />
              <CardTitle>Detection Policy & Sensitivity</CardTitle>
            </div>
            <CardDescription>
              Configure engine sensitivity weights and auto-exclusion tolerances.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="p-3.5 rounded-md bg-[#F0F0ED] border border-[#E5E5E2] flex items-center justify-between text-xs">
              <span className="text-[#525252]">Fuzzy Matching Threshold</span>
              <span className="font-mono text-[#111111]">0.80 (Standard)</span>
            </div>
            <div className="p-3.5 rounded-md bg-[#F0F0ED] border border-[#E5E5E2] flex items-center justify-between text-xs">
              <span className="text-[#525252]">Auto-Exclusion of Official Assets</span>
              <span className="font-mono text-[#111111] font-medium">Enabled (100% Boundary)</span>
            </div>
            <p className="text-[11px] text-[#858585] pt-1">
              Threshold tuning policies will be accessible once brand profiles are active.
            </p>
          </CardContent>
        </Card>

        {/* Notification & Telemetry Integrations */}
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <Bell className="w-4 h-4 text-[#111111]" />
              <CardTitle>Alert Channels & Webhooks</CardTitle>
            </div>
            <CardDescription>
              Webhook dispatch and incident response notification channels.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="p-3.5 rounded-md bg-[#F0F0ED] border border-[#E5E5E2] flex items-center justify-between text-xs">
              <span className="text-[#525252]">Critical Risk Dispatches</span>
              <span className="font-mono text-[#858585]">Unconfigured</span>
            </div>
            <div className="p-3.5 rounded-md bg-[#F0F0ED] border border-[#E5E5E2] flex items-center justify-between text-xs">
              <span className="text-[#525252]">Digest Summary Frequency</span>
              <span className="font-mono text-[#858585]">Daily</span>
            </div>
            <p className="text-[11px] text-[#858585] pt-1">
              Integration endpoints for Slack, PagerDuty, and SIEM will be configurable in future updates.
            </p>
          </CardContent>
        </Card>

        {/* Authentication & Session Info */}
        <Card className="md:col-span-2">
          <CardHeader>
            <div className="flex items-center gap-2">
              <Key className="w-4 h-4 text-[#111111]" />
              <CardTitle>Authentication & Service Credentials</CardTitle>
            </div>
            <CardDescription>
              Stateless Supabase ES256 JWT identity and FastAPI session parameters.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="p-4 rounded-md bg-[#F0F0ED] border border-[#E5E5E2] flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs">
              <div>
                <p className="font-medium text-[#111111]">Supabase Auth Session Guard</p>
                <p className="text-[#525252] mt-0.5">
                  JWT Bearer tokens are attached via Axios interceptor to all requests targeting /api/v1.
                </p>
              </div>
              <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded bg-white text-[#111111] font-mono text-[11px] border border-[#E5E5E2] flex-shrink-0">
                <Lock className="w-3 h-3 text-[#111111]" />
                JWT ES256 Verified
              </span>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
