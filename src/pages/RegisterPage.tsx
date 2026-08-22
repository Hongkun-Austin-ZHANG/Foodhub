import { useState } from 'react'

interface RegisterPageProps {
  onRegister: () => void
  onBackToLogin: () => void
}

function RegisterPage({
  onRegister,
  onBackToLogin,
}: RegisterPageProps) {
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [preferredLanguage, setPreferredLanguage] = useState('English')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')

  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()

    if (password !== confirmPassword) {
      alert('Passwords do not match.')
      return
    }

    console.log('Register:', {
      name,
      email,
      preferred_language: preferredLanguage,
      password,
    })

    onRegister()
  }

  return (
    <main className="flex min-h-screen items-center justify-center bg-gray-50 px-6 py-12">
      <div className="w-full max-w-md">
        <div className="mb-8 text-center">
          <h1 className="text-3xl font-bold text-green-700">
            FoodHub
          </h1>

          <p className="mt-2 text-sm text-gray-500">
            Scan a menu. Understand what you're actually ordering.
          </p>
        </div>

        <div className="rounded-2xl border border-gray-200 bg-white p-8 shadow-sm">
          <h2 className="text-2xl font-bold text-gray-900">
            Create your account
          </h2>

          <p className="mt-2 text-sm text-gray-500">
            Set up your FoodHub profile to get started.
          </p>

          <form
            onSubmit={handleSubmit}
            className="mt-8 space-y-5"
          >
            <div>
              <label
                htmlFor="name"
                className="text-sm font-medium text-gray-700"
              >
                Name
              </label>

              <input
                id="name"
                type="text"
                value={name}
                onChange={(event) => setName(event.target.value)}
                placeholder="Your name"
                required
                className="mt-2 w-full rounded-xl border border-gray-300 px-4 py-3 outline-none focus:border-green-700"
              />
            </div>

            <div>
              <label
                htmlFor="register-email"
                className="text-sm font-medium text-gray-700"
              >
                Email
              </label>

              <input
                id="register-email"
                type="email"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                placeholder="you@example.com"
                required
                className="mt-2 w-full rounded-xl border border-gray-300 px-4 py-3 outline-none focus:border-green-700"
              />
            </div>

            <div>
              <label
                htmlFor="preferred-language"
                className="text-sm font-medium text-gray-700"
              >
                Preferred language
              </label>

              <select
                id="preferred-language"
                value={preferredLanguage}
                onChange={(event) =>
                  setPreferredLanguage(event.target.value)
                }
                className="mt-2 w-full rounded-xl border border-gray-300 bg-white px-4 py-3 outline-none focus:border-green-700"
              >
                <option value="English">English</option>
                <option value="Chinese">Chinese</option>
                <option value="French">French</option>
              </select>
            </div>

            <div>
              <label
                htmlFor="register-password"
                className="text-sm font-medium text-gray-700"
              >
                Password
              </label>

              <input
                id="register-password"
                type="password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                placeholder="Create a password"
                required
                className="mt-2 w-full rounded-xl border border-gray-300 px-4 py-3 outline-none focus:border-green-700"
              />
            </div>

            <div>
              <label
                htmlFor="confirm-password"
                className="text-sm font-medium text-gray-700"
              >
                Confirm password
              </label>

              <input
                id="confirm-password"
                type="password"
                value={confirmPassword}
                onChange={(event) =>
                  setConfirmPassword(event.target.value)
                }
                placeholder="Enter your password again"
                required
                className="mt-2 w-full rounded-xl border border-gray-300 px-4 py-3 outline-none focus:border-green-700"
              />
            </div>

            <button
              type="submit"
              className="w-full rounded-xl bg-green-700 px-6 py-3 font-medium text-white hover:bg-green-800"
            >
              Create account
            </button>
          </form>

          <div className="mt-6 text-center text-sm text-gray-500">
            Already have an account?{' '}
            <button
              type="button"
              onClick={onBackToLogin}
              className="font-medium text-green-700 hover:text-green-800"
            >
              Log in
            </button>
          </div>
        </div>
      </div>
    </main>
  )
}

export default RegisterPage