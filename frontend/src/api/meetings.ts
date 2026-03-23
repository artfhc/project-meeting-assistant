import type { Meeting } from '../types'
import { apiFetch, BASE_URL } from './client'

export function listMeetings(): Promise<Meeting[]> {
  return apiFetch<Meeting[]>('/meetings')
}

export function createMeeting(data: {
  title?: string
  prompt_key?: string | null
}): Promise<Meeting> {
  return apiFetch<Meeting>('/meetings', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  })
}

export function getMeeting(id: string): Promise<Meeting> {
  return apiFetch<Meeting>(`/meetings/${id}`)
}

export function updateMeeting(
  id: string,
  data: { title?: string; prompt_key?: string | null },
): Promise<Meeting> {
  return apiFetch<Meeting>(`/meetings/${id}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  })
}

export async function deleteMeeting(id: string): Promise<void> {
  const response = await fetch(`${BASE_URL}/meetings/${id}`, { method: 'DELETE' })
  if (!response.ok) {
    let message = `Request failed: ${response.status} ${response.statusText}`
    try {
      const body = await response.json()
      if (typeof body?.detail === 'string') {
        message = body.detail
      }
    } catch {
      // body was not JSON — keep the default message
    }
    throw new Error(message)
  }
}
