import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function AuthModal({ mode = 'login', onClose }) {
  const [view, setView]       = useState(mode)   // 'login' | 'signup'
  const [error, setError]     = useState('')
  const [loading, setLoading] = useState(false)
  const { login, signup }     = useAuth()
  const navigate              = useNavigate()

  const [form, setForm] = useState({
    full_name: '', email: '', mobile: '', password: '',
  })

  const set = (field) => (e) => {
    setForm((f) => ({ ...f, [field]: e.target.value }))
    setError('')
  }

  const handleSubmit = async () => {
    setError('')
    setLoading(true)
    try {
      if (view === 'login') {
        await login({ email: form.email, password: form.password })
      } else {
        await signup({
          full_name: form.full_name,
          email:     form.email,
          mobile:    form.mobile,
          password:  form.password,
        })
      }
      onClose()
      navigate('/dashboard')
    } catch (err) {
      const msg = err.response?.data?.detail || 'Something went wrong. Please try again.'
      setError(typeof msg === 'string' ? msg : JSON.stringify(msg))
    } finally {
      setLoading(false)
    }
  }

  const handleKey = (e) => { if (e.key === 'Enter') handleSubmit() }

  return (
    <div className="modal-overlay open" onClick={(e) => e.target === e.currentTarget && onClose()}>
      <div className="modal">
        <button className="modal-close" onClick={onClose}>✕</button>

        <div className="modal-logo">FinSight</div>
        <div className="modal-title">
          {view === 'login' ? 'Welcome back' : 'Create account'}
        </div>
        <div className="modal-sub">
          {view === 'login' ? 'Sign in to your account to continue' : 'Begin your financial journey today'}
        </div>
        <div className="modal-rule"></div>

        {error && (
          <div style={{
            background: 'rgba(232,64,64,0.1)',
            border: '1px solid rgba(232,64,64,0.3)',
            borderRadius: '2px',
            padding: '0.65rem 0.9rem',
            fontSize: '0.8rem',
            color: '#f5a8a0',
            marginBottom: '1rem',
          }}>
            {error}
          </div>
        )}

        {view === 'signup' && (
          <div className="form-group">
            <label>Full name</label>
            <input
              type="text"
              placeholder="Aryan Gaikwad"
              value={form.full_name}
              onChange={set('full_name')}
              onKeyDown={handleKey}
            />
          </div>
        )}

        <div className="form-group">
          <label>Email address</label>
          <input
            type="email"
            placeholder="you@example.com"
            value={form.email}
            onChange={set('email')}
            onKeyDown={handleKey}
          />
        </div>

        {view === 'signup' && (
          <div className="form-group">
            <label>Mobile number</label>
            <input
              type="tel"
              placeholder="+91 98765 43210"
              value={form.mobile}
              onChange={set('mobile')}
              onKeyDown={handleKey}
            />
          </div>
        )}

        <div className="form-group">
          <label>Password</label>
          <input
            type="password"
            placeholder={view === 'signup' ? 'Minimum 8 characters' : '••••••••'}
            value={form.password}
            onChange={set('password')}
            onKeyDown={handleKey}
          />
        </div>

        <button
          className="form-submit"
          onClick={handleSubmit}
          disabled={loading}
          style={{ opacity: loading ? 0.7 : 1, cursor: loading ? 'not-allowed' : 'pointer' }}
        >
          {loading
            ? 'Please wait...'
            : view === 'login' ? 'Sign in to FinSight' : 'Create my account'
          }
        </button>

        <div className="modal-switch">
          {view === 'login' ? (
            <>No account? <a onClick={() => { setView('signup'); setError('') }}>Create one free</a></>
          ) : (
            <>Already registered? <a onClick={() => { setView('login'); setError('') }}>Sign in</a></>
          )}
        </div>
      </div>
    </div>
  )
}
