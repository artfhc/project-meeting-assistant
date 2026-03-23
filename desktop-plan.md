  Meeting Assistant — a desktop app for recording, transcribing, and summarizing
  meetings.

  ┌───────────────┬─────────────────────────────────────┐
  │     Layer     │             Technology              │
  ├───────────────┼─────────────────────────────────────┤
  │ Language      │ Python 3.7+                         │
  ├───────────────┼─────────────────────────────────────┤
  │ GUI           │ PyQt5                               │
  ├───────────────┼─────────────────────────────────────┤
  │ Transcription │ OpenAI Whisper (local/offline)      │
  ├───────────────┼─────────────────────────────────────┤
  │ Summarization │ OpenAI API (GPT models)             │
  ├───────────────┼─────────────────────────────────────┤
  │ Audio         │ PyAudio, FFmpeg, librosa, soundfile │
  ├───────────────┼─────────────────────────────────────┤
  │ ML runtime    │ PyTorch                             │
  ├───────────────┼─────────────────────────────────────┤
  │ Config        │ python-dotenv, PyYAML               │
  └───────────────┴─────────────────────────────────────┘

  Architecture: local Whisper for transcription (no API needed) + cloud GPT for
  summarization. Supports multiple Whisper model sizes and OpenAI models
  (gpt-3.5-turbo, gpt-4).

  Project structure: audio/, ui/, transcription/, summarization/, storage/, config/,
  with app.py as the entry point.

✻ Cogitated for 1m 20s

❯ /agents                                                                             
  ⎿  Agents dialog dismissed

❯ can you check @desktop.md? and see what skills or agents I need?                    
  ⎿  Read desktop.md (95 lines)                                    
                                                                                      
⏺ I can see desktop.md — it's a plan to rebuild the PyQt UI into a modern Electron + 
  React + TypeScript frontend while keeping Python for                                
  audio/transcription/summarization.                                                  
                                                                                      
  For this project, here's what maps well to available agents/skills:                 
                                                                                      
  Agents:                                                                             
  - ui-engineer — React components, Tailwind styling, Zustand state, the Electron
  renderer layer                                                                      
  - backend-typescript-architect — Electron main process, preload scripts, IPC,
  Vite/build config                                                                   
  - python-backend-engineer — FastAPI backend, SQLite models, WebSocket updates,      
  keeping existing Whisper/OpenAI pipeline
                                                                                      
  Skills:         
  - /simplify — after each phase to review generated code for quality                 
  - /frontend-design (example-skills:frontend-design) — for polishing the UI (Phase   
  7), the sidebar/topbar/center/right panel layout
                                                                                      
  Phase breakdown by agent:
                                                                                      
  ┌─────────────────────────────────────┬─────────────────────────────────────────┐   
  │                Phase                │               Agent/Skill               │
  ├─────────────────────────────────────┼─────────────────────────────────────────┤   
  │ 1 — Architecture                    │ Plan agent (already in desktop.md)      │
  ├─────────────────────────────────────┼─────────────────────────────────────────┤
  │ 2 — Scaffold & config               │ backend-typescript-architect            │   
  ├─────────────────────────────────────┼─────────────────────────────────────────┤   
  │ 3 — Electron main/preload + React   │ ui-engineer +                           │   
  │ shell                               │ backend-typescript-architect            │   
  ├─────────────────────────────────────┼─────────────────────────────────────────┤
  │ 4 — FastAPI + SQLite + WebSocket    │ python-backend-engineer                 │   
  ├─────────────────────────────────────┼─────────────────────────────────────────┤   
  │ 5 — Frontend↔backend wiring         │ Both                                    │
  ├─────────────────────────────────────┼─────────────────────────────────────────┤   
  │ 6 — Transcription/summarization     │ python-backend-engineer                 │
  │ pipeline                            │                                         │   
  ├─────────────────────────────────────┼─────────────────────────────────────────┤
  │ 7 — UI polish + settings            │ ui-engineer +                           │   
  │                                     │ example-skills:frontend-design          │   
  └─────────────────────────────────────┴─────────────────────────────────────────┘
                                                                             
