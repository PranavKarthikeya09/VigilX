import { Menu, ShieldAlert, Activity, LogOut } from 'lucide-react'
import { Badge } from '../ui/Badge'
import { useAuth } from '../../context/useAuth'
import type { NavigationTab } from './ApplicationSidebar'

export interface ApplicationHeaderProps {
  activeTab: NavigationTab
  onOpenMobileNav: () => void
}

const TAB_TITLES: Record<NavigationTab, { title: string; subtitle: string }> = {
  overview: {
    title: 'Security Overview',
    subtitle: 'Brand Risk Monitoring Workspace',
  },
  'brands-assets': {
    title: 'Brands & Assets',
    subtitle: 'Protected Identity Registry',
  },
  'threat-intel': {
    title: 'Threat Intelligence',
    subtitle: 'Active Impersonation Detection Stream',
  },
  settings: {
    title: 'Settings',
    subtitle: 'Workspace Configuration & Policies',
  },
}

export function ApplicationHeader({ activeTab, onOpenMobileNav }: ApplicationHeaderProps) {
  const current = TAB_TITLES[activeTab]
  const { user, signOut } = useAuth()

  // Generate 2-character initials from email
  const initials = user?.email
    ? user.email.slice(0, 2).toUpperCase()
    : 'AN'

  return (
    <header className="sticky top-0 z-20 h-16 border-b border-[#E5E5E2] bg-white/95 backdrop-blur-sm px-4 sm:px-6 flex items-center justify-between">
      {/* Left: Mobile trigger and Page breadcrumb */}
      <div className="flex items-center gap-3">
        <button
          onClick={onOpenMobileNav}
          className="md:hidden p-2 -ml-2 rounded text-[#525252] hover:text-[#111111] hover:bg-[#F0F0ED] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#111111]"
          aria-label="Open navigation menu"
        >
          <Menu className="w-5 h-5" />
        </button>

        <div className="flex items-center gap-2">
          <span className="hidden sm:inline text-xs font-mono text-[#858585] uppercase tracking-wider">
            vigilX
          </span>
          <span className="hidden sm:inline text-xs text-[#858585]">/</span>
          <h2 className="text-sm font-semibold text-[#111111] tracking-tight">{current.title}</h2>
        </div>
      </div>

      {/* Right: Status indicators and Account session */}
      <div className="flex items-center gap-3">
        {/* Protection workspace indicator */}
        <div className="hidden sm:flex items-center gap-2 px-2.5 py-1 rounded bg-[#F0F0ED] border border-[#E5E5E2]">
          <Activity className="w-3.5 h-3.5 text-[#111111]" />
          <span className="text-[11px] font-mono text-[#525252]">Protection Workspace</span>
          <Badge variant="dark" className="text-[10px] py-0 px-1.5 ml-1">
            Active
          </Badge>
        </div>

        {/* Monitoring indicator */}
        <div className="flex items-center gap-1.5 text-xs text-[#525252]">
          <span
            className="p-1.5 rounded bg-[#F0F0ED] border border-[#E5E5E2] text-[#525252] hover:text-[#111111] transition-colors"
            title="Monitoring Status"
          >
            <ShieldAlert className="w-4 h-4 text-[#858585]" />
          </span>
        </div>

        {/* Authenticated Analyst Session Info & Sign Out */}
        <div className="flex items-center gap-3 pl-3 border-l border-[#E5E5E2]">
          <div className="flex items-center gap-2.5">
            <div className="w-7 h-7 rounded bg-[#111111] text-white flex items-center justify-center text-xs font-mono font-medium flex-shrink-0">
              {initials}
            </div>
            <div className="hidden lg:block text-left max-w-[160px]">
              <p className="text-xs font-medium text-[#111111] leading-none truncate">
                {user?.email || 'Analyst Session'}
              </p>
              <p className="text-[10px] text-[#858585] font-mono leading-none mt-1">Authenticated</p>
            </div>
          </div>

          <button
            onClick={() => void signOut()}
            title="Sign out of VigilX"
            className="p-1.5 rounded text-[#737373] hover:text-[#B91C1C] hover:bg-[#FEF2F2] border border-transparent hover:border-[#FECACA] transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-[#111111]"
            aria-label="Sign out"
          >
            <LogOut className="w-4 h-4" />
          </button>
        </div>
      </div>
    </header>
  )
}
