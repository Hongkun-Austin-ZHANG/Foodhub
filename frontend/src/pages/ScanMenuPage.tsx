import { useState } from 'react'
import Header from '../components/Header'
import { useI18n } from '../i18n'
import type { Capabilities } from '../services/systemApi'

export type ScanMode = 'live' | 'demo'

interface MenuPage { file: File; preview: string }
interface ScanMenuPageProps {
  onScan: (files: File[], mode: ScanMode) => void
  onEditPreferences: () => void
  onLogout: () => void
  capabilities: Capabilities
  mode: ScanMode
  onModeChange: (mode: ScanMode) => void
  error?: string | null
}

function ScanMenuPage({ onScan, onEditPreferences, onLogout, capabilities, mode, onModeChange, error }: ScanMenuPageProps) {
  const { t } = useI18n()
  const [menuPages, setMenuPages] = useState<MenuPage[]>([])

  const handleFileUpload = (files: FileList | null) => {
    if (!files) return
    for (const file of Array.from(files).slice(0, 5 - menuPages.length)) {
      const reader = new FileReader()
      reader.onload = () => setMenuPages((current) => [...current, { file, preview: reader.result as string }])
      reader.readAsDataURL(file)
    }
  }

  return (
    <main className="min-h-screen bg-gray-50">
      <Header onEditPreferences={onEditPreferences} onLogout={onLogout} />
      <div className="mx-auto max-w-2xl px-6 py-12">
        <h2 className="text-3xl font-bold text-gray-900">{t('scanTitle')}</h2>
        <p className="mt-3 text-gray-600">{t('scanSubtitle')}</p>
        <div className="mt-6 grid grid-cols-2 gap-2 rounded-xl bg-gray-100 p-1">
          <button type="button" disabled={!capabilities.demo_available} onClick={() => onModeChange('demo')} className={`rounded-lg px-4 py-2 text-sm font-semibold ${mode === 'demo' ? 'bg-white text-green-700 shadow-sm' : 'text-gray-500'} disabled:opacity-40`}>{t('demoMode')}</button>
          <button type="button" disabled={!capabilities.live_scan_available} onClick={() => onModeChange('live')} className={`rounded-lg px-4 py-2 text-sm font-semibold ${mode === 'live' ? 'bg-white text-green-700 shadow-sm' : 'text-gray-500'} disabled:opacity-40`}>{t('liveMode')}</button>
        </div>
        {mode === 'demo' && <p className="mt-3 rounded-xl bg-blue-50 p-3 text-sm text-blue-700">{t('demoPrivacy')}</p>}
        {!capabilities.live_scan_available && <p className="mt-2 text-xs text-gray-500">{t('liveUnavailable')}</p>}
        {error && <p className="mt-5 rounded-xl bg-red-50 p-4 text-sm text-red-700">{error}</p>}
        <div className="mt-8 space-y-4">
          {menuPages.map((page, index) => (
            <div key={`${page.file.name}-${index}`} className="rounded-2xl border bg-white p-4 shadow-sm">
              <div className="flex items-center justify-between">
                <p className="font-medium">{t('page')} {index + 1}: {page.file.name}</p>
                <button type="button" onClick={() => setMenuPages((current) => current.filter((_, itemIndex) => itemIndex !== index))} className="text-sm text-red-600">{t('remove')}</button>
              </div>
              <img src={page.preview} alt={`${t('page')} ${index + 1}`} className="mt-4 max-h-96 w-full rounded-xl object-contain" />
            </div>
          ))}
          {menuPages.length < 5 && (
            <label className="flex cursor-pointer items-center justify-center rounded-xl border-2 border-dashed border-gray-300 bg-white px-5 py-8 font-medium text-gray-700 hover:border-green-600">
              + {menuPages.length ? t('addPage') : t('uploadPhotos')}
              <input type="file" multiple accept="image/jpeg,image/png,image/webp" className="hidden" onChange={(event) => { handleFileUpload(event.target.files); event.currentTarget.value = '' }} />
            </label>
          )}
          <button type="button" disabled={mode === 'live' && !menuPages.length} onClick={() => onScan(menuPages.map((page) => page.file), mode)} className="w-full rounded-xl bg-green-700 px-6 py-3 font-medium text-white disabled:opacity-50">
            {mode === 'demo' ? t('loadDemo') : t('scanMenu')}
          </button>
        </div>
      </div>
    </main>
  )
}

export default ScanMenuPage
