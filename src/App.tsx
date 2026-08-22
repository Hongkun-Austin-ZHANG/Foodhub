import { useEffect, useState } from 'react'
import DishCard from './components/DishCard'
import CurrentPreferenceSelector from './components/CurrentPreferenceSelector'
import ScanMenuPage from './pages/ScanMenuPage'
import { mockMenu } from './data/mockMenu'
import ProcessingPage from './pages/ProcessingPage.tsx'

type AppScreen = 'scan' | 'processing' | 'results'

function App() {
  const [screen, setScreen] = useState<AppScreen>('scan')

  useEffect(() => {
    if (screen !== 'processing') return
    
    const timer = window.setTimeout(() => {
      setScreen('results')
    }, 2000)
    return () => window.clearTimeout(timer)
  }, [screen])

  if (screen === 'scan') {
    return (
      <ScanMenuPage
      onScan={() => setScreen('processing')}
      />
    )
  }

  if (screen === 'processing') {
    return <ProcessingPage />
  }

  return (
    <main className="min-h-screen bg-gray-50">
      <header className="border-b border-gray-200 bg-white">
        <div className="mx-auto max-w-7xl px-6 py-6">
          <h1 className="text-2xl font-bold text-green-700">
            FoodHub
          </h1>

          <p className="mt-1 text-sm text-gray-500">
            Understand what you're actually ordering.
          </p>
        </div>
      </header>

      <div className="mx-auto grid max-w-7xl gap-8 px-6 py-8 lg:grid-cols-2">
        <section>
          <button
            type="button"
            onClick={() => setScreen('scan')}
            className="mb-5 text-sm font-medium text-green-700"
          >
            ← Scan another menu
          </button>

          <div className="mb-6">
            <h2 className="text-2xl font-bold text-gray-900">
              Your Menu
            </h2>

            <p className="mt-1 text-gray-500">
              {mockMenu.length} dishes found
            </p>
          </div>

          <div className="space-y-5">
            {mockMenu.map((dish) => (
              <DishCard
                key={dish.original_name}
                dish={dish}
              />
            ))}
          </div>
        </section>

        <aside className="lg:sticky lg:top-8 lg:self-start">
          <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
            <CurrentPreferenceSelector />
          </div>
        </aside>
      </div>
    </main>
  )
}

export default App