import DishCard from './components/DishCard'
import { mockMenu } from './data/mockMenu'

function App() {
  const dish = mockMenu[0]

  return (
    <div className="p-8">
      <DishCard dish={dish} />
    </div>
  )
}

export default App