import MeetingList from './MeetingList'
import TranscriptPanel from './TranscriptPanel'
import SummaryPanel from './SummaryPanel'

/**
 * History view — three-column layout: past meetings list, transcript, summary.
 */
export default function HistoryView() {
  return (
    <>
      {/* Left: meeting list */}
      <section
        className="flex w-56 shrink-0 flex-col border-r"
        style={{ borderColor: 'var(--color-border-warm)', backgroundColor: 'var(--color-bg-raised)' }}
      >
        <div
          className="shrink-0 border-b px-4 py-2"
          style={{ borderColor: 'var(--color-border-subtle)' }}
        >
          <h2
            className="text-xs tracking-widest uppercase"
            style={{ color: 'var(--color-text-faint)' }}
          >
            Past Meetings
          </h2>
        </div>
        <div className="flex-1 overflow-hidden">
          <MeetingList />
        </div>
      </section>

      {/* Center: Transcript */}
      <section
        className="flex min-w-0 flex-1 flex-col border-r"
        style={{ borderColor: 'var(--color-border-warm)' }}
      >
        <div
          className="shrink-0 border-b px-4 py-2"
          style={{ borderColor: 'var(--color-border-subtle)' }}
        >
          <h2
            className="text-xs tracking-widest uppercase"
            style={{ color: 'var(--color-text-faint)' }}
          >
            Transcript
          </h2>
        </div>
        <div className="flex-1 overflow-hidden">
          <TranscriptPanel />
        </div>
      </section>

      {/* Right: Summary */}
      <section
        className="flex flex-col"
        style={{
          width: 'var(--panel-width)',
          borderLeft: '1px solid var(--color-border-warm)',
          backgroundColor: 'var(--color-bg-raised)',
        }}
      >
        <div
          className="shrink-0 border-b px-4 py-2"
          style={{ borderColor: 'var(--color-border-subtle)' }}
        >
          <h2
            className="text-xs tracking-widest uppercase"
            style={{ color: 'var(--color-text-faint)' }}
          >
            Summary
          </h2>
        </div>
        <div className="flex-1 overflow-hidden">
          <SummaryPanel />
        </div>
      </section>
    </>
  )
}
