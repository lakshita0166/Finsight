import { Navigate, useLocation } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function ProtectedRoute({ children }) {
  const { user, loading } = useAuth()
  const location = useLocation()

  if (loading) {
    return (
      <div style={{
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        minHeight: '100vh', background: '#1a0404', color: '#f5a8a0',
        fontFamily: 'Jost, sans-serif', fontSize: '0.85rem', letterSpacing: '0.1em',
      }}>
        Loading...
      </div>
    )
  }

  if (!user) {
    // Redirect to landing page with ?login=true so modal auto-opens
    return <Navigate to={`/?login=true`} state={{ from: location }} replace />
  }

  return children
}
