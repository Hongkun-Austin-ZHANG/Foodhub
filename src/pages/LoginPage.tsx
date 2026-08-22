import { useState } from 'react'

interface LoginPageProps {
  onLogin: () => void
  onCreateAccount: () => void
}

function LoginPage({
  onLogin,
  onCreateAccount,
}: LoginPageProps) {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')

  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()

    console.log('Login:', {
      email,
      password,
    })

    onLogin()
  }

  return (
    <main className="flex min-h-screen items-center justify-center bg-gray-50 px-6">
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
            Welcome back
          </h2>

          <p className="mt-2 text-sm text-gray-500">
            Log in to continue to FoodHub.
          </p>

          <form
            onSubmit={handleSubmit}
            className="mt-8 space-y-5"
          >
            <div>
              <label
                htmlFor="email"
                className="text-sm font-medium text-gray-700"
              >
                Email
              </label>

              <input
                id="email"
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
                htmlFor="password"
                className="text-sm font-medium text-gray-700"
              >
                Password
              </label>

              <input
                id="password"
                type="password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                placeholder="Enter your password"
                required
                className="mt-2 w-full rounded-xl border border-gray-300 px-4 py-3 outline-none focus:border-green-700"
              />
            </div>

            <button
              type="submit"
              className="w-full rounded-xl bg-green-700 px-6 py-3 font-medium text-white hover:bg-green-800"
            >
              Log in
            </button>
          </form>

          <div className="mt-6 text-center text-sm text-gray-500">
            Don't have an account?{' '}
            <button
              type="button"
              onClick={onCreateAccount}
              className="font-medium text-green-700 hover:text-green-800"
            >
              Create account
            </button>
          </div>
        </div>
      </div>
    </main>
  )
}

export default LoginPage