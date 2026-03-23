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

import { contextBridge, ipcRenderer, type IpcRendererEvent } from 'electron'

// ---------------------------------------------------------------------------
// API surface
// ---------------------------------------------------------------------------

const electronAPI = {
  /**
   * Opens a native folder-picker dialog.
   * @returns The selected directory path, or null if the user cancelled.
   */
  openFolder(): Promise<string | null> {
    return ipcRenderer.invoke('dialog:open-folder')
  },

  /**
   * Opens a native save-file dialog.
   * @param options  Optional defaultPath and file-type filters.
   * @returns The chosen save path, or null if the user cancelled.
   */
  saveFile(options?: {
    defaultPath?: string
    filters?: Electron.FileFilter[]
  }): Promise<string | null> {
    return ipcRenderer.invoke('dialog:save-file', options)
  },

  /**
   * Returns the application version string from package.json.
   */
  getVersion(): Promise<string> {
    return ipcRenderer.invoke('app:get-version')
  },

  /**
   * Subscribes to the `backend:ready` event emitted by the main process once
   * the Python FastAPI server has passed its health check.
   *
   * @param cb  Callback invoked with no arguments when the backend is ready.
   * @returns   An unsubscribe function — call it to stop listening.
   */
  onBackendReady(cb: () => void): () => void {
    const listener = (_event: IpcRendererEvent): void => cb()
    ipcRenderer.on('backend:ready', listener)
    return () => ipcRenderer.removeListener('backend:ready', listener)
  },

  /**
   * Subscribes to the `backend:error` event emitted by the main process when
   * the Python backend fails to start or exits unexpectedly.
   *
   * @param cb  Callback invoked with a human-readable error message.
   * @returns   An unsubscribe function — call it to stop listening.
   */
  onBackendError(cb: (msg: string) => void): () => void {
    const listener = (_event: IpcRendererEvent, msg: string): void => cb(msg)
    ipcRenderer.on('backend:error', listener)
    return () => ipcRenderer.removeListener('backend:error', listener)
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
      onBackendReady(cb: () => void): () => void
      onBackendError(cb: (msg: string) => void): () => void
    }
  }
}
