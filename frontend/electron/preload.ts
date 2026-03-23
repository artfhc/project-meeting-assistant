// Phase 3: Implement the preload script.
//
// The preload runs in the renderer context WITH access to Node APIs, before
// any renderer code executes. It is the ONLY safe bridge between the
// sandboxed renderer and the Electron main process.
//
// Expose a typed API surface via contextBridge.exposeInMainWorld so the
// renderer can invoke IPC without ever touching the raw ipcRenderer module.
//
// Planned surface (to be implemented in Phase 3):
//
//   window.electronAPI = {
//     // Native dialogs
//     openFile: () => Promise<string | null>
//     selectDirectory: () => Promise<string | null>
//
//     // App metadata
//     getVersion: () => Promise<string>
//     getPlatform: () => Promise<NodeJS.Platform>
//   }

import { contextBridge } from 'electron'

// Stub — exposes nothing until Phase 3 fills this in.
contextBridge.exposeInMainWorld('electronAPI', {})
