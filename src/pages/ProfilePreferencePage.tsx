import { useState } from 'react'
import {
  allergyOptions,
  dietaryRestrictionOptions,
  religiousRestrictionOptions,
  preferredProteinOptions,
  preferredFlavourOptions,
  preferredTextureOptions,
  spiceLevelOptions,
} from '../data/preferenceOptions'
import type {
  SpiceLevel,
  UserPreferenceProfile,
} from '../types/UserPreferenceProfile'

function PreferencePage() {
    const [selectedAllergies, setSelectedAllergies] = useState<string[]>([])
    const [selectedDietaryRestrictions, setSelectedDietaryRestrictions] = useState<string[]>([])
    const [selectedReligiousRestrictions, setSelectedReligiousRestrictions] = useState<string[]>([])
    const [selectedPreferredProteins, setSelectedPreferredProteins] = useState<string[]>([])
    const [selectedPreferredFlavours, setSelectedPreferredFlavours] = useState<string[]>([])
    const [selectedPreferredTextures, setSelectedPreferredTextures] = useState<string[]>([])
    const [selectedSpiceLevel, setSelectedSpiceLevel] = useState<SpiceLevel>(null)
    const [dislikedIngredientInput, setDislikedIngredientInput] = useState('')
    const [dislikedIngredients, setDislikedIngredients] = useState<string[]>([])

    const toggleAllergy = (value: string) => {
        setSelectedAllergies((current) =>
            current.includes(value)
                ? current.filter((item) => item !== value)
                : [...current, value]
        )
    }
    const toggleDietaryRestriction = (value: string) => {
        setSelectedDietaryRestrictions((current) =>
            current.includes(value)
                ? current.filter((item) => item !== value)
                : [...current, value]
        )
    }
    const toggleReligiousRestriction = (value: string) => {
        setSelectedReligiousRestrictions((current) =>
            current.includes(value)
                ? current.filter((item) => item !== value)
                : [...current, value]
        )
    }
    const togglePreferredProtein = (value: string) => {
        setSelectedPreferredProteins((current) =>
            current.includes(value)
                ? current.filter((item) => item !== value)
                : [...current, value]
        )
    }
    const togglePreferredFlavour = (value: string) => {
        setSelectedPreferredFlavours((current) =>
            current.includes(value)
                ? current.filter((item) => item !== value)
                : [...current, value]
        )
    }
    const togglePreferredTexture = (value: string) => {
        setSelectedPreferredTextures((current) =>
        current.includes(value)
            ? current.filter((item) => item !== value)
            : [...current, value]
        )
    }
    const addDislikedIngredient = () => {
        const value = dislikedIngredientInput
            .trim()
            .toLowerCase()
            .replace(/\s+/g, '_')

        if (!value) return

        if (!dislikedIngredients.includes(value)) {
            setDislikedIngredients((current) => [...current, value])
        }

        setDislikedIngredientInput('')
    }
    const removeDislikedIngredient = (value: string) => {
        setDislikedIngredients((current) =>
            current.filter((item) => item !== value)
    )
}

const preferenceProfile: UserPreferenceProfile = {
  allergies: selectedAllergies,
  dietary_restrictions: selectedDietaryRestrictions,
  religious_restrictions: selectedReligiousRestrictions,
  preferred_proteins: selectedPreferredProteins,
  preferred_flavours: selectedPreferredFlavours,
  preferred_textures: selectedPreferredTextures,
  spice_level: selectedSpiceLevel,
  disliked_ingredients: dislikedIngredients,
}
const handleSavePreferences = () => {
  console.log('Preference payload:', preferenceProfile)
}

return (
    <main className="min-h-screen bg-gray-50 px-6 py-10">
    <div className="mx-auto max-w-2xl">
        <h1 className="text-3xl font-bold text-gray-900">
            Tell us what works for you
        </h1>

        <p className="mt-3 text-gray-600">
            We'll use this to personalise your menu recommendations.
            You can change these preferences later.
        </p>
         <section className="mt-10">
            <h2 className="text-xl font-semibold text-gray-900">
                Allergies
            </h2>

            <p className="mt-1 text-sm text-gray-500">
                Select any that apply to you.
            </p>

        <div className="mt-4 flex flex-wrap gap-3">
            {allergyOptions.map((option) => (
            <button
                key={option.value}
                type="button"
                onClick={() => toggleAllergy(option.value)}
                className={`rounded-full border px-4 py-2 text-sm transition ${
                selectedAllergies.includes(option.value)
                    ? 'border-green-700 bg-green-700 text-white'
                    : 'border-gray-300 bg-white text-gray-700'
                }`}
            >
                {option.label}
            </button>
            ))}
        </div>
        </section>
        
        <section className="mt-10">
            <h2 className="text-xl font-semibold text-gray-900">
                Dietary restrictions
             </h2>

             <p className="mt-1 text-sm text-gray-500">
                Select any dietary requirements that apply to you.
            </p>

            <div className="mt-4 flex flex-wrap gap-3">
                {dietaryRestrictionOptions.map((option) => (
                    <button
                        key={option.value}
                        type="button"
                        onClick={() => toggleDietaryRestriction(option.value)}
                        className={`rounded-full border px-4 py-2 text-sm transition ${
                            selectedDietaryRestrictions.includes(option.value)
                                ? 'border-green-700 bg-green-700 text-white'
                                : 'border-gray-300 bg-white text-gray-700'
                        }`}
                    >
                    {option.label}
                </button>
            ))}
            </div>
        </section>

        <section className="mt-10">
            <h2 className="text-xl font-semibold text-gray-900">
                Religious dietary requirements
            </h2>

            <p className="mt-1 text-sm text-gray-500">
                Select any requirements that apply to you.
             </p>

            <div className="mt-4 flex flex-wrap gap-3">
                {religiousRestrictionOptions.map((option) => (
                    <button
                        key={option.value}
                        type="button"
                        onClick={() => toggleReligiousRestriction(option.value)}
                        className={`rounded-full border px-4 py-2 text-sm transition ${
                            selectedReligiousRestrictions.includes(option.value)
                                ? 'border-green-700 bg-green-700 text-white'
                                : 'border-gray-300 bg-white text-gray-700'
                         }`}
                    >
                         {option.label}
                    </button>
                 ))}
             </div>
        </section>

        <section className="mt-10">
            <h2 className="text-xl font-semibold text-gray-900">
                Preferred proteins
            </h2>

            <p className="mt-1 text-sm text-gray-500">
                Select the types of protein you usually enjoy.
            </p>

            <div className="mt-4 flex flex-wrap gap-3">
                {preferredProteinOptions.map((option) => (
                    <button
                        key={option.value}
                        type="button"
                        onClick={() => togglePreferredProtein(option.value)}
                        className={`rounded-full border px-4 py-2 text-sm transition ${
                            selectedPreferredProteins.includes(option.value)
                                ? 'border-green-700 bg-green-700 text-white'
                                : 'border-gray-300 bg-white text-gray-700'
                        }`}
                    >
                        {option.label}
                    </button>
                ))}
            </div>
        </section>

        <section className="mt-10">
            <h2 className="text-xl font-semibold text-gray-900">
                Preferred flavours
            </h2>
            
            <p className="mt-1 text-sm text-gray-500">
                Select the flavours you usually enjoy.
            </p>

            <div className="mt-4 flex flex-wrap gap-3">
                {preferredFlavourOptions.map((option) => (
                    <button
                    key={option.value}
                    type="button"
                    onClick={() => togglePreferredFlavour(option.value)}
                    className={`rounded-full border px-4 py-2 text-sm transition ${
                        selectedPreferredFlavours.includes(option.value)
                            ? 'border-green-700 bg-green-700 text-white'
                            : 'border-gray-300 bg-white text-gray-700'
                    }`}
                >
                    {option.label}
                </button>
                ))}
            </div>
        </section>

        <section className="mt-10">
            <h2 className="text-xl font-semibold text-gray-900">
                Preferred textures
            </h2>

            <p className="mt-1 text-sm text-gray-500">
                Select the textures you usually enjoy.
            </p>

            <div className="mt-4 flex flex-wrap gap-3">
                {preferredTextureOptions.map((option) => (
                <button
                    key={option.value}
                    type="button"
                    onClick={() => togglePreferredTexture(option.value)}
                    className={`rounded-full border px-4 py-2 text-sm transition ${
                        selectedPreferredTextures.includes(option.value)
                            ? 'border-green-700 bg-green-700 text-white'
                            : 'border-gray-300 bg-white text-gray-700'
                    }`}
                >
                    {option.label}
                </button>
                ))}
            </div>
        </section>

        <section className="mt-10">
            <h2 className="text-xl font-semibold text-gray-900">
                Spice level
            </h2>

            <p className="mt-1 text-sm text-gray-500">
                Select your preferred level of spiciness.
            </p>

            <div className="mt-4 flex flex-wrap gap-3">
                {spiceLevelOptions.map((option) => (
                <button
                    key={option.value}
                    type="button"
                    onClick={() => setSelectedSpiceLevel(option.value as SpiceLevel)}
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
        </section>

        <section className="mt-10">
            <h2 className="text-xl font-semibold text-gray-900">
                Ingredients you'd rather avoid
            </h2>

            <p className="mt-1 text-sm text-gray-500">
                Add any ingredients you dislike or prefer not to eat.
            </p>

            <input
                type="text"
                value={dislikedIngredientInput}
                onChange={(event) => setDislikedIngredientInput(event.target.value)}
                onKeyDown={(event) => {
                    if (event.key === 'Enter') {
                        event.preventDefault()
                        addDislikedIngredient()
                    }
                }}
                placeholder="e.g. mushrooms, olives"
                className="mt-4 w-full rounded-xl border border-gray-300 bg-white px-4 py-3 text-gray-900 outline-none focus:border-green-700"
            />
            {dislikedIngredients.length > 0 && (
                <div className="mt-3 flex flex-wrap gap-2">
                    {dislikedIngredients.map((ingredient) => (
                        <span
                        key={ingredient}
                        className="flex items-center gap-2 rounded-full bg-green-100 px-3 py-1 text-sm text-green-800"
                        >
                            {ingredient.replace(/_/g, ' ')}
                            <button
                                type="button"
                                onClick={() => removeDislikedIngredient(ingredient)}
                                className="text-green-700 hover:text-green-900"
                                aria-label={`Remove ${ingredient.replace(/_/g, ' ')}`}
                            >
                                ×
                            </button>
                        </span>
                        ))}
                        </div>
                    )}
        </section>
        <button
            type="button"
            onClick={handleSavePreferences}
            className="mt-10 w-full rounded-xl bg-green-700 px-6 py-3 font-medium text-white hover:bg-green-800"
        >
            Save preferences
        </button>
        </div>
    </main>
  )
}

export default PreferencePage