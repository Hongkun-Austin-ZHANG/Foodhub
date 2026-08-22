import type { Recommendation } from '../types/Recommendation'

interface RecommendationCardProps {
  recommendation: Recommendation
}

function RecommendationCard({
  recommendation,
}: RecommendationCardProps) {
  const statusStyles = {
    best_match: 'bg-green-100 text-green-800',
    good_match: 'bg-blue-100 text-blue-800',
    check_with_staff: 'bg-amber-100 text-amber-800',
    not_suitable: 'bg-red-100 text-red-800',
  }

  const statusLabels = {
    best_match: 'Best Match',
    good_match: 'Good Match',
    check_with_staff: 'Check With Staff',
    not_suitable: 'Not Suitable',
  }

    return (
    <article className="overflow-hidden rounded-2xl border border-gray-200 bg-white shadow-sm">
      <div className="flex flex-col md:flex-row">

        {recommendation.image_url && (
          <div className="border-b border-gray-100 md:w-44 md:flex-shrink-0 md:border-b-0 md:border-r">
            <img
              src={recommendation.image_url}
              alt={recommendation.name}
              className="h-48 w-full object-cover md:h-40"
            />

            <p className="px-3 py-2 text-center text-xs text-gray-400">
              Reference image
            </p>
          </div>
        )}

        <div className="min-w-0 flex-1 p-6">
          <div className="flex items-start justify-between gap-4">
            <div>
              <h3 className="text-xl font-bold text-gray-900">
                {recommendation.name}
              </h3>

              {recommendation.price && (
                <p className="mt-1 text-gray-500">
                  {recommendation.price}
                </p>
              )}
            </div>

            <span
              className={`shrink-0 rounded-full px-3 py-1 text-xs font-semibold ${
                statusStyles[recommendation.match_status]
              }`}
            >
              {statusLabels[recommendation.match_status]}
            </span>
          </div>

          {recommendation.reasons.length > 0 && (
            <div className="mt-5">
              <h4 className="text-sm font-semibold text-gray-900">
                Why this matches you
              </h4>

              <ul className="mt-2 space-y-1 text-sm text-gray-600">
                {recommendation.reasons.map((reason) => (
                  <li key={reason}>
                    • {reason}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {recommendation.warnings.length > 0 && (
            <div className="mt-5 rounded-xl bg-amber-50 p-4">
              <h4 className="text-sm font-semibold text-amber-900">
                Important
              </h4>

              <ul className="mt-2 space-y-1 text-sm text-amber-800">
                {recommendation.warnings.map((warning) => (
                  <li key={warning}>
                    • {warning}
                  </li>
                ))}
              </ul>
            </div>
          )}

          <div className="mt-5 flex flex-wrap gap-2 text-xs">
            <span className="rounded-full bg-gray-100 px-3 py-1 text-gray-600">
              Source: {recommendation.source}
            </span>

            <span className="rounded-full bg-gray-100 px-3 py-1 text-gray-600">
              Confidence: {recommendation.confidence}
            </span>
          </div>
        </div>

      </div>
    </article>
  )
    
}

export default RecommendationCard