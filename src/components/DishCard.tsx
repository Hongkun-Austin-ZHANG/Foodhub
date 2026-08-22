import type { MenuDish } from '../types/MenuDish'

interface DishCardProps {
  dish: MenuDish
}

function DishCard({ dish }: DishCardProps) {
    return (
        <article className="overflow-hidden rounded-2xl border border-gray-200 bg-white shadow-sm">
        {dish.image_url && (
            <div>
            <img
                src={dish.image_url}
                alt={dish.translated_name}
                className="h-52 w-full object-cover"
            />

            <p className="px-6 pt-2 text-xs text-gray-400">
                Reference image
            </p>
            </div>
        )}

        <div className="p-6">
            <div className="flex items-start justify-between gap-4">
            <div>
                <h2 className="text-xl font-bold text-gray-900">
                {dish.translated_name}
                </h2>

                <p className="mt-1 text-sm text-gray-500">
                {dish.original_name}
                </p>
            </div>

            <p className="font-semibold text-gray-900">
                {dish.price}
            </p>
            </div>

            {dish.translated_description && (
            <p className="mt-4 text-sm leading-6 text-gray-600">
                {dish.translated_description}
            </p>
            )}

            {dish.explicit_ingredients.length > 0 && (
            <div className="mt-5">
                <p className="text-sm font-semibold text-gray-900">
                Ingredients
                </p>

                <div className="mt-2 flex flex-wrap gap-2">
                {dish.explicit_ingredients.map((ingredient) => (
                    <span
                    key={ingredient}
                    className="rounded-full bg-gray-100 px-3 py-1 text-xs text-gray-600"
                    >
                    {ingredient}
                    </span>
                ))}
                </div>
            </div>
            )}
        </div>
        </article>
    )
}

export default DishCard