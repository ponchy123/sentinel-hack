import React from 'react'

export default function SourceQuality({ agentData, verification }) {
  if (!agentData || Object.keys(agentData).length === 0) return null

  const totalSources = Object.values(agentData).reduce((sum, a) => sum + (a.source_count || 0), 0)
  const avgConfidence = Object.values(agentData).reduce((sum, a) => sum + (a.confidence || 0), 0) / Object.keys(agentData).length

  return (
    <div className="source-quality">
      <h2>Source Quality</h2>
      <div className="quality-grid">
        <div className="quality-card">
          <div className="quality-value">{totalSources}</div>
          <div className="quality-label">Total Sources</div>
        </div>
        <div className="quality-card">
          <div className="quality-value">{(avgConfidence * 100).toFixed(0)}%</div>
          <div className="quality-label">Avg Confidence</div>
        </div>
        {verification && (
          <div className="quality-card">
            <div className="quality-value">{verification.score}</div>
            <div className="quality-label">Bittensor Score</div>
          </div>
        )}
      </div>

      <div className="agent-sources">
        {Object.entries(agentData).map(([name, data]) => (
          <div key={name} className="agent-source-row">
            <span className="agent-name">{name}</span>
            <span className="source-count">{data.source_count} sources</span>
            <span className="confidence">{(data.confidence * 100).toFixed(0)}% conf</span>
            {data.sources && data.sources.length > 0 && (
              <span className="source-list">
                {data.sources.slice(0, 3).map((s, i) => (
                  <a key={i} href={s.url} target="_blank" rel="noopener noreferrer" className="source-link">
                    {s.provider}
                  </a>
                ))}
              </span>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}
