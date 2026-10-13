import { useState } from 'react'
import { Shield } from 'lucide-react'
import { AuthProvider } from './context/AuthContext'
import { useAuth } from './context/useAuth'
import { AuthView } from './components/auth/AuthView'
import { ApplicationLayout } from './components/layout/ApplicationLayout'
import type { NavigationTab } from './components/layout/ApplicationSidebar'
import { OverviewView } from './components/views/OverviewView'
import { BrandsAndAssetsView } from './components/views/BrandsAndAssetsView'
import { ThreatIntelligenceView } from './components/views/ThreatIntelligenceView'
import { SettingsView } from './components/views/SettingsView'

function AuthenticatedApp() {
  const { session, isLoading } = useAuth()
  const [activeTab, setActiveTab] = useState<NavigationTab>('overview')
  const [selectedBrandId, setSelectedBrandId] = useState<string | null>(null)

  // 1. Initial Session Loading State
  if (isLoading) {
    return (
      <div className="min-h-screen bg-[#F7F7F5] flex flex-col items-center justify-center p-4">
        <div className="flex flex-col items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-[#111111] text-white flex items-center justify-center font-bold animate-pulse shadow-sm">
            <Shield className="w-5 h-5 text-white" />
          </div>
          <p className="text-xs font-mono text-[#858585] uppercase tracking-widest">
            Synchronizing session...
          </p>
        </div>
      </div>
    )
  }

  // 2. Unauthenticated State: Show Sign-In / Sign-Up
  if (!session) {
    return <AuthView />
  }

  // 3. Authenticated State: Show Full Dashboard
  return (
    <ApplicationLayout activeTab={activeTab} onSelectTab={setActiveTab}>
      {activeTab === 'overview' && (
        <OverviewView onNavigateToBrands={() => setActiveTab('brands-assets')} />
      )}
      {activeTab === 'brands-assets' && (
        <BrandsAndAssetsView
          initialSelectedBrandId={selectedBrandId}
          onBrandSelect={(brand) => setSelectedBrandId(brand ? brand.id : null)}
        />
      )}
      {activeTab === 'threat-intel' && <ThreatIntelligenceView />}
      {activeTab === 'settings' && <SettingsView />}
    </ApplicationLayout>
  )
}

export function App() {
  return (
    <AuthProvider>
      <AuthenticatedApp />
    </AuthProvider>
  )
}

export default App
