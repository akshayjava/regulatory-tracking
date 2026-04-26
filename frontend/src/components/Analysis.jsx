import React, { useEffect, useState } from 'react'
import { BarChart, Bar, Cell, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { AlertCircle, CheckSquare, Square } from 'lucide-react'

const NEXT_STEPS = [
  { id: 1, label: 'Ingest base regulations (Congress, Federal Register, agencies)' },
  { id: 2, label: 'Implement daily sync from all sources' },
  { id: 3, label: 'Add automated change detection (new rules, deadline updates)' },
  { id: 4, label: 'Build Slack/email alerts for relevant regulations' },
  { id: 5, label: 'Create customer dashboard (filter by their vertical)' },
  { id: 6, label: 'Add regulatory impact scoring (AI-powered)' },
  { id: 7, label: 'Build compliance tracking (gap analysis per customer)' },
]

const URGENCY_COLORS = { critical: '#ef4444', high: '#f97316', medium: '#f59e0b', low: '#94a3b8' }
const AGENCY_COLORS = ['#3b82f6', '#8b5cf6', '#10b981', '#f59e0b', '#ef4444', '#06b6d4', '#ec4899']

export default function Analysis({ apiBase }) {
  const [stats, setStats] = useState(null)
  const [deadlines, setDeadlines] = useState([])
  const [complex, setComplex] = useState([])
  const [checks, setChecks] = useState(() => {
    try { return JSON.parse(localStorage.getItem('lattice_nextsteps') || '{}') } catch { return {} }
  })

  useEffect(() => {
    fetch(`${apiBase}/regulations/stats/summary`).then(r => r.json()).then(setStats).catch(() => {})
    fetch(`${apiBase}/alerts/deadlines?days=90`).then(r => r.json()).then(setDeadlines).catch(() => {})
    fetch(`${apiBase}/regulations?page_size=5`).then(r => r.json()).then(d => setComplex(d.items || [])).catch(() => {})
  }, [apiBase])

  const toggleCheck = (id) => {
    const next = { ...checks, [id]: !checks[id] }
    setChecks(next)
    localStorage.setItem('lattice_nextsteps', JSON.stringify(next))
  }

  const agencyData = stats
    ? Object.entries(stats.by_agency || {}).map(([name, value]) => ({ name, value })).sort((a, b) => b.value - a.value).slice(0, 7)
    : []

  const grouped = deadlines.reduce((acc, d) => {
    const key = d.urgency || 'medium'
    if (!acc[key]) acc[key] = []
    acc[key].push(d)
    return acc
  }, {})

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
      {/* Summary Cards */}
      {stats && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4,1fr)', gap: 16 }}>
          {[
            { label: 'Most Regulated', value: Object.entries(stats.by_vertical || {}).sort((a,b)=>b[1]-a[1])[0]?.[0] || '—', sub: `${Object.entries(stats.by_vertical||{}).sort((a,b)=>b[1]-a[1])[0]?.[1] || 0} regulations` },
            { label: 'Most Active Agency', value: Object.entries(stats.by_agency || {}).sort((a,b)=>b[1]-a[1])[0]?.[0] || '—', sub: `${Object.entries(stats.by_agency||{}).sort((a,b)=>b[1]-a[1])[0]?.[1] || 0} regulations` },
            { label: 'Critical Deadlines', value: deadlines.filter(d => d.urgency === 'critical').length, sub: 'next 90 days' },
            { label: 'Coverage', value: `${Object.keys(stats.by_vertical||{}).length} Verticals`, sub: `${Object.keys(stats.by_agency||{}).length} Agencies tracked` },
          ].map((card, i) => (
            <div key={i} style={{ background: '#1e293b', border: '1px solid #334155', borderRadius: 10, padding: 16 }}>
              <div style={{ fontSize: 12, color: '#60a5fa', marginBottom: 6, fontWeight: 600 }}>{card.label}</div>
              <div style={{ fontSize: 24, fontWeight: 700, textTransform: 'capitalize' }}>{card.value}</div>
              <div style={{ fontSize: 12, color: '#64748b', marginTop: 2 }}>{card.sub}</div>
            </div>
          ))}
        </div>
      )}

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 24 }}>
        {/* Agency Chart */}
        <div style={{ background: '#1e293b', border: '1px solid #334155', borderRadius: 10, padding: 24 }}>
          <h2 style={{ margin: '0 0 16px', fontSize: 16, fontWeight: 600 }}>Regulations by Agency</h2>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={agencyData} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis type="number" stroke="#94a3b8" />
              <YAxis dataKey="name" type="category" stroke="#94a3b8" width={60} />
              <Tooltip contentStyle={{ background: '#1e293b', border: '1px solid #475569' }} />
              <Bar dataKey="value" name="Regulations" radius={[0, 4, 4, 0]}>
                {agencyData.map((_, i) => <Cell key={i} fill={AGENCY_COLORS[i % AGENCY_COLORS.length]} />)}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Upcoming Deadlines */}
        <div style={{ background: '#1e293b', border: '1px solid #334155', borderRadius: 10, padding: 24 }}>
          <h2 style={{ margin: '0 0 16px', fontSize: 16, fontWeight: 600 }}>Upcoming Deadlines (90 days)</h2>
          {deadlines.length === 0
            ? <div style={{ color: '#64748b', textAlign: 'center', padding: 40 }}>No upcoming deadlines</div>
            : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 6, maxHeight: 250, overflowY: 'auto' }}>
                {['critical', 'high', 'medium', 'low'].flatMap(urgency =>
                  (grouped[urgency] || []).map(d => (
                    <div key={d.regulation_id} style={{
                      display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                      padding: '8px 12px', background: 'rgba(51,65,85,0.4)', borderRadius: 6,
                      borderLeft: `3px solid ${URGENCY_COLORS[urgency]}`,
                    }}>
                      <div style={{ flex: 1, minWidth: 0 }}>
                        <div style={{ fontSize: 13, fontWeight: 500, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{d.title}</div>
                        <div style={{ fontSize: 11, color: '#64748b' }}>{d.verticals?.join(', ')}</div>
                      </div>
                      <div style={{ textAlign: 'right', flexShrink: 0, marginLeft: 12 }}>
                        <div style={{ fontSize: 12, color: URGENCY_COLORS[urgency], fontWeight: 600 }}>{d.days_until}d</div>
                        <div style={{ fontSize: 10, color: '#64748b' }}>{new Date(d.deadline_date).toLocaleDateString()}</div>
                      </div>
                    </div>
                  ))
                )}
              </div>
            )
          }
        </div>
      </div>

      {/* Next Steps Checklist */}
      <div style={{ background: '#1e293b', border: '1px solid #3b82f6', borderRadius: 10, padding: 24 }}>
        <h2 style={{ margin: '0 0 16px', fontSize: 16, fontWeight: 600 }}>🚀 Product Roadmap — Next Steps</h2>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
          {NEXT_STEPS.map(step => (
            <button
              key={step.id}
              onClick={() => toggleCheck(step.id)}
              onFocus={e => e.currentTarget.style.boxShadow = '0 0 0 2px #3b82f6'}
              onBlur={e => e.currentTarget.style.boxShadow = 'none'}
              style={{
                display: 'flex', alignItems: 'center', gap: 12, padding: '10px 14px',
                background: checks[step.id] ? 'rgba(16,185,129,0.1)' : 'rgba(51,65,85,0.3)',
                border: `1px solid ${checks[step.id] ? '#065f46' : '#334155'}`,
                borderRadius: 8, cursor: 'pointer', transition: 'all 0.15s',
                width: '100%', textAlign: 'left', outline: 'none'
              }}
            >
              {checks[step.id]
                ? <CheckSquare size={18} color="#10b981" />
                : <Square size={18} color="#64748b" />
              }
              <span style={{ fontSize: 14, color: checks[step.id] ? '#6ee7b7' : '#cbd5e1', textDecoration: checks[step.id] ? 'line-through' : 'none' }}>
                {step.id}. {step.label}
              </span>
            </button>
          ))}
        </div>
        <div style={{ marginTop: 12, fontSize: 12, color: '#475569' }}>
          {Object.values(checks).filter(Boolean).length} / {NEXT_STEPS.length} completed
        </div>
      </div>
    </div>
  )
}
