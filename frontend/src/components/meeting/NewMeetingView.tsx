import TranscriptPanel from './TranscriptPanel'
import SummaryPanel from './SummaryPanel'

/**
 * The active recording view — shows live transcript and summary side-by-side.
 * Content is driven by recordingStore / meetingStore; this component only
 * handles the panel arrangement for the "New Meeting" route.
 */
export default function NewMeetingView() {
  return (
    <>
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
