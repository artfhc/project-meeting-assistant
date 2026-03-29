import { useMeetingStore } from '../../stores/meetingStore'

function EmptyState({ message }: { message: string }) {
  return (
    <div className="flex h-full items-center justify-center p-8">
      <div
        className="flex flex-col items-center gap-3 p-6"
        style={{
          border: '1px dashed var(--color-border-muted)',
        }}
      >
        <svg
          className="h-5 w-5"
          fill="none"
          stroke="currentColor"
          strokeWidth={1}
          viewBox="0 0 24 24"
          style={{ color: 'var(--color-text-faint)' }}
          aria-hidden="true"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            d="M3.75 6.75h16.5M3.75 12h16.5m-16.5 5.25H12"
          />
        </svg>
        <p className="text-center text-xs" style={{ color: 'var(--color-text-faint)' }}>
          {message}
        </p>
      </div>
    </div>
  )
}

export default function TranscriptPanel() {
  const selectedMeetingId = useMeetingStore((s) => s.selectedMeetingId)
  const meetings = useMeetingStore((s) => s.meetings)

  const meeting = meetings.find((m) => m.id === selectedMeetingId) ?? null

  if (!meeting) {
    return <EmptyState message="Select a meeting to view its transcript." />
  }

  if (!meeting.transcript) {
    const isInProgress =
      meeting.status === 'transcribing' || meeting.status === 'recording'
    return (
      <EmptyState
        message={
          isInProgress
            ? 'Transcript will appear here once transcription completes.'
            : 'No transcript available yet.'
        }
      />
    )
  }

  return (
    <div className="h-full overflow-y-auto">
      <div className="p-4">
        <pre
          className="whitespace-pre-wrap break-words text-xs leading-relaxed"
          style={{ color: 'var(--color-text-base)', fontFamily: '"DM Mono", monospace' }}
        >
          {meeting.transcript}
        </pre>
      </div>
    </div>
  )
}
