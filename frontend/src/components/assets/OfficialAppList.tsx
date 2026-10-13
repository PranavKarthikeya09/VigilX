import { Smartphone, Trash2, ExternalLink, Calendar, Plus } from 'lucide-react'
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '../ui/Card'
import { Badge } from '../ui/Badge'
import { Button } from '../ui/Button'
import type { OfficialApp, AppStore } from '../../types/brand'

export interface OfficialAppListProps {
  apps: OfficialApp[]
  isLoading?: boolean
  onAddApp: () => void
  onDeleteApp: (app: OfficialApp) => void
}

const STORE_LABELS: Record<AppStore, string> = {
  google_play: 'Google Play',
  app_store: 'Apple App Store',
}

export function OfficialAppList({
  apps,
  isLoading = false,
  onAddApp,
  onDeleteApp,
}: OfficialAppListProps) {
  return (
    <Card className="bg-white border-[#E5E5E2]">
      <CardHeader className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 gap-3">
        <div>
          <div className="flex items-center gap-2">
            <CardTitle className="text-base text-[#111111]">
              Official Mobile Applications
            </CardTitle>
            <Badge variant="neutral" className="text-[10px]">
              {apps.length} Whitelisted
            </Badge>
          </div>
          <CardDescription>
            Verified application packages on Google Play and Apple App Store excluded from impersonation detection.
          </CardDescription>
        </div>
        <Button
          variant="primary"
          size="sm"
          icon={<Plus className="w-3.5 h-3.5 text-white" />}
          onClick={onAddApp}
        >
          Add Mobile App
        </Button>
      </CardHeader>

      <CardContent>
        {/* Loading skeleton state */}
        {isLoading && apps.length === 0 ? (
          <div className="space-y-2 py-4">
            {[1, 2].map((i) => (
              <div
                key={i}
                className="h-16 rounded-md bg-[#F0F0ED] animate-pulse border border-[#E5E5E2]"
              />
            ))}
          </div>
        ) : apps.length === 0 ? (
          /* Empty state */
          <div className="py-12 px-4 text-center space-y-3 rounded-md bg-[#F7F7F5] border border-dashed border-[#DCDCD8]">
            <div className="w-12 h-12 rounded-full bg-white border border-[#E5E5E2] flex items-center justify-center mx-auto text-[#111111]">
              <Smartphone className="w-6 h-6 text-[#111111]" />
            </div>
            <div className="max-w-md mx-auto space-y-1">
              <h4 className="text-sm font-semibold text-[#111111]">
                No official mobile apps registered
              </h4>
              <p className="text-xs text-[#525252] leading-relaxed">
                Register your brand&apos;s legitimate mobile applications to establish store whitelist boundaries and prevent false impersonation alerts.
              </p>
            </div>
            <div className="pt-2">
              <Button
                variant="outline"
                size="sm"
                icon={<Plus className="w-3.5 h-3.5 text-[#111111]" />}
                onClick={onAddApp}
              >
                Add Mobile App
              </Button>
            </div>
          </div>
        ) : (
          /* Applications List Table */
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-[#E5E5E2] text-[11px] font-mono text-[#858585] uppercase tracking-wider">
                  <th className="py-2.5 px-3">Store</th>
                  <th className="py-2.5 px-3">Application Title</th>
                  <th className="py-2.5 px-3">Developer / Publisher</th>
                  <th className="py-2.5 px-3">Package ID</th>
                  <th className="py-2.5 px-3">Store Link</th>
                  <th className="py-2.5 px-3">Registered</th>
                  <th className="py-2.5 px-3 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#E5E5E2]">
                {apps.map((app) => {
                  const storeName = STORE_LABELS[app.store] || app.store
                  const createdDate = new Date(app.created_at).toLocaleDateString(
                    undefined,
                    { month: 'short', day: 'numeric', year: 'numeric' },
                  )

                  return (
                    <tr
                      key={app.id}
                      className="hover:bg-[#F7F7F5] transition-colors group"
                    >
                      {/* Store */}
                      <td className="py-3 px-3 font-medium text-[#111111] whitespace-nowrap">
                        <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded bg-[#F0F0ED] border border-[#E5E5E2] font-mono text-[11px]">
                          {storeName}
                        </span>
                      </td>

                      {/* Application Title */}
                      <td className="py-3 px-3 font-semibold text-[#111111] whitespace-nowrap">
                        {app.name}
                      </td>

                      {/* Developer / Publisher */}
                      <td className="py-3 px-3 text-[#525252] whitespace-nowrap">
                        {app.developer_name}
                      </td>

                      {/* Package ID */}
                      <td className="py-3 px-3 font-mono text-[11px] text-[#525252] whitespace-nowrap">
                        {app.package_id ? (
                          <span className="px-1.5 py-0.5 rounded bg-[#F7F7F5] border border-[#E5E5E2]">
                            {app.package_id}
                          </span>
                        ) : (
                          <span className="text-[#858585]">—</span>
                        )}
                      </td>

                      {/* Store Link */}
                      <td className="py-3 px-3 whitespace-nowrap">
                        {app.store_url ? (
                          <a
                            href={app.store_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="inline-flex items-center gap-1 text-xs text-[#525252] hover:text-[#111111] hover:underline"
                          >
                            <span>Store Listing</span>
                            <ExternalLink className="w-3 h-3 opacity-70" />
                          </a>
                        ) : (
                          <span className="text-[#858585] text-[11px]">—</span>
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
                          onClick={() => onDeleteApp(app)}
                          className="p-1.5 rounded text-[#858585] hover:text-[#B91C1C] hover:bg-[#FEF2F2] transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-[#DC2626]"
                          title={`Remove ${app.name} from whitelist`}
                          aria-label={`Remove ${app.name}`}
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
