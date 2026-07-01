import React, { useState, useCallback } from 'react'
import AgentStatus from './components/AgentStatus'
import ReportViewer from './components/ReportViewer'
import SourceQuality from './components/SourceQuality'
import { useWebSocket } from './hooks/useWebSocket'

const AGENTS = [
  { id: 'academic', name: 'Academic', icon: '' },
  { id: 'market', name: 'Market', icon: '' },
  { id: 'code', name: 'Code', icon: '' },
]

export default function App() {
  const [topic, setTopic] = useState('')
  const [researchId, setResearchId] = useState(null)
  const [agentStatuses, setAgentStatuses] = useState({})
  const [logs, setLogs] = useState([])
  const [report, setReport] = useState(null)
  const [agentData, setAgentData] = useState({})
  const [verification, setVerification] = useState(null)
  const [isRunning, setIsRunning] = useState(false)

  const handleWsMessage = useCallback((data) => {
    const time = new Date().toLocaleTimeString()

    if (data.type === 'research_started') {
      setLogs(prev => [...prev, { time, agent: 'System', msg: `Research started: ${data.topic}` }])
    }

    if (data.type === 'agent_status') {
      setAgentStatuses(prev => ({
        ...prev,
        [data.agent]: { status: data.status, message: data.message, progress: data.progress || 0 },
      }))
      setLogs(prev => [...prev, { time, agent: data.agent, msg: data.message }])
    }

    if (data.type === 'research_complete') {
      setReport(data.report)
      setAgentData(data.agents || {})
      setVerification(data.verification)
      setIsRunning(false)
      setLogs(prev => [...prev, { time, agent: 'System', msg: 'Research complete!' }])
    }

    if (data.type === 'research_error') {
      setIsRunning(false)
      setLogs(prev => [...prev, { time, agent: 'System', msg: `Error: ${data.error}` }])
    }
  }, [])

  useWebSocket(researchId, handleWsMessage)

  const startResearch = async () => {
    if (!topic.trim()) return
    setIsRunning(true)
    setReport(null)
    setAgentData({})
    setVerification(null)
    setLogs([])
    setAgentStatuses({})

    try {
      const resp = await fetch('/api/research', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ topic: topic.trim() }),
      })
      const data = await resp.json()
      setResearchId(data.research_id)
    } catch (err) {
      setIsRunning(false)
      setLogs(prev => [...prev, { time: new Date().toLocaleTimeString(), agent: 'System', msg: `Failed: ${err.message}` }])
    }
  }

  const exportReport = () => {
    if (!researchId) return
    window.open(`/api/export/${researchId}`, '_blank')
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !isRunning) startResearch()
  }

  return (
    <div className="app">
      <div className="header">
        <h1>Sentinel</h1>
        <p>Privacy-First Multi-Agent Research Network</p>
      </div>

      <div className="input-section">
        <div className="input-row">
          <input
            type="text"
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Enter research topic (e.g., AI Agent safety mechanisms)"
            disabled={isRunning}
          />
          <button className="btn" onClick={startResearch} disabled={isRunning || !topic.trim()}>
            {isRunning ? 'Researching...' : 'Start Research'}
          </button>
        </div>
      </div>

      <div className="agents-grid">
        {AGENTS.map(agent => (
          <AgentStatus
            key={agent.id}
            name={agent.name}
            icon={agent.icon}
            status={agentStatuses[agent.id]}
          />
        ))}
        <div className="agent-card">
          <h3>Bittensor</h3>
          <div className="status">
            {verification ? '✓' : isRunning ? '◉' : '○'}
          </div>
          <div className="message">
            {verification ? `Score: ${verification.score}` : 'Awaiting verification'}
          </div>
        </div>
      </div>

      {logs.length > 0 && (
        <div className="log-section">
          <h2>Agent Activity</h2>
          <div className="log-entries">
            {logs.map((log, i) => (
              <div key={i} className="log-entry">
                <span className="time">[{log.time}]</span>{' '}
                <span className="agent">{log.agent}</span>{' '}
                <span className="msg">{log.msg}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {report && (
        <SourceQuality agentData={agentData} verification={verification} />
      )}

      {report ? (
        <ReportViewer report={report} onExport={exportReport} />
      ) : (
        !isRunning && logs.length === 0 && (
          <div className="empty-state">
            <p>Enter a topic and click "Start Research" to begin.</p>
            <p style={{ marginTop: '0.5rem', fontSize: '0.9rem' }}>
              Three specialized agents search academic, market, and code sources in parallel,
              protected by Venice.ai's privacy infrastructure.
            </p>
          </div>
        )
      )}
    </div>
  )
}
