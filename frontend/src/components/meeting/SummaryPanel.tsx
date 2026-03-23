import { useMeetingStore } from '../../stores/meetingStore'

export default function SummaryPanel() {
  const selectedMeetingId = useMeetingStore((s) => s.selectedMeetingId)
  const meetings = useMeetingStore((s) => s.meetings)

  const meeting = meetings.find((m) => m.id === selectedMeetingId) ?? null

  if (!meeting) {
    return (
      <div className="flex h-full items-center justify-center">
        <p className="text-sm text-gray-600">
          Select a meeting to view its summary.
        </p>
      </div>
    )
  }

  if (!meeting.summary) {
    const isInProgress =
      meeting.status === 'summarizing' ||
      meeting.status === 'transcribing' ||
      meeting.status === 'transcribed'

    return (
      <div className="flex h-full items-center justify-center">
        <p className="text-sm text-gray-600">
          {isInProgress
            ? 'Summary will appear here once processing completes.'
            : 'No summary available yet.'}
        </p>
      </div>
    )
  }

  return (
    <div className="h-full overflow-y-auto">
      <div className="p-4">
        <pre className="whitespace-pre-wrap break-words text-sm leading-relaxed text-gray-300">
          {meeting.summary}
        </pre>
      </div>
    </div>
  )
}
