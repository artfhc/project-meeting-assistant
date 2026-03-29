import { useMeetingStore } from '../../stores/meetingStore'
import { useRecordingStore } from '../../stores/recordingStore'
import { useJobStore } from '../../stores/jobStore'
import type { Job } from '../../types'

function formatElapsed(seconds: number): string {
  const m = Math.floor(seconds / 60)
  const s = seconds % 60
  return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`
}

function JobStatusIndicator({ job }: { job: Job }) {
  const isInProgress = job.stage !== 'done' && job.stage !== 'error'
  const isError = job.stage === 'error'

  return (
    <div className="flex items-center gap-3">
      {/* Stage label */}
      <span
        className="text-xs capitalize tabular-nums"
        style={{ color: isError ? '#f87171' : 'var(--color-text-muted)' }}
      >
        {job.message || job.stage}
      </span>

      {/* Progress bar — amber fill, very subtle track */}
      {isInProgress && (
        <div
          className="h-0.5 w-24 overflow-hidden"
          style={{ backgroundColor: 'var(--color-border-muted)' }}
        >
          <div
            className="h-full transition-all duration-300"
            style={{
              width: `${job.progress}%`,
              backgroundColor: 'var(--color-amber)',
            }}
            role="progressbar"
            aria-valuenow={job.progress}
            aria-valuemin={0}
            aria-valuemax={100}
          />
        </div>
      )}

      {/* Percentage */}
      {isInProgress && (
        <span
          className="text-xs tabular-nums"
          style={{ color: 'var(--color-text-faint)' }}
        >
          {job.progress}%
        </span>
      )}
    </div>
  )
}

export default function BottomBar() {
  const elapsedSeconds = useRecordingStore((s) => s.elapsedSeconds)
  const selectedMeetingId = useMeetingStore((s) => s.selectedMeetingId)
  const meetings = useMeetingStore((s) => s.meetings)
  const jobs = useJobStore((s) => s.jobs)

  const selectedMeeting = meetings.find((m) => m.id === selectedMeetingId) ?? null
  const activeJob = selectedMeetingId ? jobs[selectedMeetingId] ?? null : null

  return (
    <footer
      className="flex h-8 shrink-0 items-center gap-4 border-t px-4"
      style={{
        backgroundColor: 'var(--color-bg-raised)',
        borderColor: 'var(--color-border-subtle)',
      }}
    >
      {/* Elapsed time */}
      <span
        className="text-xs tabular-nums"
        style={{ color: 'var(--color-text-faint)' }}
      >
        {formatElapsed(elapsedSeconds)}
      </span>

      {/* Unicode separator */}
      <span
        className="text-xs"
        style={{ color: 'var(--color-border-muted)' }}
        aria-hidden="true"
      >
        &#x2502;
      </span>

      {/* Save path */}
      <span
        className="flex-1 truncate text-xs"
        style={{ color: 'var(--color-text-faint)' }}
        title={selectedMeeting?.audio_path ?? undefined}
      >
        {selectedMeeting?.audio_path ?? 'no file selected'}
      </span>

      {/* Job status */}
      {activeJob && <JobStatusIndicator job={activeJob} />}
    </footer>
  )
}
