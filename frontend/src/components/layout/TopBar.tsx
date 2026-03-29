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
      <span
        className="flex items-center gap-1.5 text-xs tracking-widest uppercase"
        style={{ color: 'var(--color-amber)' }}
      >
        {/* Pulsing amber dot */}
        <span
          className="h-1.5 w-1.5 rounded-full"
          style={{
            backgroundColor: 'var(--color-amber)',
            animation: 'dot-pulse 1.4s ease-in-out infinite',
          }}
          aria-hidden="true"
        />
        Recording
      </span>
    )
  }
  return (
    <span
      className="text-xs tracking-widest uppercase"
      style={{ color: 'var(--color-text-faint)' }}
    >
      Idle
    </span>
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
    <header
      className="flex h-12 shrink-0 items-center gap-5 border-b px-4"
      style={{
        backgroundColor: 'var(--color-bg-raised)',
        borderColor: 'var(--color-border-warm)',
      }}
    >
      {/* Record / Stop button — physical hardware feel */}
      <button
        onClick={handleToggle}
        disabled={isBusy}
        className="flex items-center gap-2.5 px-4 py-1.5 text-xs tracking-widest uppercase transition-all disabled:cursor-not-allowed disabled:opacity-40"
        style={
          isRecording
            ? {
                backgroundColor: '#1a1200',
                color: 'var(--color-amber)',
                border: '1px solid var(--color-amber)',
                boxShadow: '0 0 12px rgba(245,158,11,0.25), inset 0 1px 2px rgba(0,0,0,0.6)',
                animation: 'amber-pulse 2s ease-in-out infinite',
              }
            : {
                backgroundColor: 'var(--color-bg-muted)',
                color: '#e4e4e7',
                border: '1px solid var(--color-border-muted)',
                boxShadow: 'inset 0 1px 2px rgba(0,0,0,0.5)',
              }
        }
      >
        {isRecording ? (
          <>
            {/* Square stop icon */}
            <span
              className="h-2.5 w-2.5 shrink-0"
              style={{ backgroundColor: 'var(--color-amber)', borderRadius: '1px' }}
              aria-hidden="true"
            />
            Stop
          </>
        ) : (
          <>
            {/* Circle record icon */}
            <span
              className="h-2.5 w-2.5 shrink-0 rounded-full bg-white"
              aria-hidden="true"
            />
            REC
          </>
        )}
      </button>

      {/* Status */}
      <StatusPill isRecording={isRecording} />

      {/* Elapsed time — large monospace, amber when recording */}
      {isRecording && (
        <span
          className="tabular-nums"
          style={{
            color: 'var(--color-amber)',
            fontSize: '15px',
            letterSpacing: '0.05em',
          }}
        >
          {formatElapsed(elapsedSeconds)}
        </span>
      )}

      <div className="flex-1" />

      {/* Device selector — dark aesthetic, minimal border */}
      <label
        className="flex items-center gap-2 text-xs"
        style={{ color: 'var(--color-text-muted)' }}
      >
        <span>Input</span>
        <select
          value={selectedDeviceIndex}
          onChange={(e) => setSelectedDeviceIndex(Number(e.target.value))}
          disabled={audioDevices.length === 0}
          className="text-xs focus:outline-none"
          style={{
            backgroundColor: 'var(--color-bg-muted)',
            border: '1px solid var(--color-border-muted)',
            color: '#a1a1aa',
            padding: '3px 8px',
            maxWidth: '200px',
          }}
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
