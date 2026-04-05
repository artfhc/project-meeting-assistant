import { useEffect, useState } from 'react'
import { useMeetingStore } from '../../stores/meetingStore'
import { enqueueSummary } from '../../api/summaries'
import { listPromptKeys } from '../../api/settings'

// Statuses where a transcript is not yet available to summarize
const TRANSCRIPT_NOT_READY_STATUSES = new Set(['recording', 'recorded', 'transcribing'])

function EmptyState({ message }: { message: string }) {
  return (
    <div className="flex h-full items-center justify-center p-8">
      <div
        className="flex flex-col items-center gap-3 p-6"
        style={{ border: '1px dashed var(--color-border-muted)' }}
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

  const [promptKeys, setPromptKeys] = useState<string[]>([])
  const [selectedPromptKey, setSelectedPromptKey] = useState<string>('')
  const [isSummarizing, setIsSummarizing] = useState(false)

  // Fetch prompt keys whenever the selected meeting changes
  useEffect(() => {
    if (!meeting?.id) return
    listPromptKeys()
      .then((keys) => {
        setPromptKeys(keys)
        setSelectedPromptKey(keys[0] ?? '')
      })
      .catch((err) => {
        console.error('[SummaryPanel] Failed to load prompt keys:', err)
      })
  }, [meeting?.id])

  async function handleSummarize() {
    if (!meeting) return
    setIsSummarizing(true)
    try {
      await enqueueSummary(meeting.id, selectedPromptKey || null)
    } catch (err) {
      console.error('[SummaryPanel] Failed to enqueue summary:', err)
    } finally {
      setIsSummarizing(false)
    }
  }

  if (!meeting) {
    return <EmptyState message="Select a meeting to view its summary." />
  }

  if (TRANSCRIPT_NOT_READY_STATUSES.has(meeting.status)) {
    return <EmptyState message="Record and transcribe a meeting first." />
  }

  const isSummarizingStatus = meeting.status === 'summarizing'
  const canSummarize =
    meeting.status === 'transcribed' || meeting.status === 'done' || !!meeting.summary

  // Controls whether the button should be disabled
  const buttonDisabled =
    isSummarizing ||
    isSummarizingStatus ||
    TRANSCRIPT_NOT_READY_STATUSES.has(meeting.status)

  const summarizeBar = (
    <div
      className="flex shrink-0 items-center gap-2 border-b px-3 py-2"
      style={{
        backgroundColor: 'var(--color-bg-raised)',
        borderColor: 'var(--color-border-warm)',
      }}
    >
      <select
        value={selectedPromptKey}
        onChange={(e) => setSelectedPromptKey(e.target.value)}
        disabled={buttonDisabled}
        className="flex-1 text-xs focus:outline-none"
        style={{
          backgroundColor: 'var(--color-bg-muted)',
          border: '1px solid var(--color-border-muted)',
          color: promptKeys.length > 0 ? 'var(--color-text-muted)' : 'var(--color-text-faint)',
          padding: '3px 8px',
          minWidth: 0,
          // Amber focus ring via outline trick — handled by focus:outline-none + inline style swap on focus
        }}
      >
        {promptKeys.length === 0 ? (
          <option value="">Default prompt</option>
        ) : (
          promptKeys.map((key) => (
            <option key={key} value={key}>
              {key}
            </option>
          ))
        )}
      </select>

      <button
        onClick={() => void handleSummarize()}
        disabled={buttonDisabled}
        className="shrink-0 px-4 py-1.5 text-xs tracking-widest uppercase transition-all disabled:cursor-not-allowed disabled:opacity-40"
        style={
          isSummarizing || isSummarizingStatus
            ? {
                backgroundColor: 'var(--color-bg-muted)',
                color: 'var(--color-text-faint)',
                border: '1px solid var(--color-border-muted)',
              }
            : canSummarize
              ? {
                  backgroundColor: '#2a1f00',
                  color: 'var(--color-amber)',
                  border: '1px solid var(--color-amber)',
                }
              : {
                  backgroundColor: 'var(--color-bg-muted)',
                  color: 'var(--color-text-muted)',
                  border: '1px solid var(--color-border-muted)',
                }
        }
      >
        {isSummarizing || isSummarizingStatus ? 'Summarizing...' : 'Summarize'}
      </button>
    </div>
  )

  // Meeting is actively summarizing but has no summary yet
  if (isSummarizingStatus && !meeting.summary) {
    return (
      <div className="flex h-full flex-col">
        {summarizeBar}
        <EmptyState message="Summarizing... summary will appear here shortly." />
      </div>
    )
  }

  // Transcript ready but no summary yet — show the summarize bar with an invitation
  if (!meeting.summary) {
    return (
      <div className="flex h-full flex-col">
        {summarizeBar}
        <EmptyState message="Transcript is ready. Choose a prompt and click Summarize." />
      </div>
    )
  }

  // Summary available — show summarize bar + content
  return (
    <div className="flex h-full flex-col">
      {summarizeBar}
      <div className="min-h-0 flex-1 overflow-y-auto">
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
    </div>
  )
}
