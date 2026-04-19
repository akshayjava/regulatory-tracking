import React, { useEffect, useState } from 'react'
import { RefreshCw, CheckCircle, AlertCircle, Clock, Activity, Database, Zap } from 'lucide-react'

const URGENCY_COLORS = {
  critical: { bg: '#7f1d1d', text: '#fca5a5', dot: '#ef4444' },
  high:     { bg: '#78350f', text: '#fde68a', dot: '#f59e0b' },
  medium:   { bg: '#1e3a5f', text: '#93c5fd', dot: '#3b82f6' },
  low:      { bg: '#14532d', text: '#86efac', dot: '#22c55e' },
}

function StatCard({ label, value, sub, icon: Icon, color }) {
  return (
    <div style={{
      background: '#1e293b',
      border: '1px solid #334155',
      borderRadius: 12,
      padding: '20px 24px',
      display: 'flex',
      alignItems: 'flex-start',
      gap: 16,
    }}>
      <div style={{ background: '#0f172a', borderRadius: 10, padding: 10 }}>
        <Icon size={20} color={color || '#60a5fa'} />
      </div>
      <div>
        <div style={{ fontSize: 28, fontWeight: 700, lineHeight: 1 }}>{value}</div>
        <div style={{ color: '#94a3b8', fontSize: 13, marginTop: 4 }}>{label}</div>
        {sub && <div style={{ color: '#64748b', fontSize: 12, marginTop: 2 }}>{sub}</div>}
      </div>
    </div>
  )
}

export default function SourceMonitor({ apiBase }) {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [syncing, setSyncing] = useState(null)
  const [syncResult, setSyncResult] = useState(null)
  const [error, setError] = useState(null)

  function load() {
    setLoading(true)
    fetch(`${apiBase}/sources/ingestion-status`)
      .then(r => r.json())
      .then(d => { setData(d); setLoading(false) })
      .catch(e => { setError(e.message); setLoading(false) })
  }

  useEffect(() => { load() }, [])

  async function triggerSync(sourceName) {
    setSyncing(sourceName)
    setSyncResult(null)
    try {
      const resp = await fetch(`${apiBase}/sources/sync/${sourceName}`, { method: 'POST' })
      const result = await resp.json()
      setSyncResult(result)
      load() // Refresh data
    } catch (e) {
      setSyncResult({ status: 'error', error: e.message })
    } finally {
      setSyncing(null)
    }
  }

  if (loading) return (
    <div style={{ color: '#94a3b8', padding: 40, textAlign: 'center' }}>Loading ingestion status...</div>
  )

  if (error) return (
    <div style={{ color: '#ef4444', padding: 40, textAlign: 'center' }}>Failed to load: {error}</div>
  )

  const card = {
    background: '#1e293b',
    border: '1px solid #334155',
    borderRadius: 12,
    padding: 20,
    marginBottom: 20,
  }

  const verticals = data?.vertical_breakdown || {}
  const totalVerticalRegs = Object.values(verticals).reduce((s, n) => s + n, 0)

  return (
    <div>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 24 }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 6 }}>
            <Activity size={24} color="#22d3ee" />
            <h2 style={{ margin: 0, fontSize: 22, fontWeight: 700 }}>Ingestion Monitor</h2>
          </div>
          <p style={{ color: '#94a3b8', margin: 0, fontSize: 14 }}>
            Live status of all regulatory data sources and scheduled syncs.
          </p>
        </div>
        <button
          onClick={load}
          style={{
            background: '#1e293b',
            border: '1px solid #334155',
            borderRadius: 8,
            color: '#94a3b8',
            padding: '8px 16px',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: 6,
            fontSize: 13,
          }}
        >
          <RefreshCw size={14} />
          Refresh
        </button>
      </div>

      {/* Top stats */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 16, marginBottom: 24 }}>
        <StatCard
          label="Total Regulations"
          value={data?.total_regulations?.toLocaleString()}
          icon={Database}
          color="#60a5fa"
        />
        <StatCard
          label="Active Sources"
          value={data?.sources?.filter(s => s.healthy).length + ' / ' + data?.sources?.length}
          sub={data?.sources?.some(s => !s.healthy) ? 'Some sources degraded' : 'All healthy'}
          icon={CheckCircle}
          color={data?.sources?.some(s => !s.healthy) ? '#f59e0b' : '#22c55e'}
        />
        <StatCard
          label="Scheduler"
          value={data?.scheduler_active ? 'Active' : 'Inactive'}
          sub={data?.next_scheduled_sync
            ? `Next: ${new Date(data.next_scheduled_sync).toLocaleString()}`
            : 'No job scheduled'}
          icon={Clock}
          color={data?.scheduler_active ? '#22c55e' : '#ef4444'}
        />
      </div>

      {/* Vertical breakdown */}
      <div style={card}>
        <div style={{ fontSize: 12, color: '#64748b', textTransform: 'uppercase', letterSpacing: 1, marginBottom: 14 }}>
          Regulations by Vertical
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
          {Object.entries(verticals).sort((a, b) => b[1] - a[1]).map(([v, count]) => (
            <div key={v} style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
              <div style={{ width: 90, fontSize: 13, color: '#cbd5e1', textTransform: 'capitalize' }}>{v}</div>
              <div style={{ flex: 1, background: '#0f172a', borderRadius: 4, height: 10, overflow: 'hidden' }}>
                <div style={{
                  height: '100%',
                  width: `${totalVerticalRegs ? (count / totalVerticalRegs) * 100 : 0}%`,
                  background: 'linear-gradient(90deg, #3b82f6, #818cf8)',
                  borderRadius: 4,
                }} />
              </div>
              <div style={{ width: 40, textAlign: 'right', fontSize: 13, color: '#94a3b8' }}>{count}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Sources table */}
      <div style={card}>
        <div style={{ fontSize: 12, color: '#64748b', textTransform: 'uppercase', letterSpacing: 1, marginBottom: 14 }}>
          Source Status
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
          {data?.sources?.map(s => (
            <div key={s.abbreviation} style={{
              display: 'flex',
              alignItems: 'center',
              gap: 16,
              background: '#0f172a',
              borderRadius: 8,
              padding: '12px 16px',
              flexWrap: 'wrap',
            }}>
              {/* Status indicator */}
              <div style={{
                width: 8, height: 8, borderRadius: '50%',
                background: s.healthy ? '#22c55e' : '#ef4444',
                flexShrink: 0,
              }} />

              {/* Name */}
              <div style={{ flex: 1, minWidth: 120 }}>
                <div style={{ fontWeight: 600, fontSize: 14 }}>{s.name}</div>
                <div style={{ color: '#64748b', fontSize: 12 }}>{s.abbreviation}</div>
              </div>

              {/* Stats */}
              <div style={{ textAlign: 'right', minWidth: 80 }}>
                <div style={{ fontSize: 16, fontWeight: 700, color: '#60a5fa' }}>{s.regulation_count}</div>
                <div style={{ color: '#64748b', fontSize: 11 }}>regulations</div>
              </div>

              <div style={{ textAlign: 'right', minWidth: 140 }}>
                <div style={{ fontSize: 12, color: '#94a3b8' }}>
                  {s.last_sync ? new Date(s.last_sync).toLocaleString() : 'Never synced'}
                </div>
                <div style={{ fontSize: 11, color: '#64748b' }}>last sync</div>
              </div>

              {/* Manual sync button */}
              <button
                onClick={() => triggerSync(s.abbreviation?.toLowerCase())}
                disabled={!!syncing}
                style={{
                  background: syncing === s.abbreviation?.toLowerCase() ? '#312e81' : '#1e3a5f',
                  border: '1px solid #334155',
                  borderRadius: 6,
                  color: '#93c5fd',
                  padding: '6px 12px',
                  cursor: syncing ? 'wait' : 'pointer',
                  fontSize: 12,
                  display: 'flex',
                  alignItems: 'center',
                  gap: 5,
                  opacity: syncing && syncing !== s.abbreviation?.toLowerCase() ? 0.5 : 1,
                }}
              >
                {syncing === s.abbreviation?.toLowerCase()
                  ? <><RefreshCw size={12} style={{ animation: 'spin 1s linear infinite' }} /> Syncing...</>
                  : <><Zap size={12} /> Sync now</>
                }
              </button>
            </div>
          ))}
        </div>

        {/* Sync result */}
        {syncResult && (
          <div style={{
            marginTop: 14,
            padding: '10px 14px',
            borderRadius: 8,
            background: syncResult.status === 'ok' ? '#14532d' : '#7f1d1d',
            color: syncResult.status === 'ok' ? '#86efac' : '#fca5a5',
            fontSize: 13,
          }}>
            {syncResult.status === 'ok'
              ? `Sync complete — new: ${syncResult.stats?.new ?? 0}, updated: ${syncResult.stats?.updated ?? 0}, skipped: ${syncResult.stats?.skipped ?? 0}`
              : `Sync failed: ${syncResult.error || syncResult.detail}`
            }
          </div>
        )}
      </div>

      {/* Recent ingestion activity */}
      {data?.recent_updates?.length > 0 && (
        <div style={card}>
          <div style={{ fontSize: 12, color: '#64748b', textTransform: 'uppercase', letterSpacing: 1, marginBottom: 14 }}>
            Recent Ingestion Activity
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {data.recent_updates.slice(0, 10).map((u, i) => {
              const c = URGENCY_COLORS[u.urgency] || URGENCY_COLORS.medium
              return (
                <div key={i} style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 12,
                  padding: '8px 12px',
                  background: '#0f172a',
                  borderRadius: 6,
                }}>
                  <div style={{ width: 6, height: 6, borderRadius: '50%', background: c.dot, flexShrink: 0 }} />
                  <div style={{ flex: 1, fontSize: 13, color: '#cbd5e1', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                    {u.title}
                  </div>
                  <div style={{
                    padding: '2px 8px',
                    borderRadius: 10,
                    background: c.bg,
                    color: c.text,
                    fontSize: 11,
                    fontWeight: 600,
                    flexShrink: 0,
                  }}>
                    {u.urgency}
                  </div>
                  <div style={{ color: '#475569', fontSize: 11, flexShrink: 0, minWidth: 120, textAlign: 'right' }}>
                    {u.detected_at ? new Date(u.detected_at).toLocaleString() : ''}
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      )}

      <style>{`
        @keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
      `}</style>
    </div>
  )
}
