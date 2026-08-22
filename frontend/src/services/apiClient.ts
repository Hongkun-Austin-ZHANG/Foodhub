const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? '/api'
const TOKEN_KEY = 'foodhub_access_token'

export class ApiError extends Error {
  status: number

  constructor(status: number, message: string) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}

export function getAccessToken() {
  return window.localStorage.getItem(TOKEN_KEY)
}

export function setAccessToken(token: string) {
  window.localStorage.setItem(TOKEN_KEY, token)
}

export function clearAccessToken() {
  window.localStorage.removeItem(TOKEN_KEY)
}

function errorMessage(body: unknown, status: number) {
  if (typeof body === 'object' && body !== null && 'detail' in body) {
    const detail = (body as { detail: unknown }).detail
    if (typeof detail === 'string') return detail
    if (Array.isArray(detail)) {
      return detail
        .map((item) => {
          if (typeof item !== 'object' || item === null) return String(item)
          const typed = item as { loc?: unknown[]; msg?: string }
          const location = typed.loc?.slice(1).join('.')
          return location ? `${location}: ${typed.msg}` : typed.msg
        })
        .filter(Boolean)
        .join('; ')
    }
  }
  return `Request failed (${status})`
}

export async function apiRequest<T>(
  path: string,
  init: RequestInit = {},
  authenticated = true,
): Promise<T> {
  const headers = new Headers(init.headers)
  if (!(init.body instanceof FormData) && init.body !== undefined) {
    headers.set('Content-Type', 'application/json')
  }
  if (authenticated) {
    const token = getAccessToken()
    if (!token) throw new ApiError(401, 'Please log in first.')
    headers.set('Authorization', `Bearer ${token}`)
  }

  const response = await fetch(`${API_BASE_URL}${path}`, { ...init, headers })
  if (!response.ok) {
    let body: unknown
    try {
      body = await response.json()
    } catch {
      body = null
    }
    if (response.status === 401) clearAccessToken()
    throw new ApiError(response.status, errorMessage(body, response.status))
  }
  if (response.status === 204) return undefined as T
  return response.json() as Promise<T>
}
