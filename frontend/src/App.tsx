import { useEffect, useRef, useState } from 'react'
import MainLayout from './components/layout/MainLayout'
import { useWebSocket } from './hooks/useWebSocket'
import { useRecordingStore } from './stores/recordingStore'
import { useMeetingStore } from './stores/meetingStore'
import { useSettingsStore } from './stores/settingsStore'
import { listMeetings } from './api/meetings'
import { getSettings } from './api/settings'
import { BASE_URL } from './api/client'

declare global {
  interface Window {
    electronAPI?: {
      openFolder(): Promise<string | null>
      saveFile(options?: {
        defaultPath?: string
        filters?: Array<{ name: string; extensions: string[] }>
      }): Promise<string | null>
      getVersion(): Promise<string>
    }
  }
}

// ---------------------------------------------------------------------------
// Loading / error screens
// ---------------------------------------------------------------------------

function LoadingScreen() {
  return (
    <div className="flex h-full flex-col items-center justify-center gap-3 bg-gray-950">
      <div className="h-6 w-6 animate-spin rounded-full border-2 border-gray-700 border-t-brand-500" />
      <p className="text-sm text-gray-500">Starting backend...</p>
    </div>
  )
}

function ErrorScreen({ message }: { message: string }) {
  return (
    <div className="flex h-full flex-col items-center justify-center gap-3 bg-gray-950 px-8">
      <p className="text-sm font-medium text-red-400">Backend failed to start</p>
      <p className="max-w-sm text-center text-xs text-gray-600">{message}</p>
    </div>
  )
}

// ---------------------------------------------------------------------------
// Inner app — rendered only once the backend is ready
// ---------------------------------------------------------------------------

function AppInner() {
  useWebSocket()

  const isRecording = useRecordingStore((s) => s.isRecording)
  const tickElapsed = useRecordingStore((s) => s.tickElapsed)
  const resetElapsed = useRecordingStore((s) => s.resetElapsed)
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null)

  // Drive the elapsed-time counter whenever recording is active
  useEffect(() => {
    if (isRecording) {
      resetElapsed()
      timerRef.current = setInterval(tickElapsed, 1000)
    } else {
      if (timerRef.current !== null) {
        clearInterval(timerRef.current)
        timerRef.current = null
      }
    }
    return () => {
      if (timerRef.current !== null) {
        clearInterval(timerRef.current)
      }
    }
  }, [isRecording, tickElapsed, resetElapsed])

  return <MainLayout />
}

// ---------------------------------------------------------------------------
// App — orchestrates backend readiness
// ---------------------------------------------------------------------------

type AppState = 'loading' | 'ready' | 'error'

async function loadInitialData(
  setMeetings: ReturnType<typeof useMeetingStore.getState>['setMeetings'],
  setSettings: ReturnType<typeof useSettingsStore.getState>['setSettings'],
) {
  try {
    const [meetings, settings] = await Promise.all([listMeetings(), getSettings()])
    setMeetings(meetings)
    setSettings(settings)
  } catch (err) {
    console.error('[App] Failed to load initial data:', err)
  }
}

const POLL_INTERVAL_MS = 500
const POLL_TIMEOUT_MS = 30_000

function pollBackendReady(signal: AbortSignal): Promise<void> {
  return new Promise((resolve, reject) => {
    const deadline = Date.now() + POLL_TIMEOUT_MS
    let timerId: ReturnType<typeof setTimeout> | null = null

    signal.addEventListener('abort', () => {
      if (timerId !== null) clearTimeout(timerId)
      reject(new DOMException('Aborted', 'AbortError'))
    })

    const attempt = () => {
      if (signal.aborted) return
      fetch(`${BASE_URL}/health`)
        .then((r) => {
          void r.body?.cancel()
          if (r.ok) resolve(); else schedule()
        })
        .catch(() => schedule())
    }
    const schedule = () => {
      if (signal.aborted) return
      if (Date.now() > deadline) {
        reject(new Error('Backend did not become ready in time'))
      } else {
        timerId = setTimeout(attempt, POLL_INTERVAL_MS)
      }
    }
    attempt()
  })
}

export default function App() {
  const [appState, setAppState] = useState<AppState>('loading')
  const [errorMessage, setErrorMessage] = useState('')

  const setMeetings = useMeetingStore((s) => s.setMeetings)
  const setSettings = useSettingsStore((s) => s.setSettings)

  useEffect(() => {
    document.documentElement.classList.add('dark')

    const controller = new AbortController()
    pollBackendReady(controller.signal)
      .then(() => {
        setAppState('ready')
        return loadInitialData(setMeetings, setSettings)
      })
      .catch((err: Error) => {
        if (err.name === 'AbortError') return
        setErrorMessage(err.message)
        setAppState('error')
      })
    return () => controller.abort()
  }, [setMeetings, setSettings])

  if (appState === 'loading') return <LoadingScreen />
  if (appState === 'error') return <ErrorScreen message={errorMessage} />
  return <AppInner />
}
