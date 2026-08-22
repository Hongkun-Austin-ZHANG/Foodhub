import type { MenuDish } from '../types/MenuDish'

interface DishCardProps {
  dish: MenuDish
}

function DishCard({ dish }: DishCardProps) {
  return (
  <div className="max-w-md rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
    <h2 className="text-2xl font-bold">
      {dish.translated_name}
    </h2>

    <p className="mt-1 text-sm text-gray-500">
      {dish.original_name}
    </p>

    <p className="mt-2 text-lg">
      {dish.price}
    </p>

    {dish.translated_description && (
      <p className="mt-3 text-gray-600">
        {dish.translated_description}
      </p>
    )}

    {dish.explicit_ingredients.length > 0 && (
        <div className="mt-4">
            <p className="text-sm font-medium text-gray-700">
                Ingredients
            </p>

            <p className="mt-1 text-sm text-gray-500">
                {dish.explicit_ingredients.join(', ')}
            </p>
        </div>
    )}
  </div>
)
}

export default DishCard