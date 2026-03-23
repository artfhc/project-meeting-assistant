// Phase 3: Implement Electron main process.
//
// Responsibilities (to be implemented):
//   - Spawn the Python FastAPI backend as a child process from process.resourcesPath
//   - Create and manage the BrowserWindow (load dist/renderer/index.html in prod,
//     or http://localhost:5173 in dev)
//   - Handle app lifecycle events (ready, window-all-closed, activate)
//   - Register IPC handlers for native OS capabilities:
//       ipcMain.handle('dialog:openFile', ...)
//       ipcMain.handle('dialog:selectDirectory', ...)
//   - Gracefully shut down the Python backend on app quit

import { app, BrowserWindow } from 'electron'

let mainWindow: BrowserWindow | null = null

function createWindow(): void {
  mainWindow = new BrowserWindow({
    width: 1280,
    height: 800,
    webPreferences: {
      preload: `${__dirname}/preload.js`,
      contextIsolation: true,
      nodeIntegration: false,
    },
  })

  // In dev, load the Vite dev server; in production, load the built bundle.
  if (process.env.VITE_DEV_SERVER_URL) {
    mainWindow.loadURL(process.env.VITE_DEV_SERVER_URL)
  } else {
    mainWindow.loadFile(`${__dirname}/../renderer/index.html`)
  }
}

app.whenReady().then(createWindow)

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit()
})

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) createWindow()
})
