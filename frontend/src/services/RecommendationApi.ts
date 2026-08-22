import type { CurrentPreference } from '../types/CurrentPreference'
import type { RecommendationsResponse } from '../types/Recommendation'
import { apiRequest } from './apiClient'

export function getRecommendations(
  menuId: string,
  currentPreference: CurrentPreference,
) {
  return apiRequest<RecommendationsResponse>('/recommendations', {
    method: 'POST',
    body: JSON.stringify({
      menu_id: menuId,
      current_preference: currentPreference,
    }),
  })
}
