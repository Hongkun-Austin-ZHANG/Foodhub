export type MatchStatus =
  | 'best_match'
  | 'good_match'
  | 'check_with_staff'
  | 'not_suitable'

export type RecommendationSource =
  | 'menu'
  | 'database'
  | 'ai'

export type RecommendationConfidence =
  | 'high'
  | 'medium'
  | 'low'

export interface Recommendation {
  name: string
  price: string | null
  match_status: MatchStatus
  image_url: string | null
  taste: string[]
  texture: string[]
  ingredients: string[]
  reasons: string[]
  warnings: string[]
  source: RecommendationSource
  confidence: RecommendationConfidence
}