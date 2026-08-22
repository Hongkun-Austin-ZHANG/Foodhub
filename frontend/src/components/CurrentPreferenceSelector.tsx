import { useState } from 'react'
import {
  preferredProteinOptions,
  preferredFlavourOptions,
  preferredTextureOptions,
  spiceLevelOptions,
} from '../data/preferenceOptions'
import type { SpiceLevel } from '../types/UserPreferenceProfile'
import type { CurrentPreference } from '../types/CurrentPreference'
import type { RankedRecommendation } from '../types/Recommendation'
import { getRecommendations } from '../services/RecommendationApi'
import RecommendationCard from './RecommendationCard'

interface CurrentPreferenceSelectorProps {
  menuId: string
}

function CurrentPreferenceSelector({ menuId }: CurrentPreferenceSelectorProps) {
  const [selectedProteins, setSelectedProteins] = useState<string[]>([])
  const [selectedFlavours, setSelectedFlavours] = useState<string[]>([])
  const [selectedTextures, setSelectedTextures] = useState<string[]>([])
  const [selectedSpiceLevel, setSelectedSpiceLevel] = useState<SpiceLevel>(null)
  const [recommendations, setRecommendations] = useState<RankedRecommendation[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const toggle = (value: string, current: string[], update: (value: string[]) => void) => {
    update(current.includes(value) ? current.filter((item) => item !== value) : [...current, value])
  }

  const handleRecommend = async () => {
    const currentPreference: CurrentPreference = {
      preferred_proteins: selectedProteins,
      preferred_flavours: selectedFlavours,
      preferred_textures: selectedTextures,
      spice_level: selectedSpiceLevel,
    }
    setLoading(true)
    setError(null)
    try {
      const response = await getRecommendations(menuId, currentPreference)
      setRecommendations(response.recommendations)
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'Could not load recommendations.')
    } finally {
      setLoading(false)
    }
  }

  const group = (title: string, options: typeof preferredProteinOptions, selected: string[], update: (value: string[]) => void) => (
    <div className="mt-6">
      <h3 className="text-sm font-semibold text-gray-700">{title}</h3>
      <div className="mt-3 flex flex-wrap gap-3">
        {options.map((option) => (
          <button key={option.value} type="button" onClick={() => toggle(option.value, selected, update)} className={`rounded-full border px-4 py-2 text-sm ${selected.includes(option.value) ? 'border-green-700 bg-green-700 text-white' : 'border-gray-300 bg-white text-gray-700'}`}>
            {option.label}
          </button>
        ))}
      </div>
    </div>
  )

  return (
    <section>
      <h2 className="text-2xl font-semibold text-gray-900">What are you in the mood for?</h2>
      <p className="mt-2 text-gray-500">Empty groups use your saved long-term preferences.</p>
      {group('Protein', preferredProteinOptions, selectedProteins, setSelectedProteins)}
      {group('Flavour', preferredFlavourOptions, selectedFlavours, setSelectedFlavours)}
      {group('Texture', preferredTextureOptions, selectedTextures, setSelectedTextures)}
      <div className="mt-6">
        <h3 className="text-sm font-semibold text-gray-700">Spice level</h3>
        <div className="mt-3 flex flex-wrap gap-3">
          {spiceLevelOptions.map((option) => (
            <button key={option.value} type="button" onClick={() => setSelectedSpiceLevel(selectedSpiceLevel === option.value ? null : option.value as SpiceLevel)} className={`rounded-full border px-4 py-2 text-sm ${selectedSpiceLevel === option.value ? 'border-green-700 bg-green-700 text-white' : 'border-gray-300 bg-white text-gray-700'}`}>
              {option.label}
            </button>
          ))}
        </div>
      </div>
      {error && <p className="mt-5 rounded-xl bg-red-50 p-3 text-sm text-red-700">{error}</p>}
      <button type="button" onClick={handleRecommend} disabled={loading} className="mt-8 w-full rounded-xl bg-green-700 px-6 py-3 font-medium text-white disabled:opacity-60">
        {loading ? 'Updating recommendations...' : 'Recommend dishes'}
      </button>
      {recommendations.length > 0 && (
        <div className="mt-10 space-y-4">
          <h2 className="text-2xl font-bold text-gray-900">Top Picks</h2>
          {recommendations.map((recommendation) => <RecommendationCard key={recommendation.dish.dish_id} recommendation={recommendation} />)}
        </div>
      )}
    </section>
  )
}

export default CurrentPreferenceSelector
