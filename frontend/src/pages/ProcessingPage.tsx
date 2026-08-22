import { useI18n } from '../i18n'

function ProcessingPage() {
  const { t } = useI18n()
  return (
    <main className="flex min-h-screen items-center justify-center bg-gray-50 px-6">
      <div className="text-center">
        <div className="mx-auto h-12 w-12 animate-spin rounded-full border-4 border-gray-200 border-t-green-700" />

        <h1 className="mt-6 text-2xl font-bold text-gray-900">
          {t('processingTitle')}
        </h1>

        <p className="mt-2 text-gray-500">
          {t('processingText')}
        </p>
      </div>
    </main>
  )
}

export default ProcessingPage
