import { useRecordingStore } from '../../stores/recordingStore'
import type { AudioDevice } from '../../types'

interface TopBarProps {
  audioDevices: AudioDevice[]
  selectedDeviceIndex: number
  onDeviceChange: (index: number) => void
}

function formatElapsed(seconds: number): string {
  const m = Math.floor(seconds / 60)
  const s = seconds % 60
  return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`
}

function StatusPill({ isRecording }: { isRecording: boolean }) {
  if (isRecording) {
    return (
      <span className="flex items-center gap-1.5 text-sm font-medium text-red-400">
        <span className="h-2 w-2 animate-pulse rounded-full bg-red-400" />
        Recording
      </span>
    )
  }
  return (
    <span className="text-sm font-medium text-gray-500">Idle</span>
  )
}

export default function TopBar({
  audioDevices,
  selectedDeviceIndex,
  onDeviceChange,
}: TopBarProps) {
  const isRecording = useRecordingStore((s) => s.isRecording)
  const elapsedSeconds = useRecordingStore((s) => s.elapsedSeconds)
  const setRecording = useRecordingStore((s) => s.setRecording)

  function handleToggleRecording() {
    setRecording(!isRecording)
  }

  return (
    <header className="flex h-12 shrink-0 items-center gap-4 border-b border-gray-800 bg-gray-950 px-4">
      {/* Record / Stop button */}
      <button
        onClick={handleToggleRecording}
        className={[
          'flex items-center gap-2 rounded-md px-3 py-1.5 text-sm font-medium transition-colors',
          isRecording
            ? 'bg-red-600 text-white hover:bg-red-700'
            : 'bg-brand-600 text-white hover:bg-brand-700',
        ].join(' ')}
      >
        {isRecording ? (
          <>
            <span className="h-3 w-3 rounded-sm bg-white" aria-hidden="true" />
            Stop
          </>
        ) : (
          <>
            <span className="h-3 w-3 rounded-full bg-white" aria-hidden="true" />
            Record
          </>
        )}
      </button>

      {/* Status */}
      <StatusPill isRecording={isRecording} />

      {/* Elapsed time while recording */}
      {isRecording && (
        <span className="font-mono text-sm text-red-400">
          {formatElapsed(elapsedSeconds)}
        </span>
      )}

      {/* Spacer */}
      <div className="flex-1" />

      {/* Device selector */}
      <label className="flex items-center gap-2 text-sm text-gray-400">
        <span className="hidden sm:inline">Input</span>
        <select
          value={selectedDeviceIndex}
          onChange={(e) => onDeviceChange(Number(e.target.value))}
          className="rounded-md border border-gray-700 bg-gray-900 px-2 py-1 text-sm text-gray-200 focus:outline-none focus:ring-1 focus:ring-brand-500"
          disabled={audioDevices.length === 0}
        >
          {audioDevices.length === 0 ? (
            <option value={-1}>Default device</option>
          ) : (
            audioDevices.map((device) => (
              <option key={device.index} value={device.index}>
                {device.name}
              </option>
            ))
          )}
        </select>
      </label>
    </header>
  )
}
