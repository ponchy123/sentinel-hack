import { useEffect, useRef, useCallback } from 'react'

export function useWebSocket(researchId, onMessage) {
  const wsRef = useRef(null)
  const reconnectTimeout = useRef(null)
  const retryCount = useRef(0)
  const MAX_RETRIES = 10

  const connect = useCallback(() => {
    if (!researchId) return

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const host = window.location.host
    const url = `${protocol}//${host}/ws/${researchId}`

    const ws = new WebSocket(url)
    wsRef.current = ws

    ws.onopen = () => {
      retryCount.current = 0
      console.log('WebSocket connected')
    }

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        onMessage(data)
      } catch (e) {
        console.error('Failed to parse WebSocket message:', e)
      }
    }

    ws.onclose = () => {
      if (retryCount.current >= MAX_RETRIES) {
        console.log('WebSocket max retries reached, giving up')
        return
      }
      const delay = Math.min(1000 * Math.pow(2, retryCount.current), 30000)
      retryCount.current++
      console.log(`WebSocket disconnected, retry ${retryCount.current} in ${delay}ms...`)
      reconnectTimeout.current = setTimeout(connect, delay)
    }

    ws.onerror = (error) => {
      console.error('WebSocket error:', error)
    }
  }, [researchId, onMessage])

  useEffect(() => {
    connect()
    return () => {
      if (wsRef.current) wsRef.current.close()
      if (reconnectTimeout.current) clearTimeout(reconnectTimeout.current)
    }
  }, [connect])

  return wsRef
}
