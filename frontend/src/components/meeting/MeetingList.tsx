import { useRef, useState } from 'react'
import { useMeetingStore } from '../../stores/meetingStore'
import { deleteMeeting, getMeeting, updateMeeting } from '../../api/meetings'
import type { Meeting, MeetingStatus } from '../../types'

// ---------------------------------------------------------------------------
// Status dot — colored dot + label, no pill chrome
// ---------------------------------------------------------------------------

const STATUS_DOT: Record<MeetingStatus, string> = {
  created:      '#52525b',
  recording:    '#60a5fa',
  recorded:     '#52525b',
  transcribing: '#f59e0b',
  transcribed:  '#f59e0b',
  summarizing:  '#f59e0b',
  done:         '#4ade80',
  error:        '#f87171',
}

const STATUS_LABELS: Record<MeetingStatus, string> = {
  created:      'created',
  recording:    'recording',
  recorded:     'recorded',
  transcribing: 'transcribing',
  transcribed:  'transcribed',
  summarizing:  'summarizing',
  done:         'done',
  error:        'error',
}

function StatusDot({ status }: { status: MeetingStatus }) {
  return (
    <span className="flex items-center gap-1 shrink-0">
      <span
        className="h-1.5 w-1.5 rounded-full shrink-0"
        style={{ backgroundColor: STATUS_DOT[status] }}
        aria-hidden="true"
      />
      <span
        className="text-xs"
        style={{ color: STATUS_DOT[status] }}
      >
        {STATUS_LABELS[status]}
      </span>
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
      className="group flex w-full items-start gap-1 text-left transition-colors"
      style={
        isSelected
          ? {
              borderLeft: '2px solid var(--color-amber)',
              backgroundColor: 'var(--color-bg-overlay)',
              paddingLeft: '10px',
              paddingRight: '12px',
              paddingTop: '8px',
              paddingBottom: '8px',
            }
          : {
              borderLeft: '2px solid transparent',
              paddingLeft: '10px',
              paddingRight: '12px',
              paddingTop: '8px',
              paddingBottom: '8px',
            }
      }
    >
      {/* Clickable content area */}
      <button onClick={onSelect} className="min-w-0 flex-1 text-left">
        <div className="flex items-start justify-between gap-2">
          {isEditing ? (
            <input
              ref={inputRef}
              value={editValue}
              onChange={(e) => setEditValue(e.target.value)}
              onBlur={() => void commitEdit()}
              onKeyDown={handleKeyDown}
              onClick={(e) => e.stopPropagation()}
              className="w-full bg-transparent px-0 py-0 text-xs focus:outline-none"
              style={{
                color: '#e4e4e7',
                borderBottom: '1px solid var(--color-amber)',
              }}
              autoFocus
            />
          ) : (
            <span
              className="truncate text-xs leading-tight"
              style={{ color: isSelected ? '#e4e4e7' : 'var(--color-text-base)' }}
              onDoubleClick={handleTitleDoubleClick}
              title="Double-click to rename"
            >
              {meeting.title}
            </span>
          )}
        </div>
        <div className="mt-1 flex items-center justify-between gap-2">
          <span
            className="text-xs tabular-nums"
            style={{ color: 'var(--color-text-faint)' }}
          >
            {formatDate(meeting.created_at)}
          </span>
          <StatusDot status={meeting.status} />
        </div>
        {meeting.error_msg && (
          <span className="mt-0.5 block truncate text-xs" style={{ color: '#f87171' }}>
            {meeting.error_msg}
          </span>
        )}
      </button>

      {/* Delete button — appears on row hover */}
      <button
        onClick={(e) => {
          e.stopPropagation()
          onDelete()
        }}
        aria-label={`Delete "${meeting.title}"`}
        className="mt-0.5 shrink-0 p-0.5 opacity-0 transition-all group-hover:opacity-100 focus:opacity-100"
        style={{ color: 'var(--color-text-faint)' }}
        onMouseEnter={(e) => { (e.currentTarget as HTMLButtonElement).style.color = 'var(--color-amber)' }}
        onMouseLeave={(e) => { (e.currentTarget as HTMLButtonElement).style.color = 'var(--color-text-faint)' }}
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 16 16"
          fill="currentColor"
          className="h-3 w-3"
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
        <p
          className="text-center text-xs"
          style={{ color: 'var(--color-text-faint)' }}
        >
          No past meetings yet.
        </p>
      </div>
    )
  }

  return (
    <div className="h-full overflow-y-auto">
      <div className="py-1">
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
