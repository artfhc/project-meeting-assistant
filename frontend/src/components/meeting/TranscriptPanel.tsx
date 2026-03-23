import { useMeetingStore } from '../../stores/meetingStore'

export default function TranscriptPanel() {
  const selectedMeetingId = useMeetingStore((s) => s.selectedMeetingId)
  const meetings = useMeetingStore((s) => s.meetings)

  const meeting = meetings.find((m) => m.id === selectedMeetingId) ?? null

  if (!meeting) {
    return (
      <div className="flex h-full items-center justify-center">
        <p className="text-sm text-gray-600">
          Select a meeting to view its transcript.
        </p>
      </div>
    )
  }

  if (!meeting.transcript) {
    const isInProgress =
      meeting.status === 'transcribing' || meeting.status === 'recording'

    return (
      <div className="flex h-full items-center justify-center">
        <p className="text-sm text-gray-600">
          {isInProgress
            ? 'Transcript will appear here once transcription completes.'
            : 'No transcript available yet.'}
        </p>
      </div>
    )
  }

  return (
    <div className="h-full overflow-y-auto">
      <div className="p-4">
        <pre className="whitespace-pre-wrap break-words font-mono text-sm leading-relaxed text-gray-300">
          {meeting.transcript}
        </pre>
      </div>
    </div>
  )
}
