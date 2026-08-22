import type { UserPreferenceProfile } from '../types/UserPreferenceProfile'
import { apiRequest } from './apiClient'

export interface UserProfile {
  user_id: string
  display_name: string | null
  gender: string | null
  religion: string | null
  preferred_language: string
  timezone: string
}

export function getProfile() {
  return apiRequest<UserProfile>('/profile')
}

export function updateProfile(payload: Partial<UserProfile>) {
  return apiRequest<UserProfile>('/profile', {
    method: 'PATCH',
    body: JSON.stringify(payload),
  })
}

export function getPreferenceProfile() {
  return apiRequest<UserPreferenceProfile>('/preferences/profile')
}

export function savePreferenceProfile(payload: UserPreferenceProfile) {
  return apiRequest<UserPreferenceProfile>('/preferences/profile', {
    method: 'PUT',
    body: JSON.stringify(payload),
  })
}
