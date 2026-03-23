import { apiFetch } from './client'

export function enqueueTranscription(meeting_id: string): Promise<void> {
  return apiFetch<void>('/transcriptions', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ meeting_id }),
  })
}
