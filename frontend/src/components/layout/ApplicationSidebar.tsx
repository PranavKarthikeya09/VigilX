import React from 'react'
import {
  LayoutDashboard,
  ShieldCheck,
  ScanSearch,
  Settings,
  Shield,
  X,
  Radio,
} from 'lucide-react'
import { cn } from '../../lib/utils'

export type NavigationTab = 'overview' | 'brands-assets' | 'threat-intel' | 'settings'

interface NavigationItem {
  id: NavigationTab
  label: string
  icon: React.ComponentType<{ className?: string }>
  badge?: string
}

const NAVIGATION_ITEMS: NavigationItem[] = [
  {
    id: 'overview',
    label: 'Overview',
    icon: LayoutDashboard,
  },
  {
    id: 'brands-assets',
    label: 'Brands & Assets',
    icon: ShieldCheck,
  },
  {
    id: 'threat-intel',
    label: 'Threat Intelligence',
    icon: ScanSearch,
  },
  {
    id: 'settings',
    label: 'Settings',
    icon: Settings,
  },
]

export interface ApplicationSidebarProps {
  activeTab: NavigationTab
  onSelectTab: (tab: NavigationTab) => void
  isMobileOpen?: boolean
  onCloseMobile?: () => void
}

export function ApplicationSidebar({
  activeTab,
  onSelectTab,
  isMobileOpen = false,
  onCloseMobile,
}: ApplicationSidebarProps) {
  const handleNavClick = (tab: NavigationTab) => {
    onSelectTab(tab)
    if (onCloseMobile) {
      onCloseMobile()
    }
  }

  const sidebarContent = (
    <div className="flex h-full flex-col justify-between bg-[#111111] text-white border-r border-[#222222]">
      {/* Top Branding Section */}
      <div>
        <div className="flex items-center justify-between px-5 h-16 border-b border-[#222222]">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded bg-white text-[#111111] flex items-center justify-center font-bold">
              <Shield className="w-4 h-4 text-[#111111]" />
            </div>
            <div>
              <span className="text-base font-bold tracking-tight text-white block">
                vigilX
              </span>
              <span className="text-[10px] text-[#858585] block -mt-1 font-mono uppercase tracking-widest">
                Intelligence
              </span>
            </div>
          </div>

          {/* Mobile close button */}
          {onCloseMobile && (
            <button
              onClick={onCloseMobile}
              className="md:hidden p-1.5 rounded text-[#858585] hover:text-white hover:bg-[#222222] focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-white"
              aria-label="Close navigation menu"
            >
              <X className="w-5 h-5" />
            </button>
          )}
        </div>

        {/* Section Label */}
        <div className="px-5 pt-6 pb-2">
          <p className="text-[10px] font-mono uppercase tracking-widest text-[#737373]">
            Workspace Navigation
          </p>
        </div>

        {/* Navigation Items */}
        <nav className="px-3 space-y-1" aria-label="Main Navigation">
          {NAVIGATION_ITEMS.map((item) => {
            const Icon = item.icon
            const isActive = activeTab === item.id

            return (
              <button
                key={item.id}
                onClick={() => handleNavClick(item.id)}
                className={cn(
                  'w-full flex items-center justify-between px-3 py-2.5 rounded text-xs font-medium transition-colors text-left',
                  'focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-white',
                  isActive
                    ? 'bg-white text-[#111111] font-semibold shadow-sm'
                    : 'text-[#A3A3A3] hover:text-white hover:bg-[#1E1E1E]',
                )}
                aria-current={isActive ? 'page' : undefined}
              >
                <div className="flex items-center gap-2.5">
                  <Icon
                    className={cn(
                      'w-4 h-4 flex-shrink-0 transition-colors',
                      isActive ? 'text-[#111111]' : 'text-[#737373]',
                    )}
                  />
                  <span>{item.label}</span>
                </div>
                {item.badge && (
                  <span
                    className={cn(
                      'text-[10px] font-mono px-1.5 py-0.2 rounded',
                      isActive ? 'bg-[#E5E5E2] text-[#111111]' : 'bg-[#222222] text-[#A3A3A3]',
                    )}
                  >
                    {item.badge}
                  </span>
                )}
              </button>
            )
          })}
        </nav>
      </div>

      {/* Bottom Account & System Status Section */}
      <div className="p-4 border-t border-[#222222] space-y-3">
        {/* Protection Engine Status */}
        <div className="px-3 py-2 rounded bg-[#1A1A1A] border border-[#262626] flex items-center justify-between text-xs">
          <div className="flex items-center gap-2">
            <Radio className="w-3.5 h-3.5 text-white" />
            <span className="text-[11px] font-mono text-[#A3A3A3]">Engine</span>
          </div>
          <span className="text-[10px] font-mono text-white uppercase font-medium">
            Active
          </span>
        </div>

        {/* Workspace Identity */}
        <div className="px-3 py-2 rounded bg-[#181818] border border-[#242424] flex items-center justify-between">
          <div className="flex items-center gap-2.5 overflow-hidden">
            <div className="w-6 h-6 rounded bg-[#2A2A2A] text-white flex items-center justify-center text-[10px] font-mono font-bold">
              VX
            </div>
            <div className="overflow-hidden">
              <p className="text-xs font-medium text-white truncate">Security Workspace</p>
              <p className="text-[10px] text-[#737373] font-mono truncate">Console 01</p>
            </div>
          </div>
          <span className="text-[9px] font-mono text-[#858585] px-1.5 py-0.5 rounded border border-[#2E2E2E]">
            v1.0
          </span>
        </div>
      </div>
    </div>
  )

  return (
    <>
      {/* Desktop Sidebar (Persistent left) */}
      <aside className="hidden md:block w-64 flex-shrink-0 h-screen sticky top-0 z-30">
        {sidebarContent}
      </aside>

      {/* Mobile Drawer Backdrop & Panel */}
      {isMobileOpen && (
        <div className="fixed inset-0 z-50 md:hidden flex" role="dialog" aria-modal="true">
          <div
            className="fixed inset-0 bg-black/60 transition-opacity"
            onClick={onCloseMobile}
            aria-hidden="true"
          />
          <div className="relative flex-1 flex flex-col max-w-xs w-full h-full shadow-xl z-10">
            {sidebarContent}
          </div>
        </div>
      )}
    </>
  )
}
