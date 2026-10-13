import { Share2, Trash2, ExternalLink, Check, Calendar, Plus } from 'lucide-react'
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '../ui/Card'
import { Badge } from '../ui/Badge'
import { Button } from '../ui/Button'
import type { OfficialSocialAccount } from '../../types/brand'

export interface OfficialSocialListProps {
  accounts: OfficialSocialAccount[]
  isLoading?: boolean
  onAddAccount: () => void
  onDeleteAccount: (account: OfficialSocialAccount) => void
}

const PLATFORM_LABELS: Record<string, string> = {
  x: 'X (Twitter)',
  instagram: 'Instagram',
  facebook: 'Facebook',
  linkedin: 'LinkedIn',
  tiktok: 'TikTok',
}

export function OfficialSocialList({
  accounts,
  isLoading = false,
  onAddAccount,
  onDeleteAccount,
}: OfficialSocialListProps) {
  return (
    <Card className="bg-white border-[#E5E5E2]">
      <CardHeader className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 gap-3">
        <div>
          <div className="flex items-center gap-2">
            <CardTitle className="text-base text-[#111111]">
              Official Social Accounts
            </CardTitle>
            <Badge variant="neutral" className="text-[10px]">
              {accounts.length} Whitelisted
            </Badge>
          </div>
          <CardDescription>
            Legitimate social profiles excluded from brand impersonation algorithms.
          </CardDescription>
        </div>
        <Button
          variant="primary"
          size="sm"
          icon={<Plus className="w-3.5 h-3.5 text-white" />}
          onClick={onAddAccount}
        >
          Add Social Account
        </Button>
      </CardHeader>

      <CardContent>
        {/* Loading state */}
        {isLoading && accounts.length === 0 ? (
          <div className="space-y-2 py-4">
            {[1, 2].map((i) => (
              <div
                key={i}
                className="h-16 rounded-md bg-[#F0F0ED] animate-pulse border border-[#E5E5E2]"
              />
            ))}
          </div>
        ) : accounts.length === 0 ? (
          /* Empty state */
          <div className="py-12 px-4 text-center space-y-3 rounded-md bg-[#F7F7F5] border border-dashed border-[#DCDCD8]">
            <div className="w-12 h-12 rounded-full bg-white border border-[#E5E5E2] flex items-center justify-center mx-auto text-[#111111]">
              <Share2 className="w-6 h-6 text-[#111111]" />
            </div>
            <div className="max-w-md mx-auto space-y-1">
              <h4 className="text-sm font-semibold text-[#111111]">
                No official social accounts registered
              </h4>
              <p className="text-xs text-[#525252] leading-relaxed">
                Register your brand&apos;s legitimate social profiles so they can be distinguished from potential impersonators in future monitoring.
              </p>
            </div>
            <div className="pt-2">
              <Button
                variant="outline"
                size="sm"
                icon={<Plus className="w-3.5 h-3.5 text-[#111111]" />}
                onClick={onAddAccount}
              >
                Add Social Account
              </Button>
            </div>
          </div>
        ) : (
          /* Accounts List Table */
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-[#E5E5E2] text-[11px] font-mono text-[#858585] uppercase tracking-wider">
                  <th className="py-2.5 px-3">Platform</th>
                  <th className="py-2.5 px-3">Display Handle</th>
                  <th className="py-2.5 px-3">Indexed Handle</th>
                  <th className="py-2.5 px-3">Profile Link</th>
                  <th className="py-2.5 px-3">Verified Status</th>
                  <th className="py-2.5 px-3">Registered</th>
                  <th className="py-2.5 px-3 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#E5E5E2]">
                {accounts.map((account) => {
                  const platformName =
                    PLATFORM_LABELS[account.platform.toLowerCase()] || account.platform
                  const createdDate = new Date(account.created_at).toLocaleDateString(
                    undefined,
                    { month: 'short', day: 'numeric', year: 'numeric' },
                  )

                  return (
                    <tr
                      key={account.id}
                      className="hover:bg-[#F7F7F5] transition-colors group"
                    >
                      {/* Platform */}
                      <td className="py-3 px-3 font-medium text-[#111111] whitespace-nowrap">
                        <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded bg-[#F0F0ED] border border-[#E5E5E2] font-mono text-[11px]">
                          {platformName}
                        </span>
                      </td>

                      {/* Display Handle */}
                      <td className="py-3 px-3 font-semibold text-[#111111] whitespace-nowrap">
                        {account.raw_handle}
                      </td>

                      {/* Normalized Handle */}
                      <td className="py-3 px-3 font-mono text-[#525252] whitespace-nowrap">
                        @{account.handle}
                      </td>

                      {/* Profile Link */}
                      <td className="py-3 px-3 whitespace-nowrap">
                        {account.url ? (
                          <a
                            href={account.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="inline-flex items-center gap-1 text-xs text-[#525252] hover:text-[#111111] hover:underline"
                          >
                            <span>Profile</span>
                            <ExternalLink className="w-3 h-3 opacity-70" />
                          </a>
                        ) : (
                          <span className="text-[#858585] text-[11px]">—</span>
                        )}
                      </td>

                      {/* Verified Badge */}
                      <td className="py-3 px-3 whitespace-nowrap">
                        {account.is_verified ? (
                          <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[10px] font-mono bg-[#EFF6FF] text-[#2563EB] border border-[#BFDBFE]">
                            <Check className="w-3 h-3" />
                            Verified
                          </span>
                        ) : (
                          <span className="text-[11px] font-mono text-[#858585]">
                            Standard
                          </span>
                        )}
                      </td>

                      {/* Registered Date */}
                      <td className="py-3 px-3 font-mono text-[11px] text-[#858585] whitespace-nowrap">
                        <span className="inline-flex items-center gap-1">
                          <Calendar className="w-3 h-3" />
                          {createdDate}
                        </span>
                      </td>

                      {/* Action: Delete */}
                      <td className="py-3 px-3 text-right whitespace-nowrap">
                        <button
                          onClick={() => onDeleteAccount(account)}
                          className="p-1.5 rounded text-[#858585] hover:text-[#B91C1C] hover:bg-[#FEF2F2] transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-[#DC2626]"
                          title={`Remove ${account.raw_handle} from whitelist`}
                          aria-label={`Remove ${account.raw_handle}`}
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
