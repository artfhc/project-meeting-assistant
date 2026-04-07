/**
 * Electron preload script for Meeting Assistant.
 *
 * This script executes in the renderer process context BEFORE any renderer
 * code runs, but it has access to Node.js APIs (specifically ipcRenderer).
 * It is the ONLY sanctioned bridge between the sandboxed renderer and the
 * Electron main process.
 *
 * Security model:
 *  - contextIsolation: true  — renderer JS cannot reach this scope directly.
 *  - sandbox: true           — extra OS-level process isolation.
 *  - We expose the minimum surface needed; ipcRenderer itself is never leaked.
 *
 * All channel names here must exactly match the ipcMain.handle() registrations
 * in electron/main.ts, and the TypeScript types in the `declare global` block
 * below must match what the renderer actually receives.
 */

import { contextBridge, ipcRenderer } from 'electron'

// ---------------------------------------------------------------------------
// API surface
// ---------------------------------------------------------------------------

const electronAPI = {
  openFolder(): Promise<string | null> {
    return ipcRenderer.invoke('dialog:open-folder')
  },

  saveFile(options?: {
    defaultPath?: string
    filters?: Electron.FileFilter[]
  }): Promise<string | null> {
    return ipcRenderer.invoke('dialog:save-file', options)
  },

  getVersion(): Promise<string> {
    return ipcRenderer.invoke('app:get-version')
  },
} as const

contextBridge.exposeInMainWorld('electronAPI', electronAPI)

// ---------------------------------------------------------------------------
// TypeScript ambient declarations
// ---------------------------------------------------------------------------
// These types are compiled away at runtime but give the renderer (and any
// shared code imported by it) full type safety for window.electronAPI without
// coupling the renderer bundle to Electron internals.

declare global {
  interface Window {
    electronAPI: {
      openFolder(): Promise<string | null>
      saveFile(options?: {
        defaultPath?: string
        filters?: Electron.FileFilter[]
      }): Promise<string | null>
      getVersion(): Promise<string>
    }
  }
}
