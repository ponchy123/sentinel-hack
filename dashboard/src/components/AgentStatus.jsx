import React from 'react'

export default function AgentStatus({ name, icon, status }) {
  const state = status?.status || 'idle'
  const message = status?.message || 'Waiting...'
  const progress = status?.progress ?? 0

  const statusIcon = {
    idle: '○',
    working: '◉',
    done: '✓',
    error: '✗',
  }[state] || '○'

  return (
    <div className={`agent-card ${state}`}>
      <h3>{icon} {name}</h3>
      <div className="status">{statusIcon}</div>
      <div className="message">{message}</div>
      {state === 'working' && (
        <div className="progress-bar">
          <div
            className="fill"
            style={{ width: progress > 0 ? `${progress * 100}%` : '60%' }}
          />
        </div>
      )}
    </div>
  )
}
