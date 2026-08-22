import { useState } from 'react'
import { register } from '../services/authApi'
import LanguageSelect from '../components/LanguageSelect'
import { useI18n } from '../i18n'

interface RegisterPageProps {
  onRegister: () => void
  onBackToLogin: () => void
}

function RegisterPage({ onRegister, onBackToLogin }: RegisterPageProps) {
  const { language, t } = useI18n()
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    if (password !== confirmPassword) {
      setError('Passwords do not match.')
      return
    }
    setError(null)
    setSubmitting(true)
    try {
      await register({ name, email, preferred_language: language, password })
      onRegister()
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'Registration failed.')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <main className="flex min-h-screen items-center justify-center bg-gray-50 px-6 py-12">
      <div className="w-full max-w-md rounded-2xl border border-gray-200 bg-white p-8 shadow-sm">
        <h1 className="text-3xl font-bold text-green-700">FoodHub</h1>
        <h2 className="mt-6 text-2xl font-bold text-gray-900">{t('createTitle')}</h2>
        <form onSubmit={handleSubmit} className="mt-8 space-y-5">
          <label className="block text-sm font-medium text-gray-700">
            {t('name')}
            <input value={name} onChange={(event) => setName(event.target.value)} required className="mt-2 w-full rounded-xl border border-gray-300 px-4 py-3" />
          </label>
          <label className="block text-sm font-medium text-gray-700">
            {t('email')}
            <input type="email" value={email} onChange={(event) => setEmail(event.target.value)} required className="mt-2 w-full rounded-xl border border-gray-300 px-4 py-3" />
          </label>
          <LanguageSelect />
          <label className="block text-sm font-medium text-gray-700">
            {t('password')}
            <input type="password" minLength={8} value={password} onChange={(event) => setPassword(event.target.value)} required className="mt-2 w-full rounded-xl border border-gray-300 px-4 py-3" />
          </label>
          <label className="block text-sm font-medium text-gray-700">
            {t('confirmPassword')}
            <input type="password" minLength={8} value={confirmPassword} onChange={(event) => setConfirmPassword(event.target.value)} required className="mt-2 w-full rounded-xl border border-gray-300 px-4 py-3" />
          </label>
          {error && <p className="rounded-xl bg-red-50 p-3 text-sm text-red-700">{error}</p>}
          <button type="submit" disabled={submitting} className="w-full rounded-xl bg-green-700 px-6 py-3 font-medium text-white disabled:opacity-60">
            {submitting ? t('creatingAccount') : t('createAccount')}
          </button>
        </form>
        <button type="button" onClick={onBackToLogin} className="mt-5 w-full text-sm font-medium text-green-700">
          {t('backToLogin')}
        </button>
      </div>
    </main>
  )
}

export default RegisterPage
