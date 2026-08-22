import { useState } from 'react'
import Header from './components/Header'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import DishCard from './components/DishCard'
import CurrentPreferenceSelector from './components/CurrentPreferenceSelector'
import ScanMenuPage from './pages/ScanMenuPage'
import ProcessingPage from './pages/ProcessingPage'
import ProfilePreferencePage from './pages/ProfilePreferencePage'
import { isAuthenticated } from './services/authApi'
import { scanMenu } from './services/menuApi'
import type { MenuScanResponse } from './types/MenuDish'

type AppScreen = 'login' | 'register' | 'profile' | 'scan' | 'processing' | 'results'

function App() {
  const [screen, setScreen] = useState<AppScreen>(() => isAuthenticated() ? 'scan' : 'login')
  const [profileReturnScreen, setProfileReturnScreen] = useState<AppScreen>('scan')
  const [isProfileOnboarding, setIsProfileOnboarding] = useState(false)
  const [menu, setMenu] = useState<MenuScanResponse | null>(null)
  const [scanError, setScanError] = useState<string | null>(null)

  const handleScan = async (files: File[]) => {
    setScanError(null)
    setScreen('processing')
    try {
      const response = await scanMenu(files)
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
            ← Scan another menu
          </button>
          <div className="mb-6">
            <h2 className="text-2xl font-bold text-gray-900">Your Menu</h2>
            <p className="mt-1 text-gray-500">{menu.dishes.length} dishes found · display language {menu.target_language}</p>
          </div>
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
