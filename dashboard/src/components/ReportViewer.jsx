import React from 'react'
import Markdown from 'react-markdown'

export default function ReportViewer({ report, onExport }) {
  if (!report) return null

  return (
    <div className="report-section">
      <div className="report-header">
        <h2>Research Report</h2>
        {onExport && (
          <button className="btn btn-export" onClick={onExport}>
            Download Markdown
          </button>
        )}
      </div>
      <div className="report-content">
        <Markdown>{report}</Markdown>
      </div>
    </div>
  )
}
