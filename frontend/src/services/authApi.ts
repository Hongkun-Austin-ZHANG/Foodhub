import {
  apiRequest,
  clearAccessToken,
  getAccessToken,
  setAccessToken,
} from './apiClient'

export interface AuthUser {
  id: string
  email: string
  username: string
  is_active: boolean
}

export interface AuthResponse {
  access_token: string
  token_type: 'bearer'
  expires_at: string
  user: AuthUser
}

export interface RegisterPayload {
  name: string
  email: string
  password: string
  preferred_language: string
}

export interface LoginPayload {
  email: string
  password: string
}

function remember(response: AuthResponse) {
  setAccessToken(response.access_token)
  return response
}

export async function register(payload: RegisterPayload) {
  return remember(
    await apiRequest<AuthResponse>(
      '/auth/register',
      { method: 'POST', body: JSON.stringify(payload) },
      false,
    ),
  )
}

export async function login(payload: LoginPayload) {
  return remember(
    await apiRequest<AuthResponse>(
      '/auth/login',
      { method: 'POST', body: JSON.stringify(payload) },
      false,
    ),
  )
}

export async function logout() {
  try {
    await apiRequest<{ logged_out: boolean }>('/auth/logout', { method: 'POST' })
  } finally {
    clearAccessToken()
  }
}

export function isAuthenticated() {
  return Boolean(getAccessToken())
}

export function clearStoredAuthentication() {
  clearAccessToken()
}
