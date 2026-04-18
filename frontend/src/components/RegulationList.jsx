import React, { useCallback, useEffect, useRef, useState } from 'react'
import { AlertCircle, CheckCircle, Clock, Download, Search, Zap } from 'lucide-react'

const VERTICALS = ['all', 'crypto', 'fintech', 'healthcare', 'insurance', 'saas']
const STATUSES = ['all', 'proposed', 'final', 'effective']

const STATUS_COLORS = {
  effective: { bg: '#166534', text: '#4ade80' },
  final: { bg: '#1e3a5f', text: '#60a5fa' },
  proposed: { bg: '#78350f', text: '#fbbf24' },
}

function UrgencyIcon({ deadline }) {
  if (!deadline) return null
  const days = Math.ceil((new Date(deadline) - new Date()) / 86400000)
  if (days <= 30) return <AlertCircle size={16} color="#ef4444" />
  if (days <= 90) return <Clock size={16} color="#f59e0b" />
  return <CheckCircle size={16} color="#4ade80" />
}

function useDebounce(value, delay) {
  const [debounced, setDebounced] = useState(value)
  useEffect(() => {
    const t = setTimeout(() => setDebounced(value), delay)
    return () => clearTimeout(t)
  }, [value, delay])
  return debounced
}

export default function RegulationList({ apiBase }) {
  const [vertical, setVertical] = useState('all')
  const [status, setStatus] = useState('all')
  const [search, setSearch] = useState('')
  const [page, setPage] = useState(1)
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(false)
  const debouncedSearch = useDebounce(search, 300)

  useEffect(() => { setPage(1) }, [vertical, status, debouncedSearch])

  useEffect(() => {
    setLoading(true)
    const params = new URLSearchParams({ page, page_size: 20 })
    if (vertical !== 'all') params.set('vertical', vertical)
    if (status !== 'all') params.set('status', status)
    if (debouncedSearch) params.set('search', debouncedSearch)

    fetch(`${apiBase}/regulations?${params}`)
      .then(r => r.json())
      .then(d => { setData(d); setLoading(false) })
      .catch(() => setLoading(false))
  }, [apiBase, vertical, status, debouncedSearch, page])

  const exportCSV = () => {
    const params = new URLSearchParams({ page: 1, page_size: 100 })
    if (vertical !== 'all') params.set('vertical', vertical)
    if (status !== 'all') params.set('status', status)
    if (debouncedSearch) params.set('search', debouncedSearch)

    fetch(`${apiBase}/regulations?${params}`)
      .then(r => r.json())
      .then(({ items }) => {
        const headers = ['regulation_id', 'title', 'status', 'type', 'source', 'published_date', 'deadline_date', 'impact_score', 'complexity_score']
        const rows = items.map(r => headers.map(h => JSON.stringify(r[h] ?? '')).join(','))
        const csv = [headers.join(','), ...rows].join('\n')
        const blob = new Blob([csv], { type: 'text/csv' })
        const a = document.createElement('a'); a.href = URL.createObjectURL(blob)
        a.download = `lattice_${vertical}_${status}.csv`; a.click()
      })
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
      {/* Vertical Tabs */}
      <div style={{ background: '#1e293b', border: '1px solid #334155', borderRadius: 10, padding: 20 }}>
        <div style={{ fontSize: 14, color: '#94a3b8', marginBottom: 12 }}>Filter by Vertical</div>
        <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
          {VERTICALS.map(v => (
            <button key={v} onClick={() => setVertical(v)} style={{
              padding: '6px 16px', borderRadius: 6, border: 'none', cursor: 'pointer',
              background: vertical === v ? '#2563eb' : '#334155',
              color: vertical === v ? 'white' : '#94a3b8',
              fontWeight: 600, textTransform: 'capitalize', fontSize: 13,
            }}>{v}</button>
          ))}
        </div>
      </div>

      {/* Search + Status Filter */}
      <div style={{ background: '#1e293b', border: '1px solid #334155', borderRadius: 10, padding: 16, display: 'flex', gap: 12 }}>
        <div style={{ flex: 1, position: 'relative' }}>
          <Search size={16} style={{ position: 'absolute', left: 12, top: 10, color: '#64748b' }} />
          <input
            value={search}
            onChange={e => setSearch(e.target.value)}
            placeholder="Search regulations by title or keyword..."
            style={{
              width: '100%', background: '#334155', border: '1px solid #475569', borderRadius: 6,
              padding: '8px 12px 8px 36px', color: 'white', fontSize: 14, outline: 'none',
            }}
          />
        </div>
        <select value={status} onChange={e => setStatus(e.target.value)} style={{
          background: '#334155', border: '1px solid #475569', borderRadius: 6,
          padding: '8px 12px', color: 'white', fontSize: 13, cursor: 'pointer',
        }}>
          {STATUSES.map(s => <option key={s} value={s}>{s === 'all' ? 'All Statuses' : s.charAt(0).toUpperCase() + s.slice(1)}</option>)}
        </select>
        <button onClick={exportCSV} style={{
          background: '#2563eb', border: 'none', borderRadius: 6, padding: '8px 16px',
          color: 'white', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 6, fontSize: 13, fontWeight: 600,
        }}>
          <Download size={15} /> Export
        </button>
      </div>

      {/* Results */}
      <div style={{ background: '#1e293b', border: '1px solid #334155', borderRadius: 10, padding: 24 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
          <h2 style={{ margin: 0, fontSize: 16, fontWeight: 600 }}>
            {data ? `${data.total} Regulations` : 'Loading...'}
          </h2>
          {data && <span style={{ fontSize: 12, color: '#64748b' }}>Page {page} of {data.total_pages}</span>}
        </div>

        {loading && <div style={{ textAlign: 'center', padding: 40, color: '#64748b' }}>Loading...</div>}

        {!loading && data?.items?.length === 0 && (
          <div style={{ textAlign: 'center', padding: 40, color: '#64748b' }}>No regulations found</div>
        )}

        <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
          {(data?.items || []).map(reg => (
            <div key={reg.regulation_id} style={{
              background: 'rgba(51,65,85,0.4)', border: '1px solid #334155', borderRadius: 8,
              padding: 16, transition: 'background 0.15s',
            }}
              onMouseEnter={e => e.currentTarget.style.background = 'rgba(51,65,85,0.7)'}
              onMouseLeave={e => e.currentTarget.style.background = 'rgba(51,65,85,0.4)'}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6 }}>
                <h3 style={{ margin: 0, fontSize: 14, fontWeight: 600, color: '#60a5fa' }}>{reg.title}</h3>
                <UrgencyIcon deadline={reg.deadline_date} />
              </div>
              <p style={{ margin: '0 0 10px', fontSize: 13, color: '#94a3b8', lineHeight: 1.5 }}>{reg.summary}</p>

              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, alignItems: 'center' }}>
                {reg.status && (
                  <span style={{
                    fontSize: 11, padding: '2px 8px', borderRadius: 4, fontWeight: 600,
                    background: STATUS_COLORS[reg.status]?.bg || '#334155',
                    color: STATUS_COLORS[reg.status]?.text || '#94a3b8',
                  }}>{reg.status}</span>
                )}
                {reg.type && <span style={{ fontSize: 11, padding: '2px 8px', borderRadius: 4, background: '#334155', color: '#94a3b8' }}>{reg.type}</span>}
                {reg.source && <span style={{ fontSize: 11, padding: '2px 8px', borderRadius: 4, background: '#334155', color: '#94a3b8' }}>{reg.source.replace('_', ' ')}</span>}
                {reg.verticals?.map(v => (
                  <span key={v.vertical} style={{ fontSize: 11, padding: '2px 8px', borderRadius: 4, background: '#1d4ed8', color: '#93c5fd' }}>{v.vertical}</span>
                ))}
                {reg.impact_score && (
                  <span style={{ fontSize: 11, padding: '2px 8px', borderRadius: 4, background: '#334155', color: '#94a3b8', display: 'flex', alignItems: 'center', gap: 4 }}>
                    <Zap size={10} /> Impact {reg.impact_score}/10
                  </span>
                )}
              </div>
              {reg.deadline_date && (
                <div style={{ marginTop: 8, fontSize: 12, color: '#94a3b8' }}>
                  ⏰ Deadline: {new Date(reg.deadline_date).toLocaleDateString()}
                  {reg.citation && <span style={{ marginLeft: 16 }}>📄 {reg.citation}</span>}
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Pagination */}
        {data && data.total_pages > 1 && (
          <div style={{ display: 'flex', justifyContent: 'center', gap: 12, marginTop: 20 }}>
            <button
              onClick={() => setPage(p => Math.max(1, p - 1))}
              disabled={page === 1}
              style={{ padding: '6px 16px', borderRadius: 6, border: '1px solid #334155', background: '#334155', color: page === 1 ? '#475569' : 'white', cursor: page === 1 ? 'default' : 'pointer' }}
            >← Prev</button>
            <span style={{ padding: '6px 0', color: '#94a3b8', fontSize: 13 }}>{page} / {data.total_pages}</span>
            <button
              onClick={() => setPage(p => Math.min(data.total_pages, p + 1))}
              disabled={page === data.total_pages}
              style={{ padding: '6px 16px', borderRadius: 6, border: '1px solid #334155', background: '#334155', color: page === data.total_pages ? '#475569' : 'white', cursor: page === data.total_pages ? 'default' : 'pointer' }}
            >Next →</button>
          </div>
        )}
      </div>
    </div>
  )
}
