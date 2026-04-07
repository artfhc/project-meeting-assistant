import { useEffect, useRef, useState } from 'react'
import { useJobStore } from '../stores/jobStore'
import { useMeetingStore } from '../stores/meetingStore'
import { getMeeting } from '../api/meetings'
import { BASE_URL } from '../api/client'
import type { Job } from '../types'

const WS_URL = `${BASE_URL.replace(/^http/, 'ws')}/ws`
const RECONNECT_DELAY_MS = 3000

interface WebSocketMessage {
  type: string
  [key: string]: unknown
}

interface UseWebSocketResult {
  connected: boolean
}

export function useWebSocket(): UseWebSocketResult {
  const [connected, setConnected] = useState(false)
  const setJob = useJobStore((state) => state.setJob)
  const upsertMeeting = useMeetingStore((state) => state.upsertMeeting)
  const mountedRef = useRef(true)
  const wsRef = useRef<WebSocket | null>(null)
  const reconnectTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null)
  // Track refreshed job IDs to avoid duplicate getMeeting calls if the backend
  // sends multiple done/error messages for the same job.
  const refreshedJobsRef = useRef<Set<string>>(new Set())

  useEffect(() => {
    mountedRef.current = true

    function connect() {
      if (!mountedRef.current) return

      const ws = new WebSocket(WS_URL)
      wsRef.current = ws

      ws.onopen = () => {
        if (!mountedRef.current) {
          ws.close()
          return
        }
        setConnected(true)
      }

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data as string) as WebSocketMessage
          if (data.type === 'job_progress') {
            const job = data as unknown as Job
            setJob(job)
            // Refresh meeting data when a job finishes so transcript/summary
            // are reflected in the store without requiring a page reload.
            if ((job.stage === 'done' || job.stage === 'error') &&
                !refreshedJobsRef.current.has(job.job_id)) {
              refreshedJobsRef.current.add(job.job_id)
              getMeeting(job.meeting_id)
                .then((meeting) => upsertMeeting(meeting))
                .catch(() => {/* meeting may have been deleted */})
            }
          }
        } catch {
          // Silently ignore malformed messages — backend may send non-JSON pings
        }
      }

      ws.onclose = () => {
        setConnected(false)
        wsRef.current = null
        if (mountedRef.current) {
          reconnectTimerRef.current = setTimeout(connect, RECONNECT_DELAY_MS)
        }
      }

      ws.onerror = () => {
        // onclose fires after onerror; reconnect is handled there
        ws.close()
      }
    }

    connect()

    return () => {
      mountedRef.current = false
      if (reconnectTimerRef.current !== null) {
        clearTimeout(reconnectTimerRef.current)
      }
      if (wsRef.current) {
        wsRef.current.close()
        wsRef.current = null
      }
    }
  }, [setJob])

  return { connected }
}
