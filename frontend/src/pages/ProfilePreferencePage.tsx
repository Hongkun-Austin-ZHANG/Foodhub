import { useEffect, useState } from 'react'
import {
  allergyOptions,
  dietaryRestrictionOptions,
  religiousRestrictionOptions,
  preferredProteinOptions,
  preferredFlavourOptions,
  preferredTextureOptions,
  spiceLevelOptions,
  type PreferenceOption,
} from '../data/preferenceOptions'
import type { SpiceLevel, UserPreferenceProfile } from '../types/UserPreferenceProfile'
import { getPreferenceProfile, savePreferenceProfile, updateProfile } from '../services/preferenceApi'
import { useI18n } from '../i18n'
import LanguageSelect from '../components/LanguageSelect'

interface ProfilePreferencePageProps { onBack: () => void; onContinue: () => void; isOnboarding?: boolean }

function ProfilePreferencePage({ onBack, onContinue, isOnboarding = false }: ProfilePreferencePageProps) {
  const { language, optionLabel, t } = useI18n()
  const [profile, setProfile] = useState<UserPreferenceProfile>({ allergies: [], dietary_restrictions: [], religious_restrictions: [], preferred_proteins: [], preferred_flavours: [], preferred_textures: [], spice_level: null, disliked_ingredients: [] })
  const [dislikedInput, setDislikedInput] = useState('')
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let active = true
    getPreferenceProfile().then((value) => { if (active) setProfile(value) }).catch((reason) => { if (active) setError(reason instanceof Error ? reason.message : 'Could not load preferences.') }).finally(() => { if (active) setLoading(false) })
    return () => { active = false }
  }, [])

  const toggle = (field: keyof UserPreferenceProfile, value: string) => {
    setProfile((current) => {
      const values = current[field]
      if (!Array.isArray(values)) return current
      return { ...current, [field]: values.includes(value) ? values.filter((item) => item !== value) : [...values, value] }
    })
  }

  const group = (title: string, help: string, field: keyof UserPreferenceProfile, options: PreferenceOption[]) => {
    const selected = profile[field]
    return (
      <section className="mt-10">
        <h2 className="text-xl font-semibold text-gray-900">{title}</h2>
        <p className="mt-1 text-sm text-gray-500">{help}</p>
        <div className="mt-4 flex flex-wrap gap-3">
          {options.map((option) => (
            <button key={option.value} type="button" onClick={() => toggle(field, option.value)} className={`rounded-full border px-4 py-2 text-sm transition ${Array.isArray(selected) && selected.includes(option.value) ? 'border-green-700 bg-green-700 text-white' : 'border-gray-300 bg-white text-gray-700'}`}>
              {optionLabel(option.value, option.label)}
            </button>
          ))}
        </div>
      </section>
    )
  }

  const addDisliked = () => {
    const value = dislikedInput.trim().toLowerCase().replace(/\s+/g, '_')
    if (!value || profile.disliked_ingredients.includes(value)) return
    setProfile((current) => ({ ...current, disliked_ingredients: [...current.disliked_ingredients, value] }))
    setDislikedInput('')
  }

  const save = async () => {
    setSaving(true); setError(null)
    try {
      await Promise.all([savePreferenceProfile(profile), updateProfile({ preferred_language: language })])
      onContinue()
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'Could not save preferences.')
    } finally { setSaving(false) }
  }

  return (
    <main className="min-h-screen bg-gray-50 px-6 py-10">
      <div className="mx-auto max-w-2xl">
        {!isOnboarding && <button type="button" onClick={onBack} className="mb-6 text-sm font-medium text-green-700">← {t('backToMenu')}</button>}
        <h1 className="text-3xl font-bold text-gray-900">{t('profileTitle')}</h1>
        <p className="mt-3 text-gray-600">{t('profileText')}</p>
        <div className="mt-8 rounded-2xl border border-gray-200 bg-white p-5"><LanguageSelect /></div>
        {loading && <p className="mt-5 text-sm text-gray-500">{t('loadingPreferences')}</p>}
        {error && <p className="mt-5 rounded-xl bg-red-50 p-4 text-sm text-red-700">{error}</p>}
        {group(t('allergies'), t('selectApplicable'), 'allergies', allergyOptions)}
        {group(t('dietaryRestrictions'), t('selectApplicable'), 'dietary_restrictions', dietaryRestrictionOptions)}
        {group(t('religiousRequirements'), t('selectApplicable'), 'religious_restrictions', religiousRestrictionOptions)}
        {group(t('preferredProteins'), t('selectEnjoy'), 'preferred_proteins', preferredProteinOptions)}
        {group(t('preferredFlavours'), t('selectEnjoy'), 'preferred_flavours', preferredFlavourOptions)}
        {group(t('preferredTextures'), t('selectEnjoy'), 'preferred_textures', preferredTextureOptions)}
        <section className="mt-10">
          <h2 className="text-xl font-semibold text-gray-900">{t('spiceLevel')}</h2>
          <div className="mt-4 flex flex-wrap gap-3">
            {spiceLevelOptions.map((option) => <button key={option.value} type="button" onClick={() => setProfile((current) => ({ ...current, spice_level: current.spice_level === option.value ? null : option.value as SpiceLevel }))} className={`rounded-full border px-4 py-2 text-sm ${profile.spice_level === option.value ? 'border-green-700 bg-green-700 text-white' : 'border-gray-300 bg-white text-gray-700'}`}>{optionLabel(option.value, option.label)}</button>)}
          </div>
        </section>
        <section className="mt-10">
          <h2 className="text-xl font-semibold text-gray-900">{t('disliked')}</h2>
          <input value={dislikedInput} onChange={(event) => setDislikedInput(event.target.value)} onKeyDown={(event) => { if (event.key === 'Enter') { event.preventDefault(); addDisliked() } }} placeholder={t('dislikedPlaceholder')} className="mt-4 w-full rounded-xl border border-gray-300 bg-white px-4 py-3" />
          <div className="mt-3 flex flex-wrap gap-2">{profile.disliked_ingredients.map((value) => <span key={value} className="flex items-center gap-2 rounded-full bg-green-100 px-3 py-1 text-sm text-green-800">{value.replaceAll('_', ' ')}<button type="button" onClick={() => setProfile((current) => ({ ...current, disliked_ingredients: current.disliked_ingredients.filter((item) => item !== value) }))}>×</button></span>)}</div>
        </section>
        <button type="button" onClick={save} disabled={loading || saving} className="mt-10 w-full rounded-xl bg-green-700 px-6 py-3 font-medium text-white disabled:opacity-60">{saving ? t('saving') : isOnboarding ? t('saveContinue') : t('savePreferences')}</button>
        {isOnboarding && <button type="button" onClick={onContinue} className="mt-3 w-full rounded-xl px-6 py-3 text-sm text-gray-500">{t('skip')}</button>}
      </div>
    </main>
  )
}

export default ProfilePreferencePage
