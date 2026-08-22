import { useState } from 'react'
import {
  preferredProteinOptions,
  preferredFlavourOptions,
  preferredTextureOptions,
  spiceLevelOptions,
} from '../data/preferenceOptions'
import type { SpiceLevel } from '../types/UserPreferenceProfile'
import type { CurrentPreference } from '../types/CurrentPreference'

function CurrentPreferenceSelector() {
    const [selectedProteins, setSelectedProteins] = useState<string[]>([])
    const [selectedFlavours, setSelectedFlavours] = useState<string[]>([])
    const [selectedTextures, setSelectedTextures] = useState<string[]>([])
    const [selectedSpiceLevel, setSelectedSpiceLevel] = useState<SpiceLevel>(null)

    const toggleProtein = (value: string) => {
        setSelectedProteins((current) =>
            current.includes(value)
                ? current.filter((item) => item !== value)
                : [...current, value]
        )
    }
    const toggleFlavour = (value: string) => {
        setSelectedFlavours((current) =>
            current.includes(value)
                ? current.filter((item) => item !== value)
                : [...current, value]
        )
    }
    const toggleTexture = (value: string) => {
        setSelectedTextures((current) =>
            current.includes(value)
                ? current.filter((item) => item !== value)
                : [...current, value]
        )
    }

    const currentPreference: CurrentPreference = {
        preferred_proteins: selectedProteins,
        preferred_flavours: selectedFlavours,
        preferred_textures: selectedTextures,
        spice_level: selectedSpiceLevel,
    }
    const handleRecommend = () => {
        console.log('Current preference payload:', currentPreference)
    }

    return (
    <section className="mt-8">
        <h2 className="text-2xl font-semibold text-gray-900">
            What are you in the mood for?
        </h2>
        
        <p className="mt-2 text-gray-500">
            Choose what sounds good for this meal.
        </p>
        
        <div className="mt-6">
            <h3 className="text-sm font-semibold text-gray-700">
                Protein
            </h3>
            
            <div className="mt-3 flex flex-wrap gap-3">
                {preferredProteinOptions.map((option) => (
                    <button
                        key={option.value}
                        type="button"
                        onClick={() => toggleProtein(option.value)}
                        className={`rounded-full border px-4 py-2 text-sm transition ${
                            selectedProteins.includes(option.value)
                                ? 'border-green-700 bg-green-700 text-white'
                                : 'border-gray-300 bg-white text-gray-700'
                            }`}
                    >
                        {option.label}
                    </button>
                ))}
            </div>
        </div>

        <div className="mt-6">
            <h3 className="text-sm font-semibold text-gray-700">
                Flavour
            </h3>
            
            <div className="mt-3 flex flex-wrap gap-3">
                {preferredFlavourOptions.map((option) => (
                    <button
                        key={option.value}
                        type="button"
                        onClick={() => toggleFlavour(option.value)}
                        className={`rounded-full border px-4 py-2 text-sm transition ${
                            selectedFlavours.includes(option.value)
                                ? 'border-green-700 bg-green-700 text-white'
                                : 'border-gray-300 bg-white text-gray-700'
                        }`}
                    >
                        {option.label}
                    </button>
                ))}
            </div>
        </div>

        <div className="mt-6">
            <h3 className="text-sm font-semibold text-gray-700">
                Texture
            </h3>
            
            <div className="mt-3 flex flex-wrap gap-3">
                {preferredTextureOptions.map((option) => (
                    <button
                        key={option.value}
                        type="button"
                        onClick={() => toggleTexture(option.value)}
                        className={`rounded-full border px-4 py-2 text-sm transition ${
                            selectedTextures.includes(option.value)
                                ? 'border-green-700 bg-green-700 text-white'
                                : 'border-gray-300 bg-white text-gray-700'
                        }`}
                    >
                        {option.label}
                    </button>
                ))}
            </div>
        </div>

        <div className="mt-6">
            <h3 className="text-sm font-semibold text-gray-700">
                Spice level
            </h3>

            <div className="mt-3 flex flex-wrap gap-3">
                {spiceLevelOptions.map((option) => (
                <button
                    key={option.value}
                    type="button"
                    onClick={() =>
                        setSelectedSpiceLevel(option.value as SpiceLevel)
                    }
                    className={`rounded-full border px-4 py-2 text-sm transition ${
                        selectedSpiceLevel === option.value
                            ? 'border-green-700 bg-green-700 text-white'
                            : 'border-gray-300 bg-white text-gray-700'
                    }`}
                >
                    {option.label}
                </button>
                ))}
            </div>
        </div>
        <button
            type="button"
            onClick={handleRecommend}
            className="mt-8 w-full rounded-xl bg-green-700 px-6 py-3 font-medium text-white hover:bg-green-800"
        >
            Recommend dishes
        </button>
    </section>
  )
}

export default CurrentPreferenceSelector