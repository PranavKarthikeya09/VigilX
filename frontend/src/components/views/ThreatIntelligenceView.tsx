import { ScanSearch, ShieldAlert, Filter, Lock } from 'lucide-react'
import { PageHeading } from '../ui/PageHeading'
import { Card, CardContent } from '../ui/Card'
import { Badge } from '../ui/Badge'
import { Button } from '../ui/Button'

export function ThreatIntelligenceView() {
  return (
    <div className="space-y-8 animate-in fade-in duration-150">
      <PageHeading
        title="Threat Intelligence"
        eyebrow="Impersonation Stream"
        description="Continuous external surveillance feed identifying unauthorized lookalike accounts, typo-squatted usernames, and spoofed mobile apps targetting protected brands."
        badge={
          <Badge variant="neutral">
            Surveillance Stream
          </Badge>
        }
        action={
          <Button
            variant="secondary"
            size="md"
            icon={<Filter className="w-4 h-4 text-[#525252]" />}
            disabled
          >
            Filter Findings
          </Button>
        }
      />

      {/* Analytical Engine Methodology Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="p-5 space-y-2 border-[#E5E5E2]">
          <div className="flex items-center gap-2 text-xs font-semibold text-[#111111]">
            <span className="w-2 h-2 rounded-full bg-[#111111]" />
            <span>Name Similarity Scoring</span>
          </div>
          <p className="text-xs text-[#525252] leading-relaxed">
            Levenshtein edit distance, Jaro-Winkler metric, and token sort ratio identify intentional lookalikes and typo-squatting.
          </p>
        </Card>

        <Card className="p-5 space-y-2 border-[#E5E5E2]">
          <div className="flex items-center gap-2 text-xs font-semibold text-[#111111]">
            <span className="w-2 h-2 rounded-full bg-[#111111]" />
            <span>Visual Brand Inspection</span>
          </div>
          <p className="text-xs text-[#525252] leading-relaxed">
            Perceptual hashing (pHash) against canonical brand logos to flag cloned or unauthorized profile picture usage.
          </p>
        </Card>

        <Card className="p-5 space-y-2 border-[#E5E5E2]">
          <div className="flex items-center gap-2 text-xs font-semibold text-[#111111]">
            <span className="w-2 h-2 rounded-full bg-[#111111]" />
            <span>Official Exclusion Filter</span>
          </div>
          <p className="text-xs text-[#525252] leading-relaxed">
            Whitelisted official social accounts and app packages are automatically excluded, eliminating false positive alerts.
          </p>
        </Card>
      </div>

      {/* Main Empty State Placeholder */}
      <Card className="border-dashed border-[#DCDCD8] bg-white">
        <CardContent className="py-16 text-center space-y-4">
          <div className="w-14 h-14 rounded-full bg-[#F0F0ED] border border-[#E5E5E2] flex items-center justify-center mx-auto text-[#111111]">
            <ScanSearch className="w-7 h-7 text-[#111111]" />
          </div>
          <div className="space-y-1.5 max-w-md mx-auto">
            <h3 className="text-base font-semibold text-[#111111]">No Detection Findings Yet</h3>
            <p className="text-xs text-[#525252] leading-relaxed">
              Suspicious social profiles, unauthorized store listings, risk scores, and evidence cards will populate here once the detection engine executes scheduled crawls.
            </p>
          </div>
          <div className="pt-2">
            <span className="inline-flex items-center gap-2 px-3 py-1.5 rounded text-xs font-mono text-[#525252] bg-[#F0F0ED] border border-[#E5E5E2]">
              <Lock className="w-3.5 h-3.5 text-[#111111]" />
              Phase 3: Threat Engine Integration & Evidence Drawer
            </span>
          </div>
        </CardContent>
      </Card>

      {/* Guidance Note */}
      <div className="p-4 rounded-md bg-[#F0F0ED] border border-[#E5E5E2] flex items-center gap-3 text-xs text-[#525252]">
        <ShieldAlert className="w-4 h-4 text-[#111111] flex-shrink-0" />
        <span>
          <strong className="text-[#111111]">Detection Integrity:</strong> vigilX will never display artificial threat alerts or simulated risks. Only findings verified by the detection engine algorithms will appear in this workspace.
        </span>
      </div>
    </div>
  )
}
