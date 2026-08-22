import { useState } from 'react'
import ProfilePanel from './ProfilePanel'

interface HeaderProps {
  onEditPreferences?: () => void
  showProfile?: boolean
}

function Header({
  onEditPreferences,
  showProfile = true,
}: HeaderProps) {
  const [showProfilePanel, setShowProfilePanel] = useState(false)

  return (
    <header className="border-b border-gray-200 bg-white">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-6">
        <div>
          <h1 className="text-2xl font-bold text-green-700">
            FoodHub
          </h1>

          <p className="mt-1 text-sm text-gray-500">
            Understand what you're actually ordering.
          </p>
        </div>

        {showProfile && (
          <div className="relative">
            <button
              type="button"
              onClick={() =>
                setShowProfilePanel((current) => !current)
              }
              className="flex h-10 w-10 items-center justify-center rounded-full bg-green-700 font-semibold text-white"
            >
              S
            </button>

            {showProfilePanel && onEditPreferences && (
              <ProfilePanel
                onEditPreferences={() => {
                  setShowProfilePanel(false)
                  onEditPreferences()
                }}
              />
            )}
          </div>
        )}
      </div>
    </header>
  )
}

export default Header