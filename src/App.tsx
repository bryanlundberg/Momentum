import { useState } from 'react'
import type { KeyboardEvent } from 'react'
import './App.css'

const LAMBDA_URL = import.meta.env.VITE_LAMBDA_URL ?? ''

const FALLBACKS = [
  'Start small, but start today.',
  'Done is better than perfect — begin the first line.',
  'One task at a time. That is the whole trick.',
  'Progress lives in action, not intention.',
  'Do it imperfectly, but do it now.',
]

function App() {
  const [task, setTask] = useState('')
  const [answered, setAnswered] = useState('')
  const [message, setMessage] = useState('')
  const [loading, setLoading] = useState(false)
  const [offline, setOffline] = useState(false)
  const [edition, setEdition] = useState(0)

  const date = new Date().toLocaleDateString('en-US', {
    weekday: 'long',
    day: '2-digit',
    month: 'long',
    year: 'numeric',
  })

  async function generate(e?: { preventDefault: () => void }) {
    e?.preventDefault()
    const t = task.trim()
    if (!t || loading) return

    setLoading(true)
    try {
      if (!LAMBDA_URL) throw new Error('no lambda configured')
      const res = await fetch(LAMBDA_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ task: t }),
      })
      if (!res.ok) throw new Error('HTTP ' + res.status)
      const data = await res.json()
      setMessage(data.message?.trim() || pickFallback())
      setOffline(false)
    } catch {
      setMessage(pickFallback())
      setOffline(true)
    } finally {
      setAnswered(t)
      setLoading(false)
      setEdition((n) => n + 1)
    }
  }

  function onKeyDown(e: KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
      e.preventDefault()
      void generate()
    }
  }

  const words = message.split(/\s+/).filter(Boolean)
  const hasQuote = loading || Boolean(message)

  return (
    <div className="paper">
      <div className="grain" aria-hidden="true" />

      <main className="sheet">
        <header className="masthead">
          <div className="brand">
            <Spark />
            <span className="brand-name">Momentum</span>
          </div>
          <p className="tagline">A daily ritual for deep work</p>
          <time className="date">{date}</time>
        </header>

        <div className="rule" aria-hidden="true">
          <span>No. {String(edition).padStart(3, '0')}</span>
          <span>{offline ? 'Local edition' : 'On demand'}</span>
        </div>

        <section className="stage">
          <span className="kicker" aria-hidden="true">
            <em>“</em> Your dose of focus
          </span>

          {hasQuote ? (
            <blockquote
              key={edition}
              className={loading ? 'quote is-loading' : 'quote'}
              aria-live="polite"
            >
              {loading ? (
                <span className="skeleton" aria-hidden="true">
                  <i /> <i /> <i /> <i /> <i /> <i />
                </span>
              ) : (
                words.map((word, i) => (
                  <span
                    className="w"
                    key={`${edition}-${i}`}
                    style={{ animationDelay: `${i * 45}ms` }}
                  >
                    {word}
                  </span>
                ))
              )}
            </blockquote>
          ) : (
            <p className="prompt-empty">
              Tell me what you must do, and I'll hand you the push to start.
            </p>
          )}

          {answered && !loading && (
            <p className="re-task" aria-hidden="true">
              Re:&nbsp;<span>{answered}</span>
            </p>
          )}

          <Seal edition={edition} />
        </section>

        <footer className="deck">
          <form className="composer" onSubmit={(e) => void generate(e)}>
            <label className="composer-label" htmlFor="task">
              What do you have to do?
            </label>
            <div className="composer-row">
              <textarea
                id="task"
                className="composer-input"
                value={task}
                onChange={(e) => setTask(e.target.value)}
                onKeyDown={onKeyDown}
                placeholder="e.g. finish the quarterly report"
                rows={2}
                maxLength={300}
              />
              <button
                type="submit"
                className="draw"
                disabled={loading || !task.trim()}
              >
                <span className="draw-label">
                  {loading ? 'Pouring…' : 'Get momentum'}
                </span>
                <Arrow />
              </button>
            </div>
            <p className="hint">
              {offline
                ? 'No connection to the server — showing a local line.'
                : 'Write one task. Press Get momentum. Then begin the block.'}
            </p>
          </form>
        </footer>
      </main>
    </div>
  )
}

function pickFallback() {
  return FALLBACKS[Math.floor(Math.random() * FALLBACKS.length)]
}

function Spark() {
  return (
    <svg className="spark" viewBox="0 0 32 32" width="26" height="26" aria-hidden="true">
      <path
        d="M16 2c.9 5.6 3.6 8.3 9.2 9.2C19.6 12.1 16.9 14.8 16 20.4 15.1 14.8 12.4 12.1 6.8 11.2 12.4 10.3 15.1 7.6 16 2Z"
        fill="var(--vermillion)"
      />
      <path
        d="M25 22c.4 2.7 1.8 4.1 4.5 4.5C26.8 26.9 25.4 28.3 25 31c-.4-2.7-1.8-4.1-4.5-4.5 2.7-.4 4.1-1.8 4.5-4.5Z"
        fill="var(--blue)"
      />
    </svg>
  )
}

function Arrow() {
  return (
    <svg className="arrow" viewBox="0 0 40 16" width="40" height="16" aria-hidden="true">
      <path
        d="M0 8h36M30 2l7 6-7 6"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  )
}

function Seal({ edition }: { edition: number }) {
  return (
    <svg className="seal" viewBox="0 0 200 200" aria-hidden="true">
      <defs>
        <path
          id="seal-arc"
          d="M100,100 m-74,0 a74,74 0 1,1 148,0 a74,74 0 1,1 -148,0"
        />
      </defs>
      <circle cx="100" cy="100" r="92" fill="none" stroke="var(--ink)" strokeWidth="1.5" />
      <circle cx="100" cy="100" r="60" fill="none" stroke="var(--ink)" strokeWidth="1.5" />
      <text className="seal-text">
        <textPath href="#seal-arc" startOffset="0">
          · DO IT TODAY · NO EXCUSES · ONE BLOCK AT A TIME&nbsp;
        </textPath>
      </text>
      <g className="seal-core">
        <path
          d="M100 74c1.4 8.7 5.6 12.9 14.3 14.3C105.6 89.7 101.4 93.9 100 102.6 98.6 93.9 94.4 89.7 85.7 88.3 94.4 86.9 98.6 82.7 100 74Z"
          fill="var(--vermillion)"
        />
        <text x="100" y="120" className="seal-num">
          {String(edition).padStart(3, '0')}
        </text>
      </g>
    </svg>
  )
}

export default App
