import type { Language } from '../i18n'
import type { MenuDish } from '../types/MenuDish'

const locales: Record<Language, string> = { en: 'en-AU', zh: 'zh-CN', fr: 'fr-FR' }

export function formatDishPrice(dish: MenuDish, language: Language) {
  if (dish.price_text) return dish.price_text
  if (dish.price === null) return null
  const numeric = Number(dish.price)
  if (dish.currency && Number.isFinite(numeric)) {
    return new Intl.NumberFormat(locales[language], {
      style: 'currency',
      currency: dish.currency,
    }).format(numeric)
  }
  return String(dish.price)
}
