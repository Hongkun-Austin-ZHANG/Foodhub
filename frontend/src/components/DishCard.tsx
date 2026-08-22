import type { AnalyzedDish } from '../types/MenuDish'

interface DishCardProps {
  item: AnalyzedDish
}

function DishCard({ item }: DishCardProps) {
  const { dish } = item
  const displayName = dish.translated_name || dish.original_name
  const description = dish.translated_description || dish.menu_description
  const price = dish.price_text || (dish.price !== null ? `${dish.currency ?? ''} ${dish.price}`.trim() : null)

  return (
    <article className="overflow-hidden rounded-2xl border border-gray-200 bg-white shadow-sm">
      {item.image_url && (
        <div>
          <img src={item.image_url} alt={displayName} className="h-52 w-full object-cover" />
          {item.image_is_reference && <p className="px-6 pt-2 text-xs text-gray-400">Reference image</p>}
        </div>
      )}
      <div className="p-6">
        <div className="flex items-start justify-between gap-4">
          <div>
            <h2 className="text-xl font-bold text-gray-900">{displayName}</h2>
            {displayName !== dish.original_name && <p className="mt-1 text-sm text-gray-500">{dish.original_name}</p>}
          </div>
          {price && <p className="font-semibold text-gray-900">{price}</p>}
        </div>
        {description && <p className="mt-4 text-sm leading-6 text-gray-600">{description}</p>}
        {dish.explicit_ingredients.length > 0 && (
          <div className="mt-5">
            <p className="text-sm font-semibold text-gray-900">Menu-listed ingredients</p>
            <div className="mt-2 flex flex-wrap gap-2">
              {dish.explicit_ingredients.map((ingredient) => (
                <span key={ingredient} className="rounded-full bg-gray-100 px-3 py-1 text-xs text-gray-600">{ingredient}</span>
              ))}
            </div>
          </div>
        )}
      </div>
    </article>
  )
}

export default DishCard
