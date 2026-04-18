import React, { useEffect, useState } from 'react'
import {
  BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts'
import { AlertCircle, CheckCircle, Clock, Database, Zap } from 'lucide-react'

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6']
const STATUS_COLORS = { proposed: '#f59e0b', final: '#3b82f6', effective: '#10b981' }

function StatCard({ label, value, color, icon, highlight }) {
  return (
    <div style={{
      background: highlight ? 'rgba(127,29,29,0.3)' : 'rgba(51,65,85,0.5)',
      border: `1px solid ${highlight ? '#991b1b' : '#475569'}`,
      borderRadius: 10, padding: 16,
    }}>
      <div style={{ fontSize: 12, color: '#94a3b8', marginBottom: 4 }}>{label}</div>
      <div style={{ fontSize: 30, fontWeight: 700, color: color || 'white' }}>{value ?? '—'}</div>
    </div>
  )
}

function Skeleton({ height = 300 }) {
  return <div style={{ height, background: '#1e293b', borderRadius: 8, animation: 'pulse 1.5s infinite' }} />
}

export default function Dashboard({ apiBase }) {
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetch(`${apiBase}/regulations/stats/summary`)
      .then(r => { if (!r.ok) throw new Error('API error'); return r.json() })
      .then(data => { setStats(data); setLoading(false) })
      .catch(e => { setError(e.message); setLoading(false) })
  }, [apiBase])

  if (loading) return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5,1fr)', gap: 16 }}>
        {[...Array(5)].map((_, i) => <Skeleton key={i} height={80} />)}
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 24 }}>
        <Skeleton /><Skeleton />
      </div>
    </div>
  )

  if (error) return (
    <div style={{ textAlign: 'center', padding: 60, color: '#ef4444' }}>
      <AlertCircle size={40} style={{ marginBottom: 12 }} />
      <p>Could not load dashboard data: {error}</p>
      <p style={{ color: '#94a3b8', fontSize: 13 }}>Make sure the backend is running at {apiBase}</p>
    </div>
  )

  const statusData = Object.entries(stats.by_status || {}).map(([name, value]) => ({ name, value }))
  const verticalData = Object.entries(stats.by_vertical || {}).map(([name, value]) => ({ name, value }))
  const agencyData = Object.entries(stats.by_agency || {})
    .map(([name, value]) => ({ name, value }))
    .sort((a, b) => b.value - a.value)
    .slice(0, 7)

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
      {/* Stat Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5,1fr)', gap: 16 }}>
        <StatCard label="Total Regulations" value={stats.total_regulations} color="#60a5fa" />
        <StatCard label="Active Rules" value={stats.by_status?.effective || 0} />
        <StatCard label="Proposed" value={stats.by_status?.proposed || 0} color="#f59e0b" />
        <StatCard label="⏰ Due in 30 Days" value={stats.deadlines_30_days || 0} color="#ef4444" highlight />
        <StatCard label="Sources" value={stats.sources?.length || 0} />
      </div>

      {/* Charts Row */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 24 }}>
        {/* Status Pie */}
        <div style={{ background: '#1e293b', border: '1px solid #334155', borderRadius: 10, padding: 24 }}>
          <h2 style={{ margin: '0 0 16px', fontSize: 16, fontWeight: 600 }}>Regulation Status</h2>
          <ResponsiveContainer width="100%" height={280}>
            <PieChart>
              <Pie data={statusData} cx="50%" cy="50%" outerRadius={100} dataKey="value" label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}>
                {statusData.map((entry, i) => (
                  <Cell key={i} fill={STATUS_COLORS[entry.name] || COLORS[i]} />
                ))}
              </Pie>
              <Tooltip contentStyle={{ background: '#1e293b', border: '1px solid #475569' }} />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Vertical Bar */}
        <div style={{ background: '#1e293b', border: '1px solid #334155', borderRadius: 10, padding: 24 }}>
          <h2 style={{ margin: '0 0 16px', fontSize: 16, fontWeight: 600 }}>Regulations by Vertical</h2>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={verticalData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis dataKey="name" stroke="#94a3b8" />
              <YAxis stroke="#94a3b8" />
              <Tooltip contentStyle={{ background: '#1e293b', border: '1px solid #475569' }} />
              <Bar dataKey="value" name="Regulations" radius={[6, 6, 0, 0]}>
                {verticalData.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Top Agencies */}
      <div style={{ background: '#1e293b', border: '1px solid #334155', borderRadius: 10, padding: 24 }}>
        <h2 style={{ margin: '0 0 16px', fontSize: 16, fontWeight: 600 }}>Top Regulatory Agencies</h2>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
          {agencyData.map(({ name, value }) => {
            const max = Math.max(...agencyData.map(d => d.value))
            return (
              <div key={name} style={{ display: 'flex', alignItems: 'center', gap: 12, padding: '10px 14px', background: 'rgba(51,65,85,0.4)', borderRadius: 8 }}>
                <span style={{ fontWeight: 600, width: 60, flexShrink: 0 }}>{name}</span>
                <div style={{ flex: 1, background: '#334155', height: 8, borderRadius: 4 }}>
                  <div style={{ width: `${(value / max) * 100}%`, background: '#3b82f6', height: 8, borderRadius: 4, transition: 'width 0.5s' }} />
                </div>
                <span style={{ width: 40, textAlign: 'right', color: '#94a3b8' }}>{value}</span>
              </div>
            )
          })}
        </div>
      </div>

      {/* Source Status */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3,1fr)', gap: 16 }}>
        {(stats.sources || []).map(source => (
          <div key={source.abbreviation} style={{ background: '#1e293b', border: '1px solid #334155', borderRadius: 10, padding: 16 }}>
            <div style={{ fontWeight: 600, marginBottom: 4 }}>{source.name}</div>
            <div style={{ fontSize: 26, fontWeight: 700, color: '#60a5fa', marginBottom: 2 }}>{source.regulation_count}</div>
            <div style={{ fontSize: 12, color: '#94a3b8', marginBottom: 8 }}>regulations</div>
            <div style={{ fontSize: 12, color: source.status === 'active' ? '#4ade80' : '#ef4444' }}>
              {source.status === 'active' ? '✅' : '❌'} {source.last_sync ? `Synced ${new Date(source.last_sync).toLocaleString()}` : 'Not yet synced'}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
