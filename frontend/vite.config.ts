import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import electron from 'vite-plugin-electron'
import renderer from 'vite-plugin-electron-renderer'
import { resolve } from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    react(),

    electron([
      {
        // Electron main process entry
        entry: 'electron/main.ts',
        vite: {
          build: {
            outDir: 'dist/electron',
            // sourcemap in dev, no sourcemap in prod to keep package size down
            sourcemap: process.env.NODE_ENV === 'development' ? 'inline' : false,
          },
        },
      },
      {
        // Preload script — runs in renderer context with Node integration
        entry: 'electron/preload.ts',
        onstart(options) {
          // Notify the renderer process to reload when preload script changes
          options.reload()
        },
        vite: {
          build: {
            outDir: 'dist/electron',
            sourcemap: process.env.NODE_ENV === 'development' ? 'inline' : false,
          },
        },
      },
    ]),

    // Allow renderer to use Node built-ins via polyfills (e.g. path, fs stubs)
    renderer(),
  ],

  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
    },
  },

  build: {
    // Renderer output — Electron Builder picks this up from files[] config
    outDir: 'dist/renderer',
    emptyOutDir: true,
  },

  server: {
    port: 5173,
    strictPort: true,
  },
})
