import React, { useEffect, useState } from 'react'
import { AlertCircle } from 'lucide-react'
import Dashboard from './components/Dashboard'
import RegulationList from './components/RegulationList'
import Analysis from './components/Analysis'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export { API_BASE }

const TABS = [
  { id: 'dashboard', label: '📊 Dashboard' },
  { id: 'regulations', label: '📋 Regulations' },
  { id: 'analysis', label: '📈 Analysis' },
]

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard')
  const [apiOnline, setApiOnline] = useState(true)

  useEffect(() => {
    fetch(`${API_BASE}/health`)
      .then((r) => setApiOnline(r.ok))
      .catch(() => setApiOnline(false))
  }, [])

  return (
    <div style={{ minHeight: '100vh', background: 'linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%)', color: 'white' }}>
      {/* Offline banner */}
      {!apiOnline && (
        <div style={{ background: '#7f1d1d', borderBottom: '1px solid #991b1b', padding: '8px 24px', display: 'flex', alignItems: 'center', gap: 8, fontSize: 14 }}>
          <AlertCircle size={16} />
          <span>API offline — showing cached data. Start backend: <code>uvicorn api.main:app --reload</code></span>
        </div>
      )}

      {/* Header */}
      <div style={{ maxWidth: 1280, margin: '0 auto', padding: '24px 24px 0' }}>
        <div style={{ marginBottom: 24 }}>
          <h1 style={{ fontSize: 36, fontWeight: 800, margin: 0, letterSpacing: -1 }}>LATTICE</h1>
          <p style={{ color: '#94a3b8', margin: '4px 0 0', fontSize: 14 }}>Regulatory Compliance Intelligence Platform</p>
        </div>

        {/* Tab nav */}
        <div style={{ display: 'flex', gap: 4, borderBottom: '1px solid #334155', marginBottom: 0 }}>
          {TABS.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              style={{
                padding: '10px 20px',
                background: 'none',
                border: 'none',
                borderBottom: activeTab === tab.id ? '2px solid #3b82f6' : '2px solid transparent',
                color: activeTab === tab.id ? '#60a5fa' : '#94a3b8',
                cursor: 'pointer',
                fontWeight: 500,
                fontSize: 14,
                transition: 'all 0.15s',
              }}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* Content */}
      <div style={{ maxWidth: 1280, margin: '0 auto', padding: 24 }}>
        {activeTab === 'dashboard' && <Dashboard apiBase={API_BASE} />}
        {activeTab === 'regulations' && <RegulationList apiBase={API_BASE} />}
        {activeTab === 'analysis' && <Analysis apiBase={API_BASE} />}
      </div>

      {/* Footer */}
      <div style={{ maxWidth: 1280, margin: '0 auto', padding: '16px 24px', borderTop: '1px solid #1e293b', textAlign: 'center', color: '#475569', fontSize: 13 }}>
        LATTICE Regulatory Intelligence • Real-time sync enabled
      </div>
    </div>
  )
}
