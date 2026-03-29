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
    <aside
      className="flex h-full flex-col border-r"
      style={{
        width: 'var(--sidebar-width)',
        backgroundColor: 'var(--color-bg-raised)',
        borderColor: 'var(--color-border-warm)',
      }}
    >
      {/* App name with amber accent mark */}
      <div className="px-4 py-5">
        <span
          className="text-xs tracking-widest uppercase"
          style={{ color: 'var(--color-text-muted)' }}
        >
          <span style={{ color: 'var(--color-amber)' }}>&#9632; </span>
          Meeting Asst
        </span>
      </div>

      {/* Navigation — left border accent for active state, no rounded corners */}
      <nav className="flex-1 space-y-px">
        {NAV_ITEMS.map((item) => {
          const isActive = activeView === item.id
          return (
            <button
              key={item.id}
              onClick={() => onNavigate(item.id)}
              className="flex w-full items-center gap-3 py-2.5 text-xs tracking-wide transition-colors"
              style={
                isActive
                  ? {
                      borderLeft: '2px solid var(--color-amber)',
                      backgroundColor: 'var(--color-bg-overlay)',
                      color: '#e4e4e7',
                      paddingLeft: '14px',
                      paddingRight: '16px',
                    }
                  : {
                      borderLeft: '2px solid transparent',
                      color: 'var(--color-text-muted)',
                      paddingLeft: '14px',
                      paddingRight: '16px',
                    }
              }
              onMouseEnter={(e) => {
                if (!isActive) {
                  const el = e.currentTarget as HTMLButtonElement
                  el.style.color = '#a1a1aa'
                  el.style.backgroundColor = 'var(--color-bg-overlay)'
                }
              }}
              onMouseLeave={(e) => {
                if (!isActive) {
                  const el = e.currentTarget as HTMLButtonElement
                  el.style.color = 'var(--color-text-muted)'
                  el.style.backgroundColor = 'transparent'
                }
              }}
            >
              <svg
                className="h-3.5 w-3.5 shrink-0"
                fill="none"
                stroke="currentColor"
                strokeWidth={1.5}
                viewBox="0 0 24 24"
                aria-hidden="true"
              >
                <path strokeLinecap="round" strokeLinejoin="round" d={item.icon} />
              </svg>
              {item.label}
            </button>
          )
        })}
      </nav>

      {/* Version — ultra-muted */}
      {version && (
        <div className="px-4 py-3">
          <span
            className="text-xs tabular-nums"
            style={{ color: 'var(--color-text-faint)' }}
          >
            v{version}
          </span>
        </div>
      )}
    </aside>
  )
}
