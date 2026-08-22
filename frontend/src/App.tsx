import { useEffect, useState } from 'react'
import Header from './components/Header'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import DishCard from './components/DishCard'
import CurrentPreferenceSelector from './components/CurrentPreferenceSelector'
import ScanMenuPage, { type ScanMode } from './pages/ScanMenuPage'
import ProcessingPage from './pages/ProcessingPage'
import ProfilePreferencePage from './pages/ProfilePreferencePage'
import { clearStoredAuthentication, isAuthenticated } from './services/authApi'
import { loadDemoMenu, scanMenu } from './services/menuApi'
import { getCapabilities, type Capabilities } from './services/systemApi'
import { getProfile } from './services/preferenceApi'
import type { MenuScanResponse } from './types/MenuDish'
import { useI18n, type Language } from './i18n'

type AppScreen = 'login' | 'register' | 'profile' | 'scan' | 'processing' | 'results'

function App() {
  const { setLanguage, t } = useI18n()
  const [screen, setScreen] = useState<AppScreen>(() => isAuthenticated() ? 'scan' : 'login')
  const [profileReturnScreen, setProfileReturnScreen] = useState<AppScreen>('scan')
  const [isProfileOnboarding, setIsProfileOnboarding] = useState(false)
  const [menu, setMenu] = useState<MenuScanResponse | null>(null)
  const [scanError, setScanError] = useState<string | null>(null)
  const [capabilities, setCapabilities] = useState<Capabilities>({ demo_available: true, live_scan_available: false, supported_languages: ['en', 'zh', 'fr'] })
  const [scanMode, setScanMode] = useState<ScanMode>('demo')

  useEffect(() => {
    getCapabilities().then((value) => {
      setCapabilities(value)
      setScanMode(value.live_scan_available ? 'live' : 'demo')
    }).catch(() => undefined)
    if (isAuthenticated()) {
      getProfile().then((profile) => {
        if (['en', 'zh', 'fr'].includes(profile.preferred_language)) setLanguage(profile.preferred_language as Language)
      }).catch(() => {
        clearStoredAuthentication()
        setScreen('login')
      })
    }
  }, [setLanguage])

  const handleScan = async (files: File[], mode: ScanMode) => {
    setScanError(null)
    setScreen('processing')
    try {
      const response = mode === 'demo' ? await loadDemoMenu() : await scanMenu(files)
      setMenu(response)
      setScreen('results')
    } catch (reason) {
      setScanError(reason instanceof Error ? reason.message : 'Menu scan failed.')
      setScreen('scan')
    }
  }

  const openPreferencesFromScan = () => {
    setIsProfileOnboarding(false)
    setProfileReturnScreen('scan')
    setScreen('profile')
  }

  const finishLogout = () => {
    setMenu(null)
    setScanError(null)
    setScreen('login')
  }

  const scanPage = (
    <ScanMenuPage
      onScan={handleScan}
      onEditPreferences={openPreferencesFromScan}
      onLogout={finishLogout}
      capabilities={capabilities}
      mode={scanMode}
      onModeChange={setScanMode}
      error={scanError}
    />
  )

  if (screen === 'login') {
    return <LoginPage onLogin={() => setScreen('scan')} onCreateAccount={() => setScreen('register')} />
  }

  if (screen === 'register') {
    return (
      <RegisterPage
        onRegister={() => {
          setIsProfileOnboarding(true)
          setProfileReturnScreen('scan')
          setScreen('profile')
        }}
        onBackToLogin={() => setScreen('login')}
      />
    )
  }

  if (screen === 'scan') return scanPage
  if (screen === 'processing') return <ProcessingPage />

  if (screen === 'profile') {
    return (
      <ProfilePreferencePage
        isOnboarding={isProfileOnboarding}
        onBack={() => setScreen(profileReturnScreen)}
        onContinue={() => {
          setIsProfileOnboarding(false)
          setScreen(profileReturnScreen)
        }}
      />
    )
  }

  if (!menu) return scanPage

  return (
    <main className="min-h-screen bg-gray-50">
      <Header
        onLogout={finishLogout}
        onEditPreferences={() => {
          setIsProfileOnboarding(false)
          setProfileReturnScreen('results')
          setScreen('profile')
        }}
      />
      <div className="mx-auto grid max-w-7xl gap-8 px-6 py-8 lg:grid-cols-2">
        <section>
          <button type="button" onClick={() => setScreen('scan')} className="mb-5 text-sm font-medium text-green-700">
            ← {t('scanAnother')}
          </button>
          <div className="mb-6">
            <div className="flex items-center gap-3">
              <h2 className="text-2xl font-bold text-gray-900">{t('menuTitle')}</h2>
              {menu.mode === 'demo' && <span className="rounded-full bg-blue-100 px-3 py-1 text-xs font-semibold text-blue-700">{t('demoMode')}</span>}
            </div>
            <p className="mt-1 text-gray-500">{menu.dishes.length} {t('dishesFound')} · {t('displayLanguage')} {menu.target_language}</p>
          </div>
          <p className="mb-5 rounded-xl bg-amber-50 p-4 text-sm text-amber-800">{t('disclaimer')}</p>
          <div className="space-y-5">
            {menu.dishes.map((item) => <DishCard key={item.dish.dish_id} item={item} />)}
          </div>
        </section>
        <aside className="lg:sticky lg:top-8 lg:self-start">
          <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
            <CurrentPreferenceSelector menuId={menu.menu_id} />
          </div>
        </aside>
      </div>
    </main>
  )
}

export default App
