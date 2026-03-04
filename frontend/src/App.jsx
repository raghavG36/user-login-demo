import { Navigate, Route, Routes, Link, useLocation } from 'react-router-dom'
import { useAuth } from './context/AuthContext'
import Login from './pages/Login'
import Register from './pages/Register'
import Calculator from './pages/Calculator'
import ActionsPerformed from './pages/ActionsPerformed'

function Layout({ children }) {
  const { isAuthenticated, user, logout } = useAuth()
  const location = useLocation()

  return (
    <>
      <nav className="nav">
        <Link to="/">Calculator</Link>
        <Link to="/actions" className={location.pathname === '/actions' ? 'active' : ''}>
          Actions Performed
        </Link>
        <span className="spacer" />
        {isAuthenticated ? (
          <>
            <span style={{ color: 'var(--muted)', fontSize: '0.9rem' }}>{user?.username}</span>
            <button type="button" className="btn btn-secondary" onClick={logout}>
              Logout
            </button>
          </>
        ) : (
          <>
            <Link to="/login" className={location.pathname === '/login' ? 'active' : ''}>Login</Link>
            <Link to="/register" className={location.pathname === '/register' ? 'active' : ''}>Register</Link>
          </>
        )}
      </nav>
      <main className="container">{children}</main>
    </>
  )
}

function ProtectedRoute({ children }) {
  const { isAuthenticated, loading } = useAuth()
  if (loading) return <div className="container">Loading...</div>
  if (!isAuthenticated) return <Navigate to="/login" replace />
  return children
}

function PublicOnlyRoute({ children }) {
  const { isAuthenticated, loading } = useAuth()
  if (loading) return <div className="container">Loading...</div>
  if (isAuthenticated) return <Navigate to="/" replace />
  return children
}

export default function App() {
  return (
    <Routes>
      <Route
        path="/"
        element={
          <Layout>
            <ProtectedRoute>
              <Calculator />
            </ProtectedRoute>
          </Layout>
        }
      />
      <Route
        path="/actions"
        element={
          <Layout>
            <ProtectedRoute>
              <ActionsPerformed />
            </ProtectedRoute>
          </Layout>
        }
      />
      <Route
        path="/login"
        element={
          <Layout>
            <PublicOnlyRoute>
              <Login />
            </PublicOnlyRoute>
          </Layout>
        }
      />
      <Route
        path="/register"
        element={
          <Layout>
            <PublicOnlyRoute>
              <Register />
            </PublicOnlyRoute>
          </Layout>
        }
      />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
