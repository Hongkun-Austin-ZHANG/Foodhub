import { useI18n } from '../i18n'
import type { AnalyzedDish } from '../types/MenuDish'

export default function DishDetails({ item }: { item: AnalyzedDish }) {
  const { optionLabel, t } = useI18n()
  const displayEvidence = item.evidence.display
  const explicitIngredients = displayEvidence?.explicit_ingredients?.length
    ? displayEvidence.explicit_ingredients
    : item.evidence.explicit_ingredients
  const referenceIngredients = displayEvidence?.reference_ingredients?.length
    ? displayEvidence.reference_ingredients
    : item.evidence.reference_ingredients
  const section = (title: string, values: string[], tone = 'bg-gray-100 text-gray-700') => values.length > 0 && (
    <div className="mt-4">
      <h4 className="text-sm font-semibold text-gray-900">{title}</h4>
      <div className="mt-2 flex flex-wrap gap-2">{values.map((value) => <span key={value} className={`rounded-full px-3 py-1 text-xs ${tone}`}>{value}</span>)}</div>
    </div>
  )

  return (
    <div className="mt-5 border-t border-gray-100 pt-5">
      <div className="grid gap-2 text-sm text-gray-600 sm:grid-cols-3">
        {item.enrichment.cuisine && <p><span className="font-semibold text-gray-900">{t('cuisine')}:</span> {item.enrichment.display_cuisine || item.enrichment.cuisine}</p>}
        <p><span className="font-semibold text-gray-900">{t('source')}:</span> {t(item.enrichment.source)}</p>
        {item.enrichment.confidence !== null && <p><span className="font-semibold text-gray-900">{t('confidence')}:</span> {Math.round(item.enrichment.confidence * 100)}%</p>}
      </div>
      {section(t('menuIngredients'), explicitIngredients, 'bg-green-50 text-green-800')}
      {section(t('referenceIngredients'), referenceIngredients, 'bg-blue-50 text-blue-800')}
      {item.evidence.inferred_ingredients.length > 0 && (
        <div className="mt-4">
          <h4 className="text-sm font-semibold text-gray-900">{t('inferredIngredients')}</h4>
          <ul className="mt-2 space-y-2 text-sm text-gray-600">{item.evidence.inferred_ingredients.map((ingredient, index) => { const display = displayEvidence?.inferred_ingredients?.[index]; return <li key={ingredient.name} className="rounded-lg bg-purple-50 p-3"><span className="font-medium text-purple-900">{display?.name || ingredient.name}</span>{ingredient.confidence !== null && ` · ${Math.round(ingredient.confidence * 100)}%`}{(display?.reasoning || ingredient.reasoning) && <p className="mt-1 text-xs text-purple-700">{display?.reasoning || ingredient.reasoning}</p>}</li> })}</ul>
        </div>
      )}
      {item.evidence.allergen_assessments.length > 0 && (
        <div className="mt-4">
          <h4 className="text-sm font-semibold text-gray-900">{t('allergenEvidence')}</h4>
          <div className="mt-2 space-y-2">{item.evidence.allergen_assessments.map((assessment) => <div key={`${assessment.code}-${assessment.evidence_source}`} className={`rounded-lg border p-3 text-sm ${assessment.status === 'contains' ? 'border-red-200 bg-red-50 text-red-800' : 'border-amber-200 bg-amber-50 text-amber-800'}`}><span className="font-semibold">{optionLabel(assessment.code)}</span> · {t(assessment.status)} · {t(assessment.evidence_source)}</div>)}</div>
        </div>
      )}
    </div>
  )
}
