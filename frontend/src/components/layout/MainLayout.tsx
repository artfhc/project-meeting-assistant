import { useState } from 'react'
import Sidebar from './Sidebar'
import TopBar from './TopBar'
import BottomBar from './BottomBar'
import NewMeetingView from '../meeting/NewMeetingView'
import HistoryView from '../meeting/HistoryView'
import SettingsPage from '../settings/SettingsPage'

export type ActiveView = 'new' | 'history' | 'settings'

export default function MainLayout() {
  const [activeView, setActiveView] = useState<ActiveView>('new')

  // Placeholder device state — Phase 4 will populate this from GET /audio-devices
  const [selectedDeviceIndex, setSelectedDeviceIndex] = useState(-1)

  function renderContent() {
    switch (activeView) {
      case 'new':
        return <NewMeetingView />
      case 'history':
        return <HistoryView />
      case 'settings':
        return (
          <section className="flex flex-1 overflow-hidden">
            <SettingsPage />
          </section>
        )
    }
  }

  return (
    <div className="flex h-full flex-col bg-gray-950 text-gray-100">
      {/* Top bar */}
      <TopBar
        audioDevices={[]}
        selectedDeviceIndex={selectedDeviceIndex}
        onDeviceChange={setSelectedDeviceIndex}
      />

      {/* Body: sidebar + main content panels */}
      <div className="flex min-h-0 flex-1">
        <Sidebar activeView={activeView} onNavigate={setActiveView} />

        {/* Content area — flex row so view components can render sub-columns */}
        <main className="flex min-w-0 flex-1 overflow-hidden">
          {renderContent()}
        </main>
      </div>

      {/* Bottom bar */}
      <BottomBar />
    </div>
  )
}
