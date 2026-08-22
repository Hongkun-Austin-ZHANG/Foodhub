import { useState } from 'react'
import { login } from '../services/authApi'
import { updateProfile } from '../services/preferenceApi'
import LanguageSelect from '../components/LanguageSelect'
import { useI18n } from '../i18n'

interface LoginPageProps {
  onLogin: () => void
  onCreateAccount: () => void
}

function LoginPage({ onLogin, onCreateAccount }: LoginPageProps) {
  const { language, t } = useI18n()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setError(null)
    setSubmitting(true)
    try {
      await login({ email, password })
      await updateProfile({ preferred_language: language })
      onLogin()
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'Login failed.')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <main className="flex min-h-screen items-center justify-center bg-gray-50 px-6">
      <div className="w-full max-w-md">
        <div className="mb-8 text-center">
          <h1 className="text-3xl font-bold text-green-700">FoodHub</h1>
          <p className="mt-2 text-sm text-gray-500">
            {t('tagline')}
          </p>
        </div>
        <div className="rounded-2xl border border-gray-200 bg-white p-8 shadow-sm">
          <h2 className="text-2xl font-bold text-gray-900">{t('welcomeBack')}</h2>
          <p className="mt-2 text-sm text-gray-500">{t('loginHelp')}</p>
          <form onSubmit={handleSubmit} className="mt-8 space-y-5">
            <LanguageSelect />
            <label className="block text-sm font-medium text-gray-700">
              {t('email')}
              <input
                type="email"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                placeholder="you@example.com"
                required
                className="mt-2 w-full rounded-xl border border-gray-300 px-4 py-3 outline-none focus:border-green-700"
              />
            </label>
            <label className="block text-sm font-medium text-gray-700">
              {t('password')}
              <input
                type="password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                placeholder="Enter your password"
                required
                className="mt-2 w-full rounded-xl border border-gray-300 px-4 py-3 outline-none focus:border-green-700"
              />
            </label>
            {error && <p className="rounded-xl bg-red-50 p-3 text-sm text-red-700">{error}</p>}
            <button
              type="submit"
              disabled={submitting}
              className="w-full rounded-xl bg-green-700 px-6 py-3 font-medium text-white hover:bg-green-800 disabled:opacity-60"
            >
              {submitting ? t('loggingIn') : t('login')}
            </button>
          </form>
          <div className="mt-6 text-center text-sm text-gray-500">
            {t('noAccount')}{' '}
            <button type="button" onClick={onCreateAccount} className="font-medium text-green-700">
              {t('createAccount')}
            </button>
          </div>
        </div>
      </div>
    </main>
  )
}

export default LoginPage
