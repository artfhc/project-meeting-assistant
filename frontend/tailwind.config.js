/** @type {import('tailwindcss').Config} */
export default {
  // Restrict Tailwind's class scanning to source files only — avoids false
  // positives from node_modules and keeps the production CSS bundle lean.
  content: [
    './index.html',
    './src/**/*.{ts,tsx}',
  ],

  // Enable class-based dark mode so the renderer can toggle it by adding/
  // removing the 'dark' class on <html>. Zustand settings store drives this
  // in Phase 3.
  darkMode: 'class',

  theme: {
    extend: {
      // Design tokens live here — Phase 7 will flesh these out.
      colors: {
        brand: {
          50:  '#f0f9ff',
          100: '#e0f2fe',
          500: '#0ea5e9',
          600: '#0284c7',
          700: '#0369a1',
          900: '#0c4a6e',
        },
      },
      fontFamily: {
        sans: [
          // System font stack — avoids a web font request in an offline-capable app
          '-apple-system',
          'BlinkMacSystemFont',
          '"Segoe UI"',
          'Roboto',
          '"Helvetica Neue"',
          'Arial',
          'sans-serif',
        ],
        mono: [
          '"SF Mono"',
          '"Fira Code"',
          '"Cascadia Code"',
          'Menlo',
          'monospace',
        ],
      },
    },
  },

  plugins: [],
}
