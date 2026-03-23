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
        className={[
          'text-xs font-medium capitalize',
          isError ? 'text-red-400' : 'text-gray-400',
        ].join(' ')}
      >
        {job.message || job.stage}
      </span>

      {/* Progress bar */}
      {isInProgress && (
        <div className="h-1.5 w-24 overflow-hidden rounded-full bg-gray-800">
          <div
            className="h-full rounded-full bg-brand-500 transition-all duration-300"
            style={{ width: `${job.progress}%` }}
            role="progressbar"
            aria-valuenow={job.progress}
            aria-valuemin={0}
            aria-valuemax={100}
          />
        </div>
      )}

      {/* Percentage */}
      {isInProgress && (
        <span className="text-xs tabular-nums text-gray-500">
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
    <footer className="flex h-9 shrink-0 items-center gap-4 border-t border-gray-800 bg-gray-950 px-4">
      {/* Elapsed time */}
      <span className="font-mono text-xs tabular-nums text-gray-500">
        {formatElapsed(elapsedSeconds)}
      </span>

      <span className="text-gray-800" aria-hidden="true">|</span>

      {/* Save path */}
      <span
        className="flex-1 truncate text-xs text-gray-600"
        title={selectedMeeting?.audio_path ?? undefined}
      >
        {selectedMeeting?.audio_path ?? 'No file selected'}
      </span>

      {/* Job status */}
      {activeJob && <JobStatusIndicator job={activeJob} />}
    </footer>
  )
}
