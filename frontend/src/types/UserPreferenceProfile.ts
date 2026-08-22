export type SpiceLevel = 'mild' | 'medium' | 'hot' | null

export interface UserPreferenceProfile {
  allergies: string[]
  dietary_restrictions: string[]
  religious_restrictions: string[]
  preferred_proteins: string[]
  preferred_flavours: string[]
  preferred_textures: string[]
  spice_level: SpiceLevel
  disliked_ingredients: string[]
}