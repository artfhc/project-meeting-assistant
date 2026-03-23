import { apiFetch } from './client'

export function enqueueSummary(
  meeting_id: string,
  prompt_key?: string | null,
): Promise<void> {
  return apiFetch<void>('/summaries', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ meeting_id, prompt_key }),
  })
}
