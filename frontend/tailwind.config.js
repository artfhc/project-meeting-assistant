/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './index.html',
    './src/**/*.{ts,tsx}',
  ],

  darkMode: 'class',

  theme: {
    extend: {
      colors: {
        // Warm amber accent palette — replaces the old `brand` sky-blue tokens
        amber: {
          400: '#fbbf24',
          500: '#f59e0b',
          600: '#d97706',
        },
        // Deep surface backgrounds
        surface: {
          base:  '#0d0d0f',
          raised: '#111114',
          overlay: '#16161a',
          muted: '#1c1c21',
        },
        // Warm border tones
        border: {
          subtle: '#1f1f25',
          warm:   '#27272f',
          muted:  '#2e2e38',
        },
      },
      fontFamily: {
        // DM Mono everywhere — this is a tool, not a consumer app
        sans: ['"DM Mono"', 'monospace'],
        mono: ['"DM Mono"', 'monospace'],
      },
      keyframes: {
        'amber-pulse': {
          '0%, 100%': { boxShadow: '0 0 0 0 rgba(245, 158, 11, 0)' },
          '50%':       { boxShadow: '0 0 0 8px rgba(245, 158, 11, 0.15)' },
        },
        'dot-pulse': {
          '0%, 100%': { opacity: '1' },
          '50%':      { opacity: '0.3' },
        },
      },
      animation: {
        'amber-pulse': 'amber-pulse 2s ease-in-out infinite',
        'dot-pulse':   'dot-pulse 1.4s ease-in-out infinite',
      },
    },
  },

  plugins: [],
}
