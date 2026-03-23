import MeetingList from './MeetingList'
import TranscriptPanel from './TranscriptPanel'
import SummaryPanel from './SummaryPanel'

/**
 * History view — three-column layout showing past meetings list,
 * selected transcript, and selected summary.
 */
export default function HistoryView() {
  return (
    <>
      {/* Left list */}
      <section className="flex w-64 shrink-0 flex-col border-r border-gray-800">
        <div className="shrink-0 border-b border-gray-800 px-4 py-2">
          <h2 className="text-xs font-semibold uppercase tracking-wider text-gray-500">
            Past Meetings
          </h2>
        </div>
        <div className="flex-1 overflow-hidden">
          <MeetingList />
        </div>
      </section>

      {/* Center: Transcript */}
      <section className="flex min-w-0 flex-1 flex-col border-r border-gray-800">
        <div className="shrink-0 border-b border-gray-800 px-4 py-2">
          <h2 className="text-xs font-semibold uppercase tracking-wider text-gray-500">
            Transcript
          </h2>
        </div>
        <div className="flex-1 overflow-hidden">
          <TranscriptPanel />
        </div>
      </section>

      {/* Right: Summary */}
      <section
        className="flex flex-col border-l border-gray-800"
        style={{ width: 'var(--panel-width)' }}
      >
        <div className="shrink-0 border-b border-gray-800 px-4 py-2">
          <h2 className="text-xs font-semibold uppercase tracking-wider text-gray-500">
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
