import { useMeetingStore } from '../../stores/meetingStore'
import type { Meeting, MeetingStatus } from '../../types'

// ---------------------------------------------------------------------------
// Status badge
// ---------------------------------------------------------------------------

const STATUS_STYLES: Record<MeetingStatus, string> = {
  created: 'bg-gray-800 text-gray-400',
  recording: 'bg-blue-900/60 text-blue-300',
  recorded: 'bg-gray-800 text-gray-400',
  transcribing: 'bg-yellow-900/60 text-yellow-300',
  transcribed: 'bg-yellow-900/40 text-yellow-400',
  summarizing: 'bg-yellow-900/60 text-yellow-300',
  done: 'bg-green-900/60 text-green-300',
  error: 'bg-red-900/60 text-red-300',
}

const STATUS_LABELS: Record<MeetingStatus, string> = {
  created: 'Created',
  recording: 'Recording',
  recorded: 'Recorded',
  transcribing: 'Transcribing',
  transcribed: 'Transcribed',
  summarizing: 'Summarizing',
  done: 'Done',
  error: 'Error',
}

function StatusBadge({ status }: { status: MeetingStatus }) {
  return (
    <span
      className={[
        'inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium',
        STATUS_STYLES[status],
      ].join(' ')}
    >
      {STATUS_LABELS[status]}
    </span>
  )
}

// ---------------------------------------------------------------------------
// Meeting row
// ---------------------------------------------------------------------------

function formatDate(isoString: string): string {
  const date = new Date(isoString)
  return date.toLocaleDateString(undefined, {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  })
}

function MeetingRow({
  meeting,
  isSelected,
  onSelect,
}: {
  meeting: Meeting
  isSelected: boolean
  onSelect: () => void
}) {
  return (
    <button
      onClick={onSelect}
      className={[
        'flex w-full flex-col gap-1 rounded-md px-3 py-2.5 text-left transition-colors',
        isSelected
          ? 'bg-gray-800 text-white'
          : 'text-gray-300 hover:bg-gray-800/60',
      ].join(' ')}
    >
      <div className="flex items-start justify-between gap-2">
        <span className="truncate text-sm font-medium leading-tight">
          {meeting.title}
        </span>
        <StatusBadge status={meeting.status} />
      </div>
      <span className="text-xs text-gray-500">
        {formatDate(meeting.created_at)}
      </span>
      {meeting.error_msg && (
        <span className="mt-0.5 truncate text-xs text-red-400">
          {meeting.error_msg}
        </span>
      )}
    </button>
  )
}

// ---------------------------------------------------------------------------
// MeetingList
// ---------------------------------------------------------------------------

export default function MeetingList() {
  const meetings = useMeetingStore((s) => s.meetings)
  const selectedMeetingId = useMeetingStore((s) => s.selectedMeetingId)
  const selectMeeting = useMeetingStore((s) => s.selectMeeting)

  if (meetings.length === 0) {
    return (
      <div className="flex h-full items-center justify-center p-6">
        <p className="text-center text-sm text-gray-600">
          No past meetings yet. Start a new recording to get started.
        </p>
      </div>
    )
  }

  return (
    <div className="h-full overflow-y-auto">
      <div className="space-y-1 p-2">
        {meetings.map((meeting) => (
          <MeetingRow
            key={meeting.id}
            meeting={meeting}
            isSelected={meeting.id === selectedMeetingId}
            onSelect={() => selectMeeting(meeting.id)}
          />
        ))}
      </div>
    </div>
  )
}
