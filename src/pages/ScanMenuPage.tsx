import { useState } from 'react'

interface MenuPage {
  file: File
  preview: string
}

interface ScanMenuPageProps {
  onScan: () => void
}

function ScanMenuPage({ onScan }: ScanMenuPageProps) {
  const [menuPages, setMenuPages] = useState<MenuPage[]>([])

  const handleFileUpload = (file: File | undefined) => {
    if (!file) return

    const reader = new FileReader()

    reader.onload = () => {
      setMenuPages((current) => [
        ...current,
        {
          file,
          preview: reader.result as string,
        },
      ])
    }

    reader.readAsDataURL(file)
  }

  const removePage = (index: number) => {
    setMenuPages((current) =>
      current.filter((_, pageIndex) => pageIndex !== index)
    )
  }

  const handleScan = () => {
    if (menuPages.length === 0) return

    console.log(
      'Menu pages ready to scan:',
      menuPages.map((page) => page.file)
    )

    onScan()
  }

  return (
    <main className="min-h-screen bg-gray-50">
      <header className="border-b border-gray-200 bg-white">
        <div className="mx-auto max-w-4xl px-6 py-6">
          <h1 className="text-2xl font-bold text-green-700">
            FoodHub
          </h1>

          <p className="mt-1 text-sm text-gray-500">
            Understand what you're actually ordering.
          </p>
        </div>
      </header>

      <div className="mx-auto max-w-2xl px-6 py-12">
        <h2 className="text-3xl font-bold text-gray-900">
          Scan your menu
        </h2>

        <p className="mt-3 text-gray-600">
          Upload a photo of the menu and we'll help you understand
          what you're ordering.
        </p>

        {menuPages.length === 0 ? (
          <label className="mt-8 flex cursor-pointer flex-col items-center justify-center rounded-2xl border-2 border-dashed border-gray-300 bg-white px-6 py-16 text-center hover:border-green-600">
            <span className="text-lg font-medium text-gray-900">
              Upload menu photo
            </span>

            <span className="mt-2 text-sm text-gray-500">
              JPG, PNG or HEIC
            </span>

            <input
              type="file"
              accept="image/*"
              className="hidden"
              onChange={(event) => {
                handleFileUpload(event.target.files?.[0])
                event.currentTarget.value = ''
              }}
            />
          </label>
        ) : (
          <div className="mt-8 space-y-4">
            {menuPages.map((page, index) => (
              <div
                key={`${page.file.name}-${index}`}
                className="rounded-2xl border border-gray-200 bg-white p-4 shadow-sm"
              >
                <div className="flex items-center justify-between">
                  <p className="font-medium text-gray-900">
                    Page {index + 1}
                  </p>

                  <button
                    type="button"
                    onClick={() => removePage(index)}
                    className="text-sm text-red-600 hover:text-red-700"
                  >
                    Remove
                  </button>
                </div>

                <img
                  src={page.preview}
                  alt={`Menu page ${index + 1}`}
                  className="mt-4 max-h-96 w-full rounded-xl object-contain"
                />
              </div>
            ))}

            <label className="flex cursor-pointer items-center justify-center rounded-xl border border-gray-300 bg-white px-5 py-3 font-medium text-gray-700 hover:border-green-600 hover:text-green-700">
              + Add another page

              <input
                type="file"
                accept="image/*"
                className="hidden"
                onChange={(event) => {
                  handleFileUpload(event.target.files?.[0])
                  event.currentTarget.value = ''
                }}
              />
            </label>

            <button
              type="button"
              onClick={handleScan}
              className="w-full rounded-xl bg-green-700 px-6 py-3 font-medium text-white hover:bg-green-800"
            >
              Scan Menu
            </button>
          </div>
        )}
      </div>
    </main>
  )
}

export default ScanMenuPage