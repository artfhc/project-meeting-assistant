Architecture Overview                                                               
                                                                                      
  Three cooperating processes, all local:                                             
                                                                                      
  Electron Main Process (Node.js)
    ├── spawns & manages Python backend                                               
    ├── IPC bridge to renderer (via preload contextBridge)                            
    └── native OS dialogs (folder picker, save dialog)                                
                                                                                      
  Electron Renderer (React + TypeScript)                                              
    ├── HTTP REST → Python (all business logic)                                       
    └── WebSocket → Python (live job progress)                                        
                                                                                    
  Python FastAPI Backend (port 7357)                                                  
    ├── wraps existing audio/, transcription/, summarization/ modules               
    └── owns SQLite DB                                                                
                                                                                      
  ---
  Communication Model                                                                 
                                                                                    
  Electron IPC — only for OS-native things:
                                                                                      
  ┌────────────────────┬─────────────────┬──────────────────────┐                     
  │      Channel       │    Direction    │         Use          │                     
  ├────────────────────┼─────────────────┼──────────────────────┤                     
  │ backend:ready      │ main → renderer │ Python is up         │                   
  ├────────────────────┼─────────────────┼──────────────────────┤
  │ dialog:open-folder │ renderer → main │ native folder picker │                     
  ├────────────────────┼─────────────────┼──────────────────────┤
  │ app:quit           │ renderer → main │ clean shutdown       │                     
  └────────────────────┴─────────────────┴──────────────────────┘                     
  
  HTTP REST — all business logic commands and CRUD:                                   
  - POST /recordings/start POST /recordings/stop                                    
  - POST /transcriptions POST /summaries                                              
  - GET/POST/PATCH/DELETE /meetings                                                 
  - GET/PUT /settings GET /devices/audio                                              
                                                                                      
  WebSocket /ws — server-push only for job progress:                                  
  { "type": "job_progress", "meeting_id": "...", "stage": "transcribing", "progress": 
  45, "message": "Chunk 3/7..." }                                                     
                                                                                      
  ---                                                                               
  Persistence                                                                         
                                                                                    
  SQLite (migrating from meetings.json), two tables:
                                                                                      
  meetings (id, title, created_at, duration_s, audio_path, transcript_path,           
            summary_path, transcript, summary, prompt_key, status, error_msg)         
                                                                                      
  settings (key, value)                                                               
  -- keys: openai_api_key, whisper_model, audio_device_index, output_dir, theme       
                                                                                      
  DB lives at ~/.meeting-assistant/meeting_assistant.db, owned exclusively by the     
  Python backend. Electron never touches it directly.                                 
                                                                                      
  ---                                                                               
  Folder Structure

  project-meeting-assistant/
  ├── audio/              ← KEEP AS-IS
  ├── transcription/      ← KEEP AS-IS                                                
  ├── summarization/      ← KEEP AS-IS
  ├── config/             ← KEEP AS-IS                                                
  ├── storage/            ← KEEP AS-IS                                                
  ├── app.py              ← KEEP AS-IS
  │                                                                                   
  ├── backend/            ← NEW: FastAPI wrapper                                    
  │   ├── main.py                                                                     
  │   ├── db.py           (aiosqlite)
  │   ├── models.py       (Pydantic schemas)                                          
  │   ├── jobs.py         (async job queue)                                         
  │   ├── ws_manager.py   (WebSocket manager)                                         
  │   └── routers/                                                                  
  │       ├── meetings.py                                                             
  │       ├── recordings.py                                                         
  │       ├── transcriptions.py                                                       
  │       ├── summaries.py
  │       ├── devices.py                                                              
  │       └── settings.py                                                           
  │
  └── frontend/           ← NEW: Electron + React
      ├── electron/                                                                   
      │   ├── main.ts         (spawn Python, lifecycle)
      │   ├── preload.ts      (contextBridge)                                         
      │   └── python-manager.ts                                                     
      └── src/                                                                        
          ├── api/            (typed fetch wrappers)                                
          ├── stores/         (Zustand: meetings, recording, jobs, settings)          
          ├── hooks/          (useWebSocket)                                          
          ├── components/     (layout, meeting, recording, settings)                  
          └── types/                                                                  
                                                                                    
  ---                                                                                 
  Key Decisions                                                                     
                                                                                      
  - Python spawned by Electron — one .app bundle, not two separate processes to launch
  - Direct imports, not subprocess — AudioRecorder, WhisperTranscriber, etc. imported 
  directly into FastAPI routers (no serialization overhead)                           
  - Whisper loaded once — singleton at FastAPI startup via lifespan hook, held in job 
  worker                                                                              
  - Thread pool for blocking ops — Whisper and OpenAI calls run via run_in_executor;
  progress_callback posts to an asyncio.Queue that feeds the WebSocket                
  - aiosqlite — async wrapper over stdlib sqlite3, no ORM needed for two tables     
  - Zustand over Redux — three small stores, no boilerplate                           
  - .env as fallback — settings SQLite is source of truth for runtime; .env retained
  for local dev                                                                       
                                                                                    
  ---                                                                                 
  Ready to move to Phase 2 (project scaffold + root config files) when you are.     
                                                                                      
✻ Cogitated for 5m 58s                                           
                                                                                      
❯ can I test it right now? would it work?                                             
  ⎿  ⧉ Selected 1 lines from desktop-plan.md in Visual Studio Code                    
                                                                                      
⏺ The architecture described in Phase 1 is a plan only — no code has been written yet.
   Nothing exists to test.                                                            
                                                                                      
  Here's what would need to be built before it could run:                             
                                                                                      
  - backend/ — FastAPI app, routers, DB, job queue, WebSocket manager (all new files) 
  - frontend/ — Electron main, preload, React app, Zustand stores, API client (all new
   files)                                                                             
  - Config wiring between the two                       
                                                                                      
  The existing Python modules (audio/, transcription/, summarization/) work           
  independently today (via app.py + PyQt), but the new Electron frontend has no way to
   talk to them yet.                                 