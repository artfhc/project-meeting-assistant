/**
 * Electron main process for Meeting Assistant.
 *
 * Responsibilities:
 *  1. Spawn the Python FastAPI backend as a managed child process.
 *  2. Poll the backend /health endpoint and notify the renderer when it's ready.
 *  3. Create and manage the BrowserWindow.
 *  4. Register IPC handlers for native OS capabilities (dialogs, app version).
 *  5. Gracefully terminate the Python process on quit (SIGTERM → SIGKILL).
 */

import {
  app,
  BrowserWindow,
  dialog,
  ipcMain,
  type IpcMainInvokeEvent,
} from 'electron'
import { spawn, type ChildProcess } from 'child_process'
import * as http from 'http'
import * as path from 'path'

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const BACKEND_HOST = '127.0.0.1'
const BACKEND_PORT = 7357
const HEALTH_POLL_INTERVAL_MS = 500
const HEALTH_POLL_TIMEOUT_MS = 30_000
const GRACEFUL_SHUTDOWN_TIMEOUT_MS = 3_000

const isDev = Boolean(process.env.VITE_DEV_SERVER_URL)

// ---------------------------------------------------------------------------
// Module-level state
// ---------------------------------------------------------------------------

let mainWindow: BrowserWindow | null = null
let pythonProcess: ChildProcess | null = null

// Tracks whether we are already in the middle of a managed quit so we don't
// re-enter the before-quit handler.
let isQuitting = false

// ---------------------------------------------------------------------------
// Python backend management
// ---------------------------------------------------------------------------

function spawnPythonBackend(): void {
  const uvicornArgs = [
    '-m',
    'uvicorn',
    'backend.main:app',
    '--host',
    BACKEND_HOST,
    '--port',
    String(BACKEND_PORT),
  ]

  // Working directory differs between dev and packaged production builds.
  // In dev the repo root sits one level above the Vite app root (getAppPath()).
  // In production electron-builder places backend resources under resourcesPath.
  const cwd = isDev
    ? path.join(app.getAppPath(), '..')
    : path.join(process.resourcesPath, 'backend')

  console.log(`[main] Spawning Python backend (cwd: ${cwd})`)

  pythonProcess = spawn('python3', uvicornArgs, {
    cwd,
    // Inherit stdout/stderr so uvicorn logs appear in Electron's terminal
    // during development; in production they are silently discarded.
    stdio: isDev ? 'inherit' : 'ignore',
    // Detach is intentionally false — we want the process tied to this parent.
  })

  pythonProcess.on('error', (err) => {
    // Covers "python3 not found" (ENOENT) and similar spawn failures.
    console.error('[main] Failed to spawn Python process:', err.message)
    sendToRenderer('backend:error', `Failed to start backend: ${err.message}`)
  })

  pythonProcess.on('exit', (code, signal) => {
    // A non-zero exit before we sent backend:ready means something went wrong.
    // After a clean quit (isQuitting) this is expected and we ignore it.
    if (!isQuitting && code !== 0 && code !== null) {
      const reason = signal
        ? `killed by signal ${signal}`
        : `exited with code ${code}`
      console.error(`[main] Python process terminated unexpectedly (${reason})`)
      sendToRenderer('backend:error', `Backend process stopped unexpectedly (${reason})`)
    }
    pythonProcess = null
  })

  // Begin polling immediately after spawn. The process may not have bound the
  // port yet, which is exactly why we poll rather than trusting the spawn event.
  pollBackendHealth()
}

/**
 * Polls GET http://{BACKEND_HOST}:{BACKEND_PORT}/health every 500 ms.
 * Sends `backend:ready` on the first HTTP 200 response.
 * Sends `backend:error` if the deadline is exceeded.
 */
function pollBackendHealth(): void {
  const deadline = Date.now() + HEALTH_POLL_TIMEOUT_MS
  let intervalId: ReturnType<typeof setInterval> | null = null

  const check = (): void => {
    // Abort polling if Python crashed before the deadline.
    if (pythonProcess === null && !isQuitting) {
      clearInterval(intervalId!)
      // The exit handler already sent backend:error; nothing more to do here.
      return
    }

    if (Date.now() > deadline) {
      clearInterval(intervalId!)
      const msg = `Backend did not become ready within ${HEALTH_POLL_TIMEOUT_MS / 1000}s`
      console.error(`[main] ${msg}`)
      sendToRenderer('backend:error', msg)
      return
    }

    const req = http.get(
      {
        hostname: BACKEND_HOST,
        port: BACKEND_PORT,
        path: '/health',
        // Keep the individual probe short so we don't accumulate pending requests.
        timeout: HEALTH_POLL_INTERVAL_MS - 50,
      },
      (res) => {
        if (res.statusCode === 200) {
          clearInterval(intervalId!)
          console.log('[main] Backend is ready')
          sendToRenderer('backend:ready')
        }
        // Drain the response body to free the socket, even on non-200.
        res.resume()
      },
    )

    req.on('error', () => {
      // Connection refused / ECONNREFUSED is normal while uvicorn is starting —
      // silently swallow and let the next interval retry.
    })

    req.on('timeout', () => {
      req.destroy()
    })
  }

  // Run the first check immediately, then on every interval thereafter.
  check()
  intervalId = setInterval(check, HEALTH_POLL_INTERVAL_MS)
}

/**
 * Sends SIGTERM to the Python process and waits up to GRACEFUL_SHUTDOWN_TIMEOUT_MS
 * for it to exit cleanly before escalating to SIGKILL.
 * Resolves when the process is confirmed dead (or was never alive).
 */
function shutdownPythonBackend(): Promise<void> {
  return new Promise((resolve) => {
    if (!pythonProcess || pythonProcess.exitCode !== null) {
      resolve()
      return
    }

    const proc = pythonProcess

    const forceKillTimer = setTimeout(() => {
      console.warn('[main] Python process did not exit within grace period; sending SIGKILL')
      try {
        proc.kill('SIGKILL')
      } catch {
        // Process may have already exited between the timeout firing and kill().
      }
    }, GRACEFUL_SHUTDOWN_TIMEOUT_MS)

    proc.once('exit', () => {
      clearTimeout(forceKillTimer)
      resolve()
    })

    try {
      proc.kill('SIGTERM')
    } catch (err) {
      // kill() can throw if the pid is already invalid.
      clearTimeout(forceKillTimer)
      resolve()
    }
  })
}

// ---------------------------------------------------------------------------
// BrowserWindow
// ---------------------------------------------------------------------------

function createWindow(): void {
  mainWindow = new BrowserWindow({
    width: 1280,
    height: 800,
    minWidth: 900,
    minHeight: 600,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: true,
    },
  })

  if (isDev) {
    mainWindow.loadURL(process.env.VITE_DEV_SERVER_URL as string)
    mainWindow.webContents.openDevTools()
  } else {
    mainWindow.loadFile(path.join(__dirname, '../renderer/index.html'))
  }

  mainWindow.on('closed', () => {
    mainWindow = null
  })
}

// ---------------------------------------------------------------------------
// IPC helpers
// ---------------------------------------------------------------------------

/**
 * Posts a message to the renderer. Guards against the window not yet existing
 * (e.g., backend:error fires before the window finishes loading).
 */
function sendToRenderer(channel: 'backend:ready' | 'backend:error', ...args: unknown[]): void {
  if (mainWindow && !mainWindow.isDestroyed()) {
    mainWindow.webContents.send(channel, ...args)
  } else {
    // Buffer delivery by waiting for the renderer to finish loading.
    // This handles the race between backend health poll and window load.
    const send = (): void => {
      mainWindow?.webContents.send(channel, ...args)
    }

    if (mainWindow && !mainWindow.isDestroyed()) {
      mainWindow.webContents.once('did-finish-load', send)
    }
    // If mainWindow is null at this point the app is shutting down; drop msg.
  }
}

// ---------------------------------------------------------------------------
// IPC handlers
// ---------------------------------------------------------------------------

function registerIpcHandlers(): void {
  ipcMain.handle(
    'dialog:open-folder',
    async (_event: IpcMainInvokeEvent): Promise<string | null> => {
      const result = await dialog.showOpenDialog({
        properties: ['openDirectory'],
      })
      return result.canceled ? null : (result.filePaths[0] ?? null)
    },
  )

  ipcMain.handle(
    'dialog:save-file',
    async (
      _event: IpcMainInvokeEvent,
      options?: Electron.SaveDialogOptions,
    ): Promise<string | null> => {
      const result = await dialog.showSaveDialog(options ?? {})
      return result.canceled ? null : (result.filePath ?? null)
    },
  )

  ipcMain.handle('app:get-version', (): string => {
    return app.getVersion()
  })
}

// ---------------------------------------------------------------------------
// App lifecycle
// ---------------------------------------------------------------------------

app.whenReady().then(() => {
  registerIpcHandlers()
  createWindow()
  spawnPythonBackend()
})

app.on('window-all-closed', () => {
  // On macOS it is conventional to keep the app alive until Cmd+Q.
  if (process.platform !== 'darwin') {
    app.quit()
  }
})

app.on('activate', () => {
  // macOS: recreate the window when the dock icon is clicked and no windows open.
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow()
  }
})

/**
 * Graceful shutdown sequence:
 *  1. Prevent the default quit so we control the timing.
 *  2. Send SIGTERM to Python and wait (up to 3s).
 *  3. Re-trigger app.quit() which will skip this handler the second time.
 */
app.once('before-quit', (event) => {
  if (isQuitting) return
  isQuitting = true
  event.preventDefault()

  shutdownPythonBackend()
    .catch((err) => {
      console.error('[main] Error during Python shutdown:', err)
    })
    .finally(() => {
      app.quit()
    })
})
