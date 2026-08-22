import { useState } from 'react'
import { useI18n } from '../i18n'
import type { RankedRecommendation } from '../types/Recommendation'
import { formatDishPrice } from '../utils/format'
import DishDetails from './DishDetails'

const statusStyles = { good_match: 'bg-green-100 text-green-800', check_with_staff: 'bg-amber-100 text-amber-800', avoid: 'bg-red-100 text-red-800' }

export default function RecommendationCard({ recommendation }: { recommendation: RankedRecommendation }) {
  const { language, t } = useI18n()
  const [expanded, setExpanded] = useState(false)
  const name = recommendation.dish.translated_name || recommendation.dish.original_name
  const price = formatDishPrice(recommendation.dish, language)
  return (
    <article className="overflow-hidden rounded-2xl border border-gray-200 bg-white shadow-sm">
      <div className="flex flex-col md:flex-row">
        {recommendation.image_url && <img src={recommendation.image_url} alt={name} className="h-48 w-full object-cover md:h-auto md:w-44" />}
        <div className="min-w-0 flex-1 p-6">
          <div className="flex items-start justify-between gap-4">
            <div><p className="text-xs font-semibold text-green-700">#{recommendation.rank} · {Math.round(recommendation.preference_score * 100)}% {t('preferenceMatch')}</p><h3 className="mt-1 text-xl font-bold text-gray-900">{name}</h3>{price && <p className="mt-1 text-gray-500">{price}</p>}</div>
            <span className={`shrink-0 rounded-full px-3 py-1 text-xs font-semibold ${statusStyles[recommendation.decision.status]}`}>{t(recommendation.decision.status)}</span>
          </div>
          <div className="mt-5"><h4 className="text-sm font-semibold text-gray-900">{t('why')}</h4><ul className="mt-2 space-y-1 text-sm text-gray-600">{recommendation.decision.reasons.slice(0, 3).map((reason) => <li key={reason}>• {reason}</li>)}</ul></div>
          <button type="button" onClick={() => setExpanded((value) => !value)} className="mt-5 text-sm font-semibold text-green-700">{expanded ? t('hideDetails') : t('details')}</button>
          {expanded && <DishDetails item={recommendation} />}
        </div>
      </div>
    </article>
  )
}
