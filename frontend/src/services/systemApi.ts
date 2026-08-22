import { apiRequest } from './apiClient'

export interface Capabilities {
  demo_available: boolean
  live_scan_available: boolean
  supported_languages: string[]
}

export function getCapabilities() {
  return apiRequest<Capabilities>('/capabilities', {}, false)
}
