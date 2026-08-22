export type ExtractionConfidence = 'high' | 'medium' | 'low'

export interface MenuDish {
  original_name: string
  translated_name: string
  canonical_guess: string | null

  price: string

  menu_description: string | null
  translated_description: string | null

  explicit_ingredients: string[]

  source_text: string

  extraction_confidence: ExtractionConfidence
  menu_language: string
}