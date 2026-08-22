import type { Language } from '../i18n'
import type { MenuDish } from '../types/MenuDish'

const locales: Record<Language, string> = {
  en: 'en-AU',
  zh: 'zh-CN',
  fr: 'fr-FR',
}

const priceLabels: Record<Language, string> = {
  en: 'Price',
  zh: '价格',
  fr: 'Prix',
}

export function formatDishPrice(dish: MenuDish, language: Language) {
  const rawPrice = dish.price_text?.trim()
  const normalizedPrice = rawPrice?.replace(',', '.')
  const numeric = Number(dish.price ?? normalizedPrice)

  // If the currency was recognized, format it normally.
  if (dish.currency && Number.isFinite(numeric)) {
    return new Intl.NumberFormat(locales[language], {
      style: 'currency',
      currency: dish.currency,
    }).format(numeric)
  }

  // Preserve a currency symbol already found by OCR.
  if (rawPrice) {
    const hasCurrency =
      /[€$£¥₹₩₽]/.test(rawPrice) ||
      /\b(AUD|USD|EUR|GBP|CNY|RMB|JPY|CAD|CHF)\b/i.test(rawPrice)

    return hasCurrency
      ? rawPrice
      : `${priceLabels[language]}: ${rawPrice}`
  }

  if (dish.price !== null) {
    return `${priceLabels[language]}: ${dish.price}`
  }

  return null
}
