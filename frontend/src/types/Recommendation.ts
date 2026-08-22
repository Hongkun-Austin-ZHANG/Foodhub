import type { CurrentPreference } from './CurrentPreference'
import type { AnalyzedDish } from './MenuDish'

export interface RankedRecommendation extends AnalyzedDish {
  rank: number
  preference_score: number
  matched_preferences: string[]
  preference_tags: {
    proteins: string[]
    flavours: string[]
    textures: string[]
    spice_level: string
  }
}

export interface RecommendationsResponse {
  menu_id: string
  target_language: string
  effective_preferences: unknown[]
  effective_current_preference: CurrentPreference
  recommendations: RankedRecommendation[]
}
