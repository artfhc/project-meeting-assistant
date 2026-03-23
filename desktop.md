You are helping me build a real desktop app codebase.

Project: Meeting Assistant
Target stack:
- Electron
- React
- TypeScript
- Vite
- Tailwind CSS
- Zustand
- Electron Builder
- Python FastAPI backend
- SQLite + local filesystem storage
- WebSocket for live job updates

Goal:
Replace my old PyQt UI with a modern Electron + React frontend while keeping Python for audio/transcription/summarization.

Important:
- Build this as a practical MVP
- Prefer working vertical slices
- Keep code secure and maintainable
- Avoid over-engineering

## Product requirements

The app should:
- record meetings/audio
- save audio locally
- transcribe locally with Whisper through Python
- summarize with OpenAI API through Python
- display transcript and summary
- persist meeting history
- allow browsing old meetings
- support settings:
  - OpenAI API key
  - Whisper model selection
  - microphone/input device
  - output folder
  - summary template
  - theme

## UI layout

- Left sidebar: New Meeting / History / Settings
- Top bar: recording controls, status, device
- Center: transcript
- Right: summary / action items / decisions / follow-ups
- Bottom: elapsed time, save path, job state

## Instructions for how to work

Do not try to dump the entire project all at once.

Work in phases.

### Phase 1
Propose:
- architecture
- communication model between Electron and Python
- persistence approach
- folder structure

### Phase 2
Generate the initial project scaffold and root configuration files.

### Phase 3
Generate the Electron main/preload and React app shell.

### Phase 4
Generate the Python backend skeleton with FastAPI, SQLite models, and WebSocket updates.

### Phase 5
Wire the frontend to backend for:
- create meeting
- start/stop recording state
- list meetings
- fetch meeting detail
- status updates

### Phase 6
Add transcription and summarization pipeline integration points.

### Phase 7
Polish UI and settings.

For each phase:
- explain decisions briefly
- then generate complete files for that phase
- ensure filenames are explicit
- ensure code is internally consistent

Assume I may paste your output directly into Claude Code to create/edit files.

Start with Phase 1 only.