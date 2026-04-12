import { createContext, useContext, useState, useEffect, useCallback } from 'react'
import { authAPI } from '../services/api'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser]       = useState(null)
  const [loading, setLoading] = useState(true)  // true while checking stored token

  // ── On mount: restore session from localStorage ──────
  useEffect(() => {
    const restore = async () => {
      const token = localStorage.getItem('access_token')
      if (!token) { setLoading(false); return }
      try {
        const { data } = await authAPI.me()
        setUser(data)
      } catch {
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
      } finally {
        setLoading(false)
      }
    }
    restore()
  }, [])

  // ── Signup ────────────────────────────────────────────
  const signup = useCallback(async ({ full_name, email, mobile, password }) => {
    const { data } = await authAPI.signup({ full_name, email, mobile, password })
    localStorage.setItem('access_token',  data.access_token)
    localStorage.setItem('refresh_token', data.refresh_token)
    setUser(data.user)
    return data.user
  }, [])

  // ── Login ─────────────────────────────────────────────
  const login = useCallback(async ({ email, password }) => {
    const { data } = await authAPI.login({ email, password })
    localStorage.setItem('access_token',  data.access_token)
    localStorage.setItem('refresh_token', data.refresh_token)
    setUser(data.user)
    return data.user
  }, [])

  // ── Logout ────────────────────────────────────────────
  const logout = useCallback(async () => {
    try { await authAPI.logout() } catch {}
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    setUser(null)
  }, [])

  return (
    <AuthContext.Provider value={{ user, loading, signup, login, logout, setUser }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used inside AuthProvider')
  return ctx
}
