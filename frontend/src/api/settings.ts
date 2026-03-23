import type { Settings } from '../types'
import { apiFetch } from './client'

export function getSettings(): Promise<Settings> {
  return apiFetch<Settings>('/settings')
}

export function saveSettings(settings: Settings): Promise<Settings> {
  return apiFetch<Settings>('/settings', {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(settings),
  })
}

export function listPromptKeys(): Promise<string[]> {
  return apiFetch<string[]>('/settings/prompts')
}
