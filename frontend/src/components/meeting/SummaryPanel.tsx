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
            d="M9.813 15.904 9 18.75l-.813-2.846a4.5 4.5 0 0 0-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 0 0 3.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 0 0 3.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 0 0-3.09 3.09Z"
          />
        </svg>
        <p className="text-center text-xs" style={{ color: 'var(--color-text-faint)' }}>
          {message}
        </p>
      </div>
    </div>
  )
}

export default function SummaryPanel() {
  const selectedMeetingId = useMeetingStore((s) => s.selectedMeetingId)
  const meetings = useMeetingStore((s) => s.meetings)

  const meeting = meetings.find((m) => m.id === selectedMeetingId) ?? null

  if (!meeting) {
    return <EmptyState message="Select a meeting to view its summary." />
  }

  if (!meeting.summary) {
    const isInProgress =
      meeting.status === 'summarizing' ||
      meeting.status === 'transcribing' ||
      meeting.status === 'transcribed'
    return (
      <EmptyState
        message={
          isInProgress
            ? 'Summary will appear here once processing completes.'
            : 'No summary available yet.'
        }
      />
    )
  }

  return (
    <div className="h-full overflow-y-auto">
      <div className="p-4">
        <pre
          className="whitespace-pre-wrap break-words text-xs leading-relaxed"
          style={{
            color: 'var(--color-text-base)',
            fontFamily: '"DM Mono", monospace',
          }}
        >
          {meeting.summary}
        </pre>
      </div>
    </div>
  )
}
