import { useState, useEffect } from 'react'
import { useSettingsStore } from '../../stores/settingsStore'
import { listPromptKeys, saveSettings } from '../../api/settings'
import type { Settings } from '../../types'

// ---------------------------------------------------------------------------
// Field wrapper
// ---------------------------------------------------------------------------

function Field({
  label,
  htmlFor,
  hint,
  children,
}: {
  label: string
  htmlFor: string
  hint?: React.ReactNode
  children: React.ReactNode
}) {
  return (
    <div className="space-y-1.5">
      <label
        htmlFor={htmlFor}
        className="block text-xs tracking-widest uppercase"
        style={{ color: 'var(--color-text-muted)' }}
      >
        {label}
      </label>
      {children}
      {hint && (
        <p className="text-xs" style={{ color: 'var(--color-text-faint)' }}>
          {hint}
        </p>
      )}
    </div>
  )
}

const inputStyle: React.CSSProperties = {
  width: '100%',
  backgroundColor: 'var(--color-bg-muted)',
  border: '1px solid var(--color-border-muted)',
  color: '#d4d4d8',
  padding: '6px 10px',
  fontSize: '12px',
  fontFamily: '"DM Mono", monospace',
  outline: 'none',
}

const selectStyle: React.CSSProperties = {
  ...inputStyle,
  cursor: 'pointer',
}

function StyledInput(props: React.InputHTMLAttributes<HTMLInputElement>) {
  return (
    <input
      {...props}
      style={{ ...inputStyle, ...props.style }}
      onFocus={(e) => {
        e.currentTarget.style.borderColor = 'var(--color-amber)'
        props.onFocus?.(e)
      }}
      onBlur={(e) => {
        e.currentTarget.style.borderColor = 'var(--color-border-muted)'
        props.onBlur?.(e)
      }}
    />
  )
}

function StyledSelect(props: React.SelectHTMLAttributes<HTMLSelectElement>) {
  return (
    <select
      {...props}
      style={{ ...selectStyle, ...props.style }}
      onFocus={(e) => {
        e.currentTarget.style.borderColor = 'var(--color-amber)'
        props.onFocus?.(e)
      }}
      onBlur={(e) => {
        e.currentTarget.style.borderColor = 'var(--color-border-muted)'
        props.onBlur?.(e)
      }}
    />
  )
}

// ---------------------------------------------------------------------------
// Section divider
// ---------------------------------------------------------------------------

function Section({ title }: { title: string }) {
  return (
    <div className="flex items-center gap-3 pt-2">
      <span
        className="text-xs tracking-widest uppercase"
        style={{ color: 'var(--color-amber)', whiteSpace: 'nowrap' }}
      >
        {title}
      </span>
      <div className="h-px flex-1" style={{ backgroundColor: 'var(--color-border-subtle)' }} />
    </div>
  )
}

// ---------------------------------------------------------------------------
// SettingsPage
// ---------------------------------------------------------------------------

const WHISPER_MODELS: Settings['whisper_model'][] = [
  'tiny', 'base', 'small', 'medium', 'large',
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
  const [promptKeys, setPromptKeys] = useState<string[]>([])

  useEffect(() => {
    if (storeSettings) setForm(storeSettings)
  }, [storeSettings])

  useEffect(() => {
    listPromptKeys()
      .then(setPromptKeys)
      .catch((err) => console.error('[SettingsPage] Failed to load prompt keys:', err))
  }, [])

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
    if (path) handleChange('output_dir', path)
  }

  return (
    <div className="h-full overflow-y-auto" style={{ backgroundColor: 'var(--color-bg-base)' }}>
      <div className="mx-auto max-w-xl px-6 py-8">
        <h2
          className="mb-8 text-xs tracking-widest uppercase"
          style={{ color: 'var(--color-text-muted)' }}
        >
          Configuration
        </h2>

        <form onSubmit={(e) => void handleSubmit(e)} className="space-y-6">

          <Section title="API" />

          <Field label="OpenAI API Key" htmlFor="openai_api_key">
            <StyledInput
              id="openai_api_key"
              type="password"
              autoComplete="off"
              value={form.openai_api_key}
              onChange={(e) => handleChange('openai_api_key', e.target.value)}
              placeholder="sk-..."
            />
          </Field>

          <Section title="Transcription" />

          <Field
            label="Whisper Model"
            htmlFor="whisper_model"
            hint="Larger models are more accurate but slower to run."
          >
            <StyledSelect
              id="whisper_model"
              value={form.whisper_model}
              onChange={(e) =>
                handleChange('whisper_model', e.target.value as Settings['whisper_model'])
              }
            >
              {WHISPER_MODELS.map((model) => (
                <option key={model} value={model}>
                  {model}
                </option>
              ))}
            </StyledSelect>
          </Field>

          <Field
            label="Audio Device Index"
            htmlFor="audio_device_index"
            hint="Set to -1 to use the system default input device."
          >
            <StyledInput
              id="audio_device_index"
              type="number"
              min={-1}
              value={form.audio_device_index}
              onChange={(e) => handleChange('audio_device_index', Number(e.target.value))}
            />
          </Field>

          <Section title="Output" />

          <Field label="Output Directory" htmlFor="output_dir">
            <div className="flex gap-2">
              <StyledInput
                id="output_dir"
                type="text"
                value={form.output_dir}
                onChange={(e) => handleChange('output_dir', e.target.value)}
                placeholder="/Users/you/Meetings"
                style={{ flex: 1, width: 'auto' }}
              />
              <button
                type="button"
                onClick={() => void handleChooseOutputDir()}
                className="shrink-0 text-xs tracking-widest uppercase transition-colors"
                style={{
                  backgroundColor: 'var(--color-bg-muted)',
                  border: '1px solid var(--color-border-muted)',
                  color: 'var(--color-text-muted)',
                  padding: '6px 12px',
                  fontFamily: '"DM Mono", monospace',
                }}
                onMouseEnter={(e) => {
                  (e.currentTarget as HTMLButtonElement).style.borderColor = 'var(--color-amber)'
                  ;(e.currentTarget as HTMLButtonElement).style.color = 'var(--color-amber)'
                }}
                onMouseLeave={(e) => {
                  (e.currentTarget as HTMLButtonElement).style.borderColor = 'var(--color-border-muted)'
                  ;(e.currentTarget as HTMLButtonElement).style.color = 'var(--color-text-muted)'
                }}
              >
                Browse
              </button>
            </div>
          </Field>

          <Section title="Summarization" />

          <Field
            label="Default Prompt Key"
            htmlFor="default_prompt_key"
            hint={<>Template keys loaded from <code style={{ fontFamily: '"DM Mono", monospace' }}>config/prompts.yaml</code>.</>}
          >
            <StyledSelect
              id="default_prompt_key"
              value={form.default_prompt_key}
              onChange={(e) => handleChange('default_prompt_key', e.target.value)}
            >
              <option value="">— use built-in default —</option>
              {promptKeys.map((key) => (
                <option key={key} value={key}>
                  {key}
                </option>
              ))}
            </StyledSelect>
          </Field>

          <Section title="Appearance" />

          <Field label="Theme" htmlFor="theme">
            <StyledSelect
              id="theme"
              value={form.theme}
              onChange={(e) => handleChange('theme', e.target.value as Settings['theme'])}
            >
              <option value="dark">dark</option>
              <option value="light">light</option>
            </StyledSelect>
          </Field>

          {/* Save */}
          <div className="pt-4">
            <button
              type="submit"
              disabled={isSaving}
              className="text-xs tracking-widest uppercase transition-all disabled:cursor-not-allowed disabled:opacity-40"
              style={{
                backgroundColor: isSaving ? 'var(--color-bg-muted)' : 'var(--color-amber)',
                color: isSaving ? 'var(--color-text-muted)' : '#0d0d0f',
                border: '1px solid var(--color-amber)',
                padding: '7px 20px',
                fontFamily: '"DM Mono", monospace',
                fontWeight: 500,
              }}
            >
              {isSaving ? 'saving...' : 'save'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
