import type { Configuration } from 'electron-builder'

const config: Configuration = {
  appId: 'com.meetingassistant.app',
  productName: 'Meeting Assistant',

  // Electron entry point (compiled from electron/main.ts)
  main: 'dist/electron/main.js',

  directories: {
    output: 'dist/packaged',
    buildResources: 'build-resources',
  },

  files: [
    // Compiled renderer bundle
    'dist/renderer/**',
    // Compiled Electron main + preload
    'dist/electron/**',
    // HTML entry
    'index.html',
    'package.json',
  ],

  // Bundle the Python backend into the app's extraResources so the Electron
  // main process can locate and spawn it at runtime via process.resourcesPath.
  extraResources: [
    {
      // Source path relative to this config file (repo root modules)
      from: '../audio',
      to: 'backend/audio',
      filter: ['**/*', '!**/__pycache__/**', '!**/*.pyc'],
    },
    {
      from: '../transcription',
      to: 'backend/transcription',
      filter: ['**/*', '!**/__pycache__/**', '!**/*.pyc'],
    },
    {
      from: '../summarization',
      to: 'backend/summarization',
      filter: ['**/*', '!**/__pycache__/**', '!**/*.pyc'],
    },
    {
      from: '../config',
      to: 'backend/config',
      filter: ['**/*', '!**/__pycache__/**', '!**/*.pyc'],
    },
    {
      from: '../storage',
      to: 'backend/storage',
      filter: ['**/*', '!**/__pycache__/**', '!**/*.pyc'],
    },
    {
      // FastAPI app entry (Phase 4)
      from: '../app.py',
      to: 'backend/app.py',
    },
    {
      from: '../requirements.txt',
      to: 'backend/requirements.txt',
    },
  ],

  // macOS — primary target
  mac: {
    target: [{ target: 'dmg', arch: ['arm64', 'x64'] }],
    category: 'public.app-category.productivity',
    // Code signing — set CSC_LINK / CSC_KEY_PASSWORD env vars in CI
    identity: undefined,
    hardenedRuntime: true,
    gatekeeperAssess: false,
    entitlements: 'build-resources/entitlements.mac.plist',
    entitlementsInherit: 'build-resources/entitlements.mac.plist',
  },

  dmg: {
    sign: false,
    contents: [
      { x: 130, y: 220 },
      { x: 410, y: 220, type: 'link', path: '/Applications' },
    ],
  },

  // Windows — secondary target
  win: {
    target: [{ target: 'nsis', arch: ['x64'] }],
  },

  // Linux — tertiary target
  linux: {
    target: [{ target: 'AppImage', arch: ['x64'] }],
    category: 'AudioVideo',
  },

  // Publish configuration — override in CI via env
  publish: {
    provider: 'github',
    releaseType: 'draft',
  },
}

export default config
