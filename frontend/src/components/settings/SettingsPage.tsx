import { useState, useEffect } from 'react'
import { useSettingsStore } from '../../stores/settingsStore'
import { saveSettings } from '../../api/settings'
import type { Settings } from '../../types'

// ---------------------------------------------------------------------------
// Field wrapper
// ---------------------------------------------------------------------------

function Field({
  label,
  htmlFor,
  children,
}: {
  label: string
  htmlFor: string
  children: React.ReactNode
}) {
  return (
    <div className="space-y-1.5">
      <label
        htmlFor={htmlFor}
        className="block text-sm font-medium text-gray-300"
      >
        {label}
      </label>
      {children}
    </div>
  )
}

const inputClass =
  'w-full rounded-md border border-gray-700 bg-gray-900 px-3 py-2 text-sm text-gray-200 placeholder-gray-600 focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500'

const selectClass =
  'w-full rounded-md border border-gray-700 bg-gray-900 px-3 py-2 text-sm text-gray-200 focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500'

// ---------------------------------------------------------------------------
// SettingsPage
// ---------------------------------------------------------------------------

const WHISPER_MODELS: Settings['whisper_model'][] = [
  'tiny',
  'base',
  'small',
  'medium',
  'large',
]

const DEFAULT_SETTINGS: Settings = {
  openai_api_key: '',
  whisper_model: 'base',
  audio_device_index: -1,
  output_dir: '',
  default_prompt_key: '',
  theme: 'dark',
}

export default function SettingsPage() {
  const storeSettings = useSettingsStore((s) => s.settings)
  const setStoreSettings = useSettingsStore((s) => s.setSettings)

  const [form, setForm] = useState<Settings>(storeSettings ?? DEFAULT_SETTINGS)
  const [isSaving, setIsSaving] = useState(false)

  // Sync form when the store gets populated externally (e.g. after the App's
  // initial data load completes after backend becomes ready)
  useEffect(() => {
    if (storeSettings) {
      setForm(storeSettings)
    }
  }, [storeSettings])

  function handleChange<K extends keyof Settings>(key: K, value: Settings[K]) {
    setForm((prev) => ({ ...prev, [key]: value }))
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setIsSaving(true)
    try {
      const saved = await saveSettings(form)
      setStoreSettings(saved)
    } catch (err) {
      console.error('[SettingsPage] Failed to save settings:', err)
    } finally {
      setIsSaving(false)
    }
  }

  async function handleChooseOutputDir() {
    const path = await window.electronAPI?.openFolder()
    if (path) {
      handleChange('output_dir', path)
    }
  }

  return (
    <div className="h-full overflow-y-auto">
      <div className="mx-auto max-w-xl px-6 py-8">
        <h2 className="mb-6 text-lg font-semibold text-gray-100">Settings</h2>

        <form onSubmit={(e) => void handleSubmit(e)} className="space-y-6">
          {/* OpenAI API Key */}
          <Field label="OpenAI API Key" htmlFor="openai_api_key">
            <input
              id="openai_api_key"
              type="password"
              autoComplete="off"
              value={form.openai_api_key}
              onChange={(e) => handleChange('openai_api_key', e.target.value)}
              placeholder="sk-..."
              className={inputClass}
            />
          </Field>

          {/* Whisper Model */}
          <Field label="Whisper Model" htmlFor="whisper_model">
            <select
              id="whisper_model"
              value={form.whisper_model}
              onChange={(e) =>
                handleChange(
                  'whisper_model',
                  e.target.value as Settings['whisper_model'],
                )
              }
              className={selectClass}
            >
              {WHISPER_MODELS.map((model) => (
                <option key={model} value={model}>
                  {model.charAt(0).toUpperCase() + model.slice(1)}
                </option>
              ))}
            </select>
            <p className="text-xs text-gray-600">
              Larger models are more accurate but slower to run.
            </p>
          </Field>

          {/* Audio Device Index */}
          <Field label="Audio Device Index" htmlFor="audio_device_index">
            <input
              id="audio_device_index"
              type="number"
              min={-1}
              value={form.audio_device_index}
              onChange={(e) =>
                handleChange('audio_device_index', Number(e.target.value))
              }
              className={inputClass}
            />
            <p className="text-xs text-gray-600">
              Set to -1 to use the system default input device.
            </p>
          </Field>

          {/* Output Directory */}
          <Field label="Output Directory" htmlFor="output_dir">
            <div className="flex gap-2">
              <input
                id="output_dir"
                type="text"
                value={form.output_dir}
                onChange={(e) => handleChange('output_dir', e.target.value)}
                placeholder="/Users/you/Meetings"
                className={inputClass}
              />
              <button
                type="button"
                onClick={() => void handleChooseOutputDir()}
                className="shrink-0 rounded-md border border-gray-700 bg-gray-800 px-3 py-2 text-sm text-gray-300 transition-colors hover:bg-gray-700"
              >
                Browse
              </button>
            </div>
          </Field>

          {/* Default Prompt Key */}
          <Field label="Default Prompt Key" htmlFor="default_prompt_key">
            <input
              id="default_prompt_key"
              type="text"
              value={form.default_prompt_key}
              onChange={(e) =>
                handleChange('default_prompt_key', e.target.value)
              }
              placeholder="default"
              className={inputClass}
            />
            <p className="text-xs text-gray-600">
              Must match a key defined in prompts.yaml.
            </p>
          </Field>

          {/* Theme */}
          <Field label="Theme" htmlFor="theme">
            <select
              id="theme"
              value={form.theme}
              onChange={(e) =>
                handleChange('theme', e.target.value as Settings['theme'])
              }
              className={selectClass}
            >
              <option value="dark">Dark</option>
              <option value="light">Light</option>
            </select>
          </Field>

          {/* Save button */}
          <div className="pt-2">
            <button
              type="submit"
              disabled={isSaving}
              className="rounded-md bg-brand-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-brand-700 focus:outline-none focus:ring-2 focus:ring-brand-500 focus:ring-offset-2 focus:ring-offset-gray-950 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {isSaving ? 'Saving...' : 'Save Settings'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
