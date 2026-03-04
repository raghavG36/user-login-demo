/**
 * API client for FastAPI backend.
 * Uses VITE_API_URL in production; in dev, use relative /api (Vite proxy).
 */
const getBaseUrl = () => {
  if (import.meta.env.VITE_API_URL) return import.meta.env.VITE_API_URL.replace(/\/$/, '')
  return '/api'
}

const baseUrl = getBaseUrl()

function getToken() {
  return localStorage.getItem('token')
}

function getHeaders(includeAuth = false) {
  const headers = { 'Content-Type': 'application/json' }
  if (includeAuth) {
    const token = getToken()
    if (token) headers['Authorization'] = `Bearer ${token}`
  }
  return headers
}

async function handleResponse(res) {
  const data = await res.json().catch(() => ({}))
  if (!res.ok) {
    const err = new Error(data.detail || res.statusText || 'Request failed')
    err.status = res.status
    err.data = data
    throw err
  }
  return data
}

// Auth
export async function register({ email, username, password }) {
  const res = await fetch(`${baseUrl}/auth/register`, {
    method: 'POST',
    headers: getHeaders(),
    body: JSON.stringify({ email, username, password }),
  })
  return handleResponse(res)
}

export async function login(username, password) {
  const form = new URLSearchParams({ username, password })
  const res = await fetch(`${baseUrl}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: form,
  })
  return handleResponse(res)
}

export async function getMe() {
  const res = await fetch(`${baseUrl}/auth/me`, {
    headers: getHeaders(true),
  })
  return handleResponse(res)
}

// Calculator (requires auth)
export async function calculatorOp(operation, a, b) {
  const res = await fetch(`${baseUrl}/calculator/${operation}`, {
    method: 'POST',
    headers: getHeaders(true),
    body: JSON.stringify({ a: Number(a), b: Number(b) }),
  })
  return handleResponse(res)
}
