import { useEffect, useRef, useState } from 'react'
import { useRecordingStore } from '../../stores/recordingStore'
import { useMeetingStore } from '../../stores/meetingStore'
import { useJobStore } from '../../stores/jobStore'
import { useSettingsStore } from '../../stores/settingsStore'
import { createMeeting, getMeeting } from '../../api/meetings'
import { startRecording, stopRecording } from '../../api/recordings'
import { enqueueTranscription } from '../../api/transcriptions'
import { enqueueSummary } from '../../api/summaries'
import { listAudioDevices } from '../../api/devices'
import type { AudioDevice } from '../../types'

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

// Stages that belong to the transcription phase (before summarization kicks off)
const TRANSCRIPTION_STAGES = new Set(['transcribing', 'cleaning'])

export default function TopBar() {
  const isRecording = useRecordingStore((s) => s.isRecording)
  const elapsedSeconds = useRecordingStore((s) => s.elapsedSeconds)
  const currentMeetingId = useRecordingStore((s) => s.currentMeetingId)
  const setRecording = useRecordingStore((s) => s.setRecording)
  const setCurrentMeeting = useRecordingStore((s) => s.setCurrentMeeting)
  const resetElapsed = useRecordingStore((s) => s.resetElapsed)

  const upsertMeeting = useMeetingStore((s) => s.upsertMeeting)
  const selectMeeting = useMeetingStore((s) => s.selectMeeting)

  const jobs = useJobStore((s) => s.jobs)
  const defaultPromptKey = useSettingsStore((s) => s.settings?.default_prompt_key)

  const [audioDevices, setAudioDevices] = useState<AudioDevice[]>([])
  const [selectedDeviceIndex, setSelectedDeviceIndex] = useState(-1)
  const [isBusy, setIsBusy] = useState(false)

  // Tracks the job stage from the previous render so we can tell which phase
  // just completed when the stage transitions to 'done'.
  const prevStageRef = useRef<string | null>(null)

  // ---------------------------------------------------------------------------
  // Load audio devices on mount
  // ---------------------------------------------------------------------------

  useEffect(() => {
    listAudioDevices()
      .then((devices) => {
        setAudioDevices(devices)
        if (devices.length > 0) {
          setSelectedDeviceIndex(devices[0].index)
        }
      })
      .catch((err) => {
        console.error('[TopBar] Failed to load audio devices:', err)
      })
  }, [])

  // ---------------------------------------------------------------------------
  // Job watcher — drives post-transcription and post-summarization side effects
  // ---------------------------------------------------------------------------

  useEffect(() => {
    if (!currentMeetingId) return

    const job = jobs[currentMeetingId]
    if (!job) return

    const prevStage = prevStageRef.current
    const currentStage = job.stage

    if (currentStage === 'done') {
      if (prevStage !== null && TRANSCRIPTION_STAGES.has(prevStage)) {
        // Transcription phase just completed — fetch updated meeting, then enqueue summary
        getMeeting(currentMeetingId)
          .then((meeting) => {
            upsertMeeting(meeting)
            return enqueueSummary(currentMeetingId, defaultPromptKey ?? null)
          })
          .catch((err) => {
            console.error('[TopBar] Error after transcription done:', err)
          })
      } else if (prevStage === 'summarizing') {
        // Summarization phase just completed — refresh meeting data
        getMeeting(currentMeetingId)
          .then(upsertMeeting)
          .catch((err) => {
            console.error('[TopBar] Error after summarization done:', err)
          })
      }
    } else if (currentStage === 'error') {
      getMeeting(currentMeetingId)
        .then(upsertMeeting)
        .catch((err) => {
          console.error('[TopBar] Error refreshing meeting after job error:', err)
        })
    }

    prevStageRef.current = currentStage
  }, [jobs, currentMeetingId, upsertMeeting, defaultPromptKey])

  // ---------------------------------------------------------------------------
  // Record / Stop handlers
  // ---------------------------------------------------------------------------

  async function handleStartRecording() {
    setIsBusy(true)
    try {
      const title = `Meeting ${new Date().toLocaleString()}`
      const meeting = await createMeeting({ title })
      upsertMeeting(meeting)
      selectMeeting(meeting.id)
      await startRecording(meeting.id)
      setRecording(true)
      setCurrentMeeting(meeting.id)
    } catch (err) {
      console.error('[TopBar] Failed to start recording:', err)
    } finally {
      setIsBusy(false)
    }
  }

  async function handleStopRecording() {
    if (!currentMeetingId) return
    setIsBusy(true)
    try {
      await stopRecording(currentMeetingId, elapsedSeconds)
      setRecording(false)
      resetElapsed()
      // Reset the stage tracker so the job watcher starts fresh for this meeting
      prevStageRef.current = null
      await enqueueTranscription(currentMeetingId)
    } catch (err) {
      console.error('[TopBar] Failed to stop recording:', err)
    } finally {
      setIsBusy(false)
    }
  }

  function handleToggle() {
    if (isRecording) {
      void handleStopRecording()
    } else {
      void handleStartRecording()
    }
  }

  return (
    <header className="flex h-12 shrink-0 items-center gap-4 border-b border-gray-800 bg-gray-950 px-4">
      {/* Record / Stop button */}
      <button
        onClick={handleToggle}
        disabled={isBusy}
        className={[
          'flex items-center gap-2 rounded-md px-3 py-1.5 text-sm font-medium transition-colors disabled:cursor-not-allowed disabled:opacity-50',
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
          onChange={(e) => setSelectedDeviceIndex(Number(e.target.value))}
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
