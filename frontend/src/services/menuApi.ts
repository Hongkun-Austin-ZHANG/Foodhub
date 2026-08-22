import type { MenuScanResponse } from '../types/MenuDish'
import { apiRequest } from './apiClient'

export function scanMenu(menuImages: File[]) {
  const formData = new FormData()
  for (const image of menuImages) formData.append('menu_images', image)
  return apiRequest<MenuScanResponse>('/menu/scan', {
    method: 'POST',
    body: formData,
  })
}

export function loadDemoMenu() {
  return apiRequest<MenuScanResponse>('/menu/demo-scan', { method: 'POST' })
}
