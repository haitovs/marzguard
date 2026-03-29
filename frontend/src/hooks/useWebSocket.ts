import { useEffect, useRef, useState, useCallback } from 'react'

interface WSData {
  type: string
  users: Record<string, { ips: string[]; count: number }>
  total_users: number
  total_ips: number
}

export function useWebSocket() {
  const [data, setData] = useState<WSData | null>(null)
  const [connected, setConnected] = useState(false)
  const wsRef = useRef<WebSocket | null>(null)

  const connect = useCallback(() => {
    const token = localStorage.getItem('marzguard_token')
    if (!token) return

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const ws = new WebSocket(`${protocol}//${window.location.host}/ws/live?token=${token}`)

    ws.onopen = () => setConnected(true)
    ws.onclose = () => {
      setConnected(false)
      setTimeout(connect, 5000)
    }
    ws.onmessage = (event) => {
      try {
        setData(JSON.parse(event.data))
      } catch {}
    }

    wsRef.current = ws
  }, [])

  useEffect(() => {
    connect()
    return () => {
      wsRef.current?.close()
    }
  }, [connect])

  return { data, connected }
}
