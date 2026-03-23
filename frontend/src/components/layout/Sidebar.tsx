import { useEffect, useState } from 'react'
import type { ActiveView } from './MainLayout'

interface SidebarProps {
  activeView: ActiveView
  onNavigate: (view: ActiveView) => void
}

interface NavItem {
  id: ActiveView
  label: string
  icon: string
}

const NAV_ITEMS: NavItem[] = [
  { id: 'new', label: 'New Meeting', icon: 'M12 4v16m8-8H4' },
  {
    id: 'history',
    label: 'History',
    icon: 'M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z',
  },
  {
    id: 'settings',
    label: 'Settings',
    icon: 'M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z M15 12a3 3 0 11-6 0 3 3 0 016 0z',
  },
]

export default function Sidebar({ activeView, onNavigate }: SidebarProps) {
  const [version, setVersion] = useState<string>('')

  useEffect(() => {
    window.electronAPI
      ?.getVersion()
      .then((v) => setVersion(v))
      .catch(() => setVersion(''))
  }, [])

  return (
    <aside className="flex h-full w-[var(--sidebar-width)] flex-col border-r border-gray-800 bg-gray-950">
      {/* App name */}
      <div className="px-4 py-5">
        <span className="text-sm font-semibold tracking-wide text-gray-200">
          Meeting Assistant
        </span>
      </div>

      {/* Navigation */}
      <nav className="flex-1 space-y-1 px-2">
        {NAV_ITEMS.map((item) => {
          const isActive = activeView === item.id
          return (
            <button
              key={item.id}
              onClick={() => onNavigate(item.id)}
              className={[
                'flex w-full items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors',
                isActive
                  ? 'bg-gray-800 text-white'
                  : 'text-gray-400 hover:bg-gray-800/60 hover:text-gray-100',
              ].join(' ')}
            >
              <svg
                className="h-4 w-4 shrink-0"
                fill="none"
                stroke="currentColor"
                strokeWidth={1.5}
                viewBox="0 0 24 24"
                aria-hidden="true"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d={item.icon}
                />
              </svg>
              {item.label}
            </button>
          )
        })}
      </nav>

      {/* Version footer */}
      {version && (
        <div className="px-4 py-3">
          <span className="text-xs text-gray-600">v{version}</span>
        </div>
      )}
    </aside>
  )
}
