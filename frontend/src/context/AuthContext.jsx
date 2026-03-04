import { createContext, useCallback, useContext, useEffect, useState } from 'react'
import * as api from '../api/client'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [token, setTokenState] = useState(() => localStorage.getItem('token'))
  const [loading, setLoading] = useState(true)

  const setToken = useCallback((newToken) => {
    if (newToken) {
      localStorage.setItem('token', newToken)
      setTokenState(newToken)
    } else {
      localStorage.removeItem('token')
      setTokenState(null)
      setUser(null)
    }
  }, [])

  useEffect(() => {
    if (!token) {
      setUser(null)
      setLoading(false)
      return
    }
    api.getMe()
      .then(setUser)
      .catch(() => setToken(null))
      .finally(() => setLoading(false))
  }, [token, setToken])

  const login = useCallback(async (username, password) => {
    const data = await api.login(username, password)
    setToken(data.access_token)
    const me = await api.getMe()
    setUser(me)
    return me
  }, [setToken])

  const logout = useCallback(() => {
    setToken(null)
  }, [setToken])

  const value = {
    user,
    token,
    loading,
    login,
    logout,
    setToken,
    isAuthenticated: !!token,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
