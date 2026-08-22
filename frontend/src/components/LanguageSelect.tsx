import { useI18n, type Language } from '../i18n'

export default function LanguageSelect() {
  const { language, setLanguage, t } = useI18n()
  return (
    <label className="block text-sm font-medium text-gray-700">
      {t('preferredLanguage')}
      <select value={language} onChange={(event) => setLanguage(event.target.value as Language)} className="mt-2 w-full rounded-xl border border-gray-300 bg-white px-4 py-3">
        <option value="en">English</option>
        <option value="zh">中文</option>
        <option value="fr">Français</option>
      </select>
    </label>
  )
}
