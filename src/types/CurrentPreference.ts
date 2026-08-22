import type { SpiceLevel } from './UserPreferenceProfile'

export interface CurrentPreference {
  preferred_proteins: string[]
  preferred_flavours: string[]
  preferred_textures: string[]
  spice_level: SpiceLevel
}