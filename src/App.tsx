import DishCard from './components/DishCard'
import { mockMenu } from './data/mockMenu'

function App() {
  return (
  <div className="p-8">
    <div className="mb-8">
      <h1 className="text-3xl font-bold">
        Your Menu
      </h1>

      <p className="mt-2 text-gray-500">
        {mockMenu.length} dishes found
      </p>
    </div>

    <div className="space-y-6">
      {mockMenu.map((dish) => (
        <DishCard
          key={dish.original_name}
          dish={dish}
        />
      ))}
    </div>
  </div>
)
}

export default App