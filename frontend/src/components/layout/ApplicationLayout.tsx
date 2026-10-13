import React, { useState } from 'react'
import { ApplicationSidebar, type NavigationTab } from './ApplicationSidebar'
import { ApplicationHeader } from './ApplicationHeader'

export interface ApplicationLayoutProps {
  activeTab: NavigationTab
  onSelectTab: (tab: NavigationTab) => void
  children: React.ReactNode
}

export function ApplicationLayout({
  activeTab,
  onSelectTab,
  children,
}: ApplicationLayoutProps) {
  const [isMobileOpen, setIsMobileOpen] = useState(false)

  return (
    <div className="min-h-screen bg-[#F7F7F5] text-[#111111] flex">
      {/* Sidebar Navigation */}
      <ApplicationSidebar
        activeTab={activeTab}
        onSelectTab={onSelectTab}
        isMobileOpen={isMobileOpen}
        onCloseMobile={() => setIsMobileOpen(false)}
      />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0">
        <ApplicationHeader
          activeTab={activeTab}
          onOpenMobileNav={() => setIsMobileOpen(true)}
        />

        <main className="flex-1 p-4 sm:p-6 lg:p-8 max-w-7xl w-full mx-auto">
          {children}
        </main>

        <footer className="border-t border-[#E5E5E2] py-4 px-6 text-xs text-[#858585] font-mono flex flex-col sm:flex-row items-center justify-between gap-2 max-w-7xl mx-auto w-full">
          <span>vigilX • Digital Risk Protection Platform</span>
          <span className="flex items-center gap-2">
            <span className="w-1.5 h-1.5 rounded-full bg-[#111111]" />
            Architecture: FastAPI + Supabase Core
          </span>
        </footer>
      </div>
    </div>
  )
}
