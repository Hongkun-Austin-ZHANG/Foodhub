import { useState } from 'react'
import { useI18n } from '../i18n'
import type { AnalyzedDish } from '../types/MenuDish'
import { formatDishPrice } from '../utils/format'
import DishDetails from './DishDetails'

const statusStyles = { good_match: 'bg-green-100 text-green-800', check_with_staff: 'bg-amber-100 text-amber-800', avoid: 'bg-red-100 text-red-800' }

export default function DishCard({ item }: { item: AnalyzedDish }) {
  const { language, t } = useI18n()
  const [expanded, setExpanded] = useState(false)
  const { dish } = item
  const displayName = dish.translated_name || dish.original_name
  const description = item.enrichment.display_summary || dish.translated_description || item.enrichment.summary || dish.menu_description
  const price = formatDishPrice(dish, language)
  return (
    <article className="overflow-hidden rounded-2xl border border-gray-200 bg-white shadow-sm">
      {item.image_url && <img src={item.image_url} alt={displayName} className="h-52 w-full object-cover" />}
      <div className="p-6">
        <div className="flex items-start justify-between gap-4">
          <div><h2 className="text-xl font-bold text-gray-900">{displayName}</h2>{displayName !== dish.original_name && <p className="mt-1 text-sm text-gray-500">{t('originalName')}: {dish.original_name}</p>}</div>
          <div className="text-right">{price && <p className="font-semibold text-gray-900">{price}</p>}<span className={`mt-2 inline-block rounded-full px-3 py-1 text-xs font-semibold ${statusStyles[item.decision.status]}`}>{t(item.decision.status)}</span></div>
        </div>
        {description && <p className="mt-4 text-sm leading-6 text-gray-600">{description}</p>}
        {item.decision.reasons[0] && <div className="mt-4 rounded-xl bg-gray-50 p-3 text-sm text-gray-700"><span className="font-semibold">{t('why')}:</span> {item.decision.reasons[0]}</div>}
        <button type="button" onClick={() => setExpanded((value) => !value)} className="mt-5 text-sm font-semibold text-green-700">{expanded ? t('hideDetails') : t('details')}</button>
        {expanded && <DishDetails item={item} />}
      </div>
    </article>
  )
}
