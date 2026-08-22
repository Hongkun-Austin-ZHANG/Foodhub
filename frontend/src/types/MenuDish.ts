export interface MenuDish {
  dish_id: string
  original_name: string
  translated_name: string | null
  canonical_name_en: string
  menu_description: string | null
  translated_description: string | null
  explicit_ingredients: string[]
  canonical_ingredients_en: string[]
  translated_explicit_ingredients: string[]
  price: string | number | null
  price_text: string | null
  currency: string | null
  source_text: string | null
  extraction_confidence: number
}

export interface IngredientEvidence {
  name: string
  source: 'menu' | 'themealdb' | 'llm' | 'local_fallback'
  evidence_level:
    | 'explicit'
    | 'reference_recipe'
    | 'inferred'
    | 'cached_inference'
  confidence: number | null
  reasoning: string | null
}

export interface AllergenAssessment {
  code: string
  status: 'contains' | 'may_contain' | 'unknown'
  evidence_source: 'menu_evidence' | 'reference_recipe' | 'inferred'
  confidence: number
  reasoning: string
}

export interface DishEvidence {
  explicit_ingredients: string[]
  reference_ingredients: string[]
  inferred_ingredients: IngredientEvidence[]
  allergen_assessments: AllergenAssessment[]
  display: {
    explicit_ingredients: string[]
    reference_ingredients: string[]
    inferred_ingredients: Array<{ name: string; reasoning: string | null }>
  }
}

export interface DishDecision {
  status: 'good_match' | 'check_with_staff' | 'avoid'
  reasons: string[]
  warnings: string[]
}

export interface DishEnrichment {
  summary: string | null
  display_summary: string | null
  cuisine: string | null
  display_cuisine: string | null
  source: 'menu_only' | 'themealdb' | 'llm' | 'local_fallback' | 'demo_database'
  confidence: number | null
}

export interface AnalyzedDish {
  dish: MenuDish
  resolution_status:
    | 'local_fallback'
    | 'llm_fallback'
    | 'themealdb_match'
    | 'needs_llm'
    | 'lookup_unavailable'
  match_score: number | null
  image_url: string | null
  image_is_reference: boolean
  enrichment: DishEnrichment
  evidence: DishEvidence
  decision: DishDecision
}

export interface MenuScanResponse {
  menu_id: string
  source_language: string
  target_language: string
  mode: 'live' | 'demo'
  analysis_complete: boolean
  effective_preferences: unknown[]
  dishes: AnalyzedDish[]
  fallback_batch_request: unknown | null
}
