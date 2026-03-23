import { apiFetch } from './client'

export function startRecording(meeting_id: string): Promise<void> {
  return apiFetch<void>('/recordings/start', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ meeting_id }),
  })
}

export function stopRecording(
  meeting_id: string,
  duration_s: number,
): Promise<{ audio_path: string }> {
  return apiFetch<{ audio_path: string }>('/recordings/stop', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ meeting_id, duration_s }),
  })
}
