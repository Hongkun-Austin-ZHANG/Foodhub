interface ProfilePanelProps {
  onEditPreferences: () => void
  onLogout?: () => void
  displayName?: string | null
  preferredLanguage?: string
}

function ProfilePanel({
  onEditPreferences,
  onLogout,
  displayName,
  preferredLanguage,
}: ProfilePanelProps) {
  return (
    <div className="absolute right-0 top-12 z-50 w-72 rounded-2xl border border-gray-200 bg-white p-5 shadow-lg">
      <div className="border-b border-gray-100 pb-4">
        <p className="font-semibold text-gray-900">
          {displayName || 'FoodHub user'}
        </p>

        <p className="mt-1 text-sm text-gray-500">
          Preferred language: {preferredLanguage || 'en'}
        </p>
      </div>

      <div className="py-4">
        <p className="text-sm font-semibold text-gray-900">
          Dietary preferences
        </p>

        <p className="mt-1 text-sm text-gray-500">
          Manage allergies, dietary requirements and food preferences.
        </p>
      </div>

      <button
        type="button"
        onClick={onEditPreferences}
        className="w-full rounded-xl bg-green-700 px-4 py-2 text-sm font-medium text-white hover:bg-green-800"
      >
        Edit preferences
      </button>

      <button
        type="button"
        onClick={onLogout}
        className="mt-2 w-full rounded-xl px-4 py-2 text-sm text-gray-600 hover:bg-gray-100"
      >
        Log out
      </button>
    </div>
  )
}

export default ProfilePanel
