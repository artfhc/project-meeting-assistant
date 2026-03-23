import { useRef, useState } from 'react'
import { useMeetingStore } from '../../stores/meetingStore'
import { deleteMeeting, getMeeting, updateMeeting } from '../../api/meetings'
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
  onDelete,
  onTitleSave,
}: {
  meeting: Meeting
  isSelected: boolean
  onSelect: () => void
  onDelete: () => void
  onTitleSave: (newTitle: string) => Promise<void>
}) {
  const [isEditing, setIsEditing] = useState(false)
  const [editValue, setEditValue] = useState(meeting.title)
  const inputRef = useRef<HTMLInputElement>(null)

  function handleTitleDoubleClick(e: React.MouseEvent) {
    e.stopPropagation()
    setEditValue(meeting.title)
    setIsEditing(true)
    // Focus the input on the next frame after it mounts
    setTimeout(() => inputRef.current?.select(), 0)
  }

  async function commitEdit() {
    const trimmed = editValue.trim()
    if (trimmed && trimmed !== meeting.title) {
      await onTitleSave(trimmed)
    }
    setIsEditing(false)
  }

  function handleKeyDown(e: React.KeyboardEvent<HTMLInputElement>) {
    if (e.key === 'Enter') {
      void commitEdit()
    } else if (e.key === 'Escape') {
      setIsEditing(false)
    }
  }

  return (
    <div
      className={[
        'group flex w-full items-start gap-1 rounded-md px-3 py-2.5 text-left transition-colors',
        isSelected
          ? 'bg-gray-800 text-white'
          : 'text-gray-300 hover:bg-gray-800/60',
      ].join(' ')}
    >
      {/* Clickable content area */}
      <button
        onClick={onSelect}
        className="min-w-0 flex-1 text-left"
      >
        <div className="flex items-start justify-between gap-2">
          {isEditing ? (
            <input
              ref={inputRef}
              value={editValue}
              onChange={(e) => setEditValue(e.target.value)}
              onBlur={() => void commitEdit()}
              onKeyDown={handleKeyDown}
              onClick={(e) => e.stopPropagation()}
              className="w-full rounded border border-brand-500 bg-gray-900 px-1 py-0 text-sm font-medium text-white focus:outline-none focus:ring-1 focus:ring-brand-500"
              autoFocus
            />
          ) : (
            <span
              className="truncate text-sm font-medium leading-tight"
              onDoubleClick={handleTitleDoubleClick}
              title="Double-click to rename"
            >
              {meeting.title}
            </span>
          )}
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

      {/* Delete button — visible on row hover */}
      <button
        onClick={(e) => {
          e.stopPropagation()
          onDelete()
        }}
        aria-label={`Delete "${meeting.title}"`}
        className="mt-0.5 shrink-0 rounded p-0.5 text-gray-600 opacity-0 transition-opacity hover:text-red-400 group-hover:opacity-100 focus:opacity-100"
      >
        {/* Simple × glyph — no icon library dependency */}
        <svg
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 16 16"
          fill="currentColor"
          className="h-3.5 w-3.5"
          aria-hidden="true"
        >
          <path d="M6.5 1h3a.5.5 0 0 1 .5.5v1H6v-1a.5.5 0 0 1 .5-.5ZM11 2.5v-1A1.5 1.5 0 0 0 9.5 0h-3A1.5 1.5 0 0 0 5 1.5v1H2.506a.58.58 0 0 0-.01 0H1.5a.5.5 0 0 0 0 1h.538l.853 10.66A2 2 0 0 0 4.885 16h6.23a2 2 0 0 0 1.994-1.84l.853-10.66H14.5a.5.5 0 0 0 0-1h-.996a.59.59 0 0 0-.01 0H11Zm1.958 1-.846 10.58a1 1 0 0 1-.997.92h-6.23a1 1 0 0 1-.997-.92L3.042 3.5h9.916Z" />
        </svg>
      </button>
    </div>
  )
}

// ---------------------------------------------------------------------------
// MeetingList
// ---------------------------------------------------------------------------

export default function MeetingList() {
  const meetings = useMeetingStore((s) => s.meetings)
  const selectedMeetingId = useMeetingStore((s) => s.selectedMeetingId)
  const selectMeeting = useMeetingStore((s) => s.selectMeeting)
  const removeMeeting = useMeetingStore((s) => s.removeMeeting)
  const upsertMeeting = useMeetingStore((s) => s.upsertMeeting)

  async function handleDelete(id: string) {
    try {
      await deleteMeeting(id)
      removeMeeting(id)
    } catch (err) {
      console.error('[MeetingList] Failed to delete meeting:', err)
    }
  }

  async function handleTitleSave(id: string, newTitle: string) {
    try {
      const updated = await updateMeeting(id, { title: newTitle })
      upsertMeeting(updated)
    } catch (err) {
      console.error('[MeetingList] Failed to update meeting title:', err)
      // Re-fetch to ensure local state stays consistent with backend
      try {
        const refreshed = await getMeeting(id)
        upsertMeeting(refreshed)
      } catch {
        // ignore secondary failure
      }
    }
  }

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
            onDelete={() => void handleDelete(meeting.id)}
            onTitleSave={(newTitle) => handleTitleSave(meeting.id, newTitle)}
          />
        ))}
      </div>
    </div>
  )
}
