import { useEffect, useRef, useState } from 'react'
import MainLayout from './components/layout/MainLayout'
import { useWebSocket } from './hooks/useWebSocket'
import { useRecordingStore } from './stores/recordingStore'

// ---------------------------------------------------------------------------
// Extend window with the Electron context bridge API
// ---------------------------------------------------------------------------

declare global {
  interface Window {
    electronAPI?: {
      openFolder(): Promise<string | null>
      saveFile(options?: {
        defaultPath?: string
        filters?: Array<{ name: string; extensions: string[] }>
      }): Promise<string | null>
      getVersion(): Promise<string>
      onBackendReady(cb: () => void): () => void
      onBackendError(cb: (msg: string) => void): () => void
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

export default function App() {
  const [appState, setAppState] = useState<AppState>('loading')
  const [errorMessage, setErrorMessage] = useState('')

  useEffect(() => {
    // Apply dark mode class unconditionally — settings store can toggle later
    document.documentElement.classList.add('dark')

    // If running outside Electron (e.g. plain Vite dev server), skip IPC
    if (!window.electronAPI) {
      setAppState('ready')
      return
    }

    const unsubReady = window.electronAPI.onBackendReady(() => {
      setAppState('ready')
    })

    const unsubError = window.electronAPI.onBackendError((msg) => {
      setErrorMessage(msg)
      setAppState('error')
    })

    return () => {
      unsubReady()
      unsubError()
    }
  }, [])

  if (appState === 'loading') return <LoadingScreen />
  if (appState === 'error') return <ErrorScreen message={errorMessage} />
  return <AppInner />
}
