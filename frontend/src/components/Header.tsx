import { useEffect, useState } from 'react'
import ProfilePanel from './ProfilePanel'
import { logout } from '../services/authApi'
import { getProfile, type UserProfile } from '../services/preferenceApi'
import { useI18n } from '../i18n'

interface HeaderProps {
  onEditPreferences?: () => void
  onLogout?: () => void
  showProfile?: boolean
}

function Header({
  onEditPreferences,
  onLogout,
  showProfile = true,
}: HeaderProps) {
  const { t } = useI18n()
  const [showProfilePanel, setShowProfilePanel] = useState(false)
  const [profile, setProfile] = useState<UserProfile | null>(null)

  useEffect(() => {
    if (!showProfile) return
    getProfile().then(setProfile).catch(() => undefined)
  }, [showProfile])

  return (
    <header className="border-b border-gray-200 bg-white">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-6">
        <div>
          <h1 className="text-2xl font-bold text-green-700">
            FoodHub
          </h1>

          <p className="mt-1 text-sm text-gray-500">
            {t('tagline')}
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
              {(profile?.display_name || 'F').trim().charAt(0).toUpperCase()}
            </button>

            {showProfilePanel && onEditPreferences && (
              <ProfilePanel
                displayName={profile?.display_name}
                preferredLanguage={profile?.preferred_language}
                onEditPreferences={() => {
                  setShowProfilePanel(false)
                  onEditPreferences()
                }}
                onLogout={async () => {
                  setShowProfilePanel(false)
                  try {
                    await logout()
                  } finally {
                    onLogout?.()
                  }
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
