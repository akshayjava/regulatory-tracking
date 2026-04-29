import React, { useRef, useState } from 'react'
import { Bot, Send, Loader, AlertCircle } from 'lucide-react'

const VERTICALS = ['all', 'crypto', 'fintech', 'healthcare', 'insurance', 'saas']

const SUGGESTED = [
  'What are the most critical compliance deadlines in the next 30 days?',
  'Summarize the key fintech regulations I need to know about.',
  'What crypto regulations are currently proposed or pending?',
  'Which healthcare regulations have the highest impact score?',
  'What are the main compliance requirements for SaaS companies?',
]

export default function AIQuery({ apiBase }) {
  const [question, setQuestion] = useState('')
  const [vertical, setVertical] = useState('all')
  const [answer, setAnswer] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const answerRef = useRef(null)

  async function submit(q) {
    const text = (q || question).trim()
    if (!text) return

    setLoading(true)
    setAnswer('')
    setError(null)

    try {
      const body = {
        question: text,
        stream: true,
        ...(vertical !== 'all' && { vertical }),
      }

      const resp = await fetch(`${apiBase}/ai/query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      })

      if (!resp.ok) {
        const err = await resp.json().catch(() => ({ detail: resp.statusText }))
        throw new Error(err.detail || 'Query failed')
      }

      const reader = resp.body.getReader()
      const decoder = new TextDecoder()
      let full = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        const chunk = decoder.decode(value, { stream: true })
        full += chunk
        setAnswer(full)
        // Auto-scroll
        if (answerRef.current) {
          answerRef.current.scrollTop = answerRef.current.scrollHeight
        }
      }
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  const card = {
    background: '#1e293b',
    border: '1px solid #334155',
    borderRadius: 12,
    padding: 20,
    marginBottom: 16,
  }

  return (
    <div>
      {/* Header */}
      <div style={{ marginBottom: 24 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 6 }}>
          <Bot size={24} color="#818cf8" />
          <h2 style={{ margin: 0, fontSize: 22, fontWeight: 700 }}>Ask AI</h2>
        </div>
        <p style={{ color: '#94a3b8', margin: 0, fontSize: 14 }}>
          Ask natural language questions about regulations. Powered by Claude.
        </p>
      </div>

      {/* Input area */}
      <div style={card}>
        {/* Vertical filter */}
        <div style={{ display: 'flex', gap: 8, marginBottom: 12, flexWrap: 'wrap' }}>
          {VERTICALS.map(v => (
            <button
              key={v}
              onClick={() => setVertical(v)}
              onFocus={e => e.target.style.boxShadow = '0 0 0 2px #818cf8'}
              onBlur={e => e.target.style.boxShadow = 'none'}
              style={{
                padding: '4px 12px',
                borderRadius: 20,
                border: '1px solid',
                borderColor: vertical === v ? '#818cf8' : '#334155',
                background: vertical === v ? '#312e81' : 'transparent',
                color: vertical === v ? '#c7d2fe' : '#94a3b8',
                cursor: 'pointer',
                fontSize: 13,
                fontWeight: 500,
              }}
            >
              {v === 'all' ? 'All verticals' : v.charAt(0).toUpperCase() + v.slice(1)}
            </button>
          ))}
        </div>

        {/* Text input */}
        <div style={{ display: 'flex', gap: 10 }}>
          <textarea
            value={question}
            onChange={e => setQuestion(e.target.value)}
            onFocus={e => { e.target.style.boxShadow = '0 0 0 2px #818cf8'; e.target.style.borderColor = '#818cf8' }}
            onBlur={e => { e.target.style.boxShadow = 'none'; e.target.style.borderColor = '#334155' }}
            onKeyDown={e => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault()
                submit()
              }
            }}
            placeholder="Ask about regulations, compliance requirements, deadlines..."
            rows={3}
            style={{
              flex: 1,
              background: '#0f172a',
              border: '1px solid #334155',
              borderRadius: 8,
              color: 'white',
              padding: '10px 14px',
              fontSize: 14,
              resize: 'none',
              outline: 'none',
            }}
          />
          <button
            onClick={() => submit()}
            disabled={loading || !question.trim()}
            onFocus={e => e.target.style.boxShadow = '0 0 0 2px #818cf8'}
            onBlur={e => e.target.style.boxShadow = 'none'}
            style={{
              padding: '0 20px',
              background: loading || !question.trim() ? '#1e3a5f' : '#1d4ed8',
              border: 'none',
              borderRadius: 8,
              color: 'white',
              cursor: loading || !question.trim() ? 'not-allowed' : 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: 6,
              fontSize: 14,
              fontWeight: 600,
              opacity: loading || !question.trim() ? 0.6 : 1,
            }}
          >
            {loading ? <Loader size={16} style={{ animation: 'spin 1s linear infinite' }} /> : <Send size={16} />}
            {loading ? 'Thinking...' : 'Ask'}
          </button>
        </div>
      </div>

      {/* Suggested questions */}
      {!answer && !loading && (
        <div style={card}>
          <div style={{ fontSize: 12, color: '#64748b', marginBottom: 10, textTransform: 'uppercase', letterSpacing: 1 }}>
            Suggested questions
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {SUGGESTED.map((s, i) => (
              <button
                key={i}
                onClick={() => { setQuestion(s); submit(s) }}
                style={{
                  textAlign: 'left',
                  background: '#0f172a',
                  border: '1px solid #334155',
                  borderRadius: 8,
                  color: '#94a3b8',
                  padding: '8px 14px',
                  cursor: 'pointer',
                  fontSize: 13,
                  transition: 'all 0.15s',
                }}
                onMouseEnter={e => { e.target.style.borderColor = '#818cf8'; e.target.style.color = '#c7d2fe' }}
                onMouseLeave={e => { e.target.style.borderColor = '#334155'; e.target.style.color = '#94a3b8' }}
                onFocus={e => { e.target.style.borderColor = '#818cf8'; e.target.style.color = '#c7d2fe'; e.target.style.boxShadow = '0 0 0 2px #818cf8' }}
                onBlur={e => { e.target.style.borderColor = '#334155'; e.target.style.color = '#94a3b8'; e.target.style.boxShadow = 'none' }}
              >
                {s}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Error */}
      {error && (
        <div style={{ ...card, borderColor: '#7f1d1d', background: '#1c0a0a', display: 'flex', gap: 10, alignItems: 'flex-start' }}>
          <AlertCircle size={18} color="#ef4444" style={{ flexShrink: 0, marginTop: 2 }} />
          <div>
            <div style={{ color: '#fca5a5', fontWeight: 600, marginBottom: 4 }}>Query failed</div>
            <div style={{ color: '#f87171', fontSize: 13 }}>{error}</div>
            {error.includes('ANTHROPIC_API_KEY') && (
              <div style={{ color: '#94a3b8', fontSize: 12, marginTop: 8 }}>
                Set the <code style={{ color: '#818cf8' }}>ANTHROPIC_API_KEY</code> environment variable before starting the backend.
              </div>
            )}
          </div>
        </div>
      )}

      {/* Answer */}
      {(answer || loading) && (
        <div style={card}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 14 }}>
            <Bot size={16} color="#818cf8" />
            <span style={{ fontSize: 13, color: '#818cf8', fontWeight: 600 }}>
              Claude {loading ? '(typing...)' : '(claude-opus-4-6)'}
            </span>
          </div>
          <div
            ref={answerRef}
            style={{
              color: '#e2e8f0',
              fontSize: 14,
              lineHeight: 1.7,
              whiteSpace: 'pre-wrap',
              maxHeight: 600,
              overflowY: 'auto',
            }}
          >
            {answer}
            {loading && <span style={{ opacity: 0.5 }}>▌</span>}
          </div>
        </div>
      )}

      <style>{`
        @keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
      `}</style>
    </div>
  )
}
