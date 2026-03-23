export const BASE_URL = import.meta.env.VITE_BACKEND_URL ?? 'http://localhost:7357'

export async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${BASE_URL}${path}`, options)

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

  return response.json() as Promise<T>
}
