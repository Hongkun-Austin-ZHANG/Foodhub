import type { RankedRecommendation } from '../types/Recommendation'

interface RecommendationCardProps {
  recommendation: RankedRecommendation
}

const statusStyles = {
  good_match: 'bg-green-100 text-green-800',
  check_with_staff: 'bg-amber-100 text-amber-800',
  avoid: 'bg-red-100 text-red-800',
}

const statusLabels = {
  good_match: 'Good Match',
  check_with_staff: 'Check With Staff',
  avoid: 'Avoid',
}

function RecommendationCard({ recommendation }: RecommendationCardProps) {
  const name = recommendation.dish.translated_name || recommendation.dish.original_name
  const price = recommendation.dish.price_text

  return (
    <article className="overflow-hidden rounded-2xl border border-gray-200 bg-white shadow-sm">
      <div className="flex flex-col md:flex-row">
        {recommendation.image_url && (
          <div className="border-b border-gray-100 md:w-44 md:flex-shrink-0 md:border-b-0 md:border-r">
            <img src={recommendation.image_url} alt={name} className="h-48 w-full object-cover md:h-40" />
          </div>
        )}
        <div className="min-w-0 flex-1 p-6">
          <div className="flex items-start justify-between gap-4">
            <div>
              <p className="text-xs font-semibold text-green-700">#{recommendation.rank} · {Math.round(recommendation.preference_score * 100)}% preference match</p>
              <h3 className="mt-1 text-xl font-bold text-gray-900">{name}</h3>
              {price && <p className="mt-1 text-gray-500">{price}</p>}
            </div>
            <span className={`shrink-0 rounded-full px-3 py-1 text-xs font-semibold ${statusStyles[recommendation.decision.status]}`}>
              {statusLabels[recommendation.decision.status]}
            </span>
          </div>
          {recommendation.decision.reasons.length > 0 && (
            <ul className="mt-5 space-y-1 text-sm text-gray-600">
              {recommendation.decision.reasons.map((reason) => <li key={reason}>• {reason}</li>)}
            </ul>
          )}
          {recommendation.decision.warnings.length > 0 && (
            <div className="mt-5 rounded-xl bg-amber-50 p-4 text-sm text-amber-800">
              {recommendation.decision.warnings.map((warning) => <p key={warning}>• {warning}</p>)}
            </div>
          )}
        </div>
      </div>
    </article>
  )
}

export default RecommendationCard
