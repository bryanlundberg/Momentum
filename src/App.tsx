import { useState, useEffect, useCallback } from 'react'

// 1. Paste your Lambda Function URL here (ends in .lambda-url.<region>.on.aws/)
//    You can also put it in a .env file as VITE_LAMBDA_URL and it will be used automatically.
const LAMBDA_URL =
  import.meta.env.VITE_LAMBDA_URL ||
  'https://YOUR-FUNCTION-URL.lambda-url.us-east-1.on.aws/'

const FALLBACK = 'Start small, but start today.'

function App() {
  const [message, setMessage] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const date = new Date().toLocaleDateString('en-US', {
    weekday: 'long',
    day: 'numeric',
    month: 'long',
    year: 'numeric',
  })

  const generate = useCallback(async () => {
    setLoading(true)
    setError('')
    try {
      const res = await fetch(LAMBDA_URL, { method: 'GET' })
      if (!res.ok) throw new Error('HTTP ' + res.status)
      const data = await res.json()
      setMessage(data.message || FALLBACK)
    } catch (e) {
      setError('Could not reach the Lambda.')
      setMessage(FALLBACK)
    } finally {
      setLoading(false)
    }
  }, [])

  // Generate the pill when the page loads.
  useEffect(() => {
    generate()
  }, [generate])

  return (
    <main style={styles.page}>
      <div style={styles.card}>
        <p style={styles.date}>{date}</p>
        <h1 style={styles.title}>Daily Pill</h1>

        <div style={styles.quoteBox}>
          <span style={styles.label}>Your dose for today</span>
          <p style={{ ...styles.quote, opacity: loading ? 0.5 : 1 }}>
            {loading ? 'Generating your message...' : message}
          </p>
        </div>

        <button
          type="button"
          style={{ ...styles.btn, opacity: loading ? 0.6 : 1 }}
          onClick={generate}
          disabled={loading}
        >
          {loading ? '...' : 'New pill'}
        </button>

        {error && <p style={styles.error}>{error}</p>}
      </div>
    </main>
  )
}

const styles: Record<string, React.CSSProperties> = {
  page: {
    minHeight: '100vh',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    background: '#0f0f1a',
    padding: 20,
    fontFamily:
      '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
  },
  card: {
    width: '100%',
    maxWidth: 480,
    background: '#1a1a2e',
    borderRadius: 24,
    padding: '36px 30px',
    boxShadow: '0 20px 50px rgba(0,0,0,.4)',
    textAlign: 'center',
    color: '#fff',
  },
  date: {
    textTransform: 'capitalize',
    color: '#9ca3af',
    fontSize: 14,
    margin: 0,
  },
  title: { fontSize: 26, margin: '6px 0 26px' },
  quoteBox: {
    background: 'linear-gradient(135deg,#4f46e5,#7c3aed)',
    borderRadius: 18,
    padding: '30px 24px',
    minHeight: 150,
    display: 'flex',
    flexDirection: 'column',
    justifyContent: 'center',
  },
  label: {
    fontSize: 11,
    letterSpacing: 2,
    textTransform: 'uppercase',
    opacity: 0.8,
    marginBottom: 12,
  },
  quote: { fontSize: 22, lineHeight: 1.4, fontWeight: 600, margin: 0 },
  btn: {
    marginTop: 22,
    width: '100%',
    border: 'none',
    borderRadius: 12,
    padding: '14px 20px',
    fontSize: 15,
    fontWeight: 600,
    color: '#fff',
    background: '#7c3aed',
    cursor: 'pointer',
  },
  error: { color: '#f87171', fontSize: 13, marginTop: 14 },
}

export default App
