import React, { useCallback, useEffect, useRef, useState } from 'react'
import { AlertCircle, Bot, CheckCircle, Clock, Download, Search, Zap } from 'lucide-react'

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

function AIAnnotation({ apiBase, regulationId }) {
  const [annotation, setAnnotation] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  async function load() {
    setLoading(true)
    setError(null)
    try {
      // Try cache first
      const resp = await fetch(`${apiBase}/ai/annotation/${regulationId}`)
      if (resp.ok) {
        const d = await resp.json()
        setAnnotation(d)
      } else if (resp.status === 404) {
        // Generate new annotation
        const gen = await fetch(`${apiBase}/ai/annotate/${regulationId}`, { method: 'POST' })
        if (!gen.ok) {
          const e = await gen.json().catch(() => ({ detail: gen.statusText }))
          throw new Error(e.detail || 'Annotation failed')
        }
        setAnnotation(await gen.json())
      } else {
        throw new Error('Failed to load annotation')
      }
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  if (!annotation && !loading && !error) {
    return (
      <button
        onClick={load}
        style={{
          background: 'none',
          border: '1px solid #4f46e5',
          borderRadius: 6,
          color: '#818cf8',
          padding: '4px 10px',
          cursor: 'pointer',
          fontSize: 12,
          display: 'flex',
          alignItems: 'center',
          gap: 4,
        }}
      >
        <Bot size={12} /> AI Explain
      </button>
    )
  }

  if (loading) {
    return (
      <div style={{
        marginTop: 12, padding: '12px 14px',
        background: '#0f172a', borderRadius: 8,
        border: '1px solid #312e81',
        color: '#818cf8', fontSize: 13,
        display: 'flex', alignItems: 'center', gap: 8,
      }}>
        <Bot size={14} style={{ animation: 'pulse 1.5s infinite' }} />
        Claude is reading this regulation...
      </div>
    )
  }

  if (error) {
    return (
      <div style={{
        marginTop: 12, padding: '10px 14px',
        background: '#1c0a0a', borderRadius: 8,
        border: '1px solid #7f1d1d',
        color: '#f87171', fontSize: 12,
      }}>
        {error.includes('ANTHROPIC_API_KEY')
          ? 'Set ANTHROPIC_API_KEY to enable AI annotations.'
          : error}
      </div>
    )
  }

  return (
    <div style={{
      marginTop: 12, padding: '14px 16px',
      background: '#0f172a', borderRadius: 8,
      border: '1px solid #312e81',
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 10 }}>
        <Bot size={14} color="#818cf8" />
        <span style={{ fontSize: 12, color: '#818cf8', fontWeight: 600 }}>
          AI Annotation {annotation?.cached ? '(cached)' : '(just generated)'}
        </span>
      </div>
      <div style={{ color: '#cbd5e1', fontSize: 13, lineHeight: 1.7, whiteSpace: 'pre-wrap' }}>
        {annotation?.annotation}
      </div>
    </div>
  )
}

export default function RegulationList({ apiBase }) {
  const [vertical, setVertical] = useState('all')
  const [status, setStatus] = useState('all')
  const [search, setSearch] = useState('')
  const [page, setPage] = useState(1)
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [expandedAnnotations, setExpandedAnnotations] = useState(new Set())
  const [focusedElement, setFocusedElement] = useState(null)
  const debouncedSearch = useDebounce(search, 300)

  function toggleAnnotation(id) {
    setExpandedAnnotations(prev => {
      const next = new Set(prev)
      if (next.has(id)) next.delete(id)
      else next.add(id)
      return next
    })
  }

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
        <div role="group" aria-label="Filter by vertical" style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
          {VERTICALS.map(v => (
            <button key={v} onClick={() => setVertical(v)} aria-pressed={vertical === v} onFocus={() => setFocusedElement(`vertical-${v}`)} onBlur={() => setFocusedElement(null)} style={{
              padding: '6px 16px', borderRadius: 6, border: 'none', cursor: 'pointer',
              background: vertical === v ? '#2563eb' : '#334155',
              color: vertical === v ? 'white' : '#94a3b8',
              fontWeight: 600, textTransform: 'capitalize', fontSize: 13,
              boxShadow: focusedElement === `vertical-${v}` ? '0 0 0 2px #60a5fa' : 'none',
              transition: 'box-shadow 0.2s ease',
            }}>{v}</button>
          ))}
        </div>
      </div>

      {/* Search + Status Filter */}
      <div style={{ background: '#1e293b', border: '1px solid #334155', borderRadius: 10, padding: 16, display: 'flex', gap: 12 }}>
        <div style={{ flex: 1, position: 'relative' }}>
          <Search size={16} style={{ position: 'absolute', left: 12, top: 10, color: '#64748b' }} />
          <input
            aria-label="Search regulations"
            onFocus={() => setFocusedElement('search')}
            onBlur={() => setFocusedElement(null)}
            value={search}
            onChange={e => setSearch(e.target.value)}
            placeholder="Search regulations by title or keyword..."
            style={{
              width: '100%', background: '#334155', border: '1px solid #475569', borderRadius: 6,
              padding: '8px 12px 8px 36px', color: 'white', fontSize: 14, outline: 'none',
              boxShadow: focusedElement === 'search' ? '0 0 0 2px #60a5fa' : 'none',
              transition: 'box-shadow 0.2s ease',
            }}
          />
        </div>
        <select aria-label="Filter by status" value={status} onChange={e => setStatus(e.target.value)} onFocus={() => setFocusedElement('status')} onBlur={() => setFocusedElement(null)} style={{
          background: '#334155', border: '1px solid #475569', borderRadius: 6,
          padding: '8px 12px', color: 'white', fontSize: 13, cursor: 'pointer',
          outline: 'none',
          boxShadow: focusedElement === 'status' ? '0 0 0 2px #60a5fa' : 'none',
          transition: 'box-shadow 0.2s ease',
        }}>
          {STATUSES.map(s => <option key={s} value={s}>{s === 'all' ? 'All Statuses' : s.charAt(0).toUpperCase() + s.slice(1)}</option>)}
        </select>
        <button aria-label="Export regulations to CSV" onClick={exportCSV} onFocus={() => setFocusedElement('export')} onBlur={() => setFocusedElement(null)} style={{
          background: '#2563eb', border: 'none', borderRadius: 6, padding: '8px 16px',
          color: 'white', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 6, fontSize: 13, fontWeight: 600,
          outline: 'none',
          boxShadow: focusedElement === 'export' ? '0 0 0 2px #60a5fa' : 'none',
          transition: 'box-shadow 0.2s ease',
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
          <div style={{ textAlign: 'center', padding: 60, background: 'rgba(51,65,85,0.2)', borderRadius: 8, border: '1px dashed #475569' }}>
            <div style={{ fontSize: 48, marginBottom: 16 }}>📭</div>
            <h3 style={{ margin: '0 0 8px', color: '#e2e8f0', fontSize: 18, fontWeight: 600 }}>No regulations found</h3>
            <p style={{ margin: '0 0 20px', color: '#94a3b8', fontSize: 14 }}>Try adjusting your search or filters to find what you're looking for.</p>
            {(vertical !== 'all' || status !== 'all' || search !== '') && (
              <button
                onClick={() => { setVertical('all'); setStatus('all'); setSearch(''); }}
                style={{
                  background: '#2563eb', border: 'none', borderRadius: 6, padding: '8px 16px',
                  color: 'white', cursor: 'pointer', fontSize: 14, fontWeight: 500,
                }}
              >
                Clear all filters
              </button>
            )}
          </div>
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

              {/* AI Annotation toggle */}
              <div style={{ marginTop: 10 }}>
                <button
                  onClick={() => toggleAnnotation(reg.regulation_id)}
                  style={{
                    background: 'none',
                    border: '1px solid',
                    borderColor: expandedAnnotations.has(reg.regulation_id) ? '#4f46e5' : '#334155',
                    borderRadius: 6,
                    color: expandedAnnotations.has(reg.regulation_id) ? '#818cf8' : '#64748b',
                    padding: '4px 10px',
                    cursor: 'pointer',
                    fontSize: 12,
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: 4,
                  }}
                >
                  <Bot size={12} />
                  {expandedAnnotations.has(reg.regulation_id) ? 'Hide AI Explanation' : 'AI Explain'}
                </button>
              </div>

              {expandedAnnotations.has(reg.regulation_id) && (
                <AIAnnotation apiBase={apiBase} regulationId={reg.regulation_id} />
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
