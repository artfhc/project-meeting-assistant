import { useEffect, useRef, useState } from 'react'
import { useJobStore } from '../stores/jobStore'
import type { Job } from '../types'

const WS_URL = 'ws://localhost:7357/ws'
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
  const mountedRef = useRef(true)
  const wsRef = useRef<WebSocket | null>(null)
  const reconnectTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null)

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
            setJob(data as unknown as Job)
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
