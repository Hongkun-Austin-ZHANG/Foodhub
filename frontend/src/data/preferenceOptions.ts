export interface PreferenceOption {
  value: string
  label: string
}

export const allergyOptions: PreferenceOption[] = [
  { value: 'peanut', label: 'Peanuts' },
  { value: 'tree_nuts', label: 'Tree Nuts' },
  { value: 'milk', label: 'Milk / Dairy' },
  { value: 'egg', label: 'Eggs' },
  { value: 'fish', label: 'Fish' },
  { value: 'shellfish', label: 'Shellfish' },
  { value: 'molluscs', label: 'Molluscs' },
  { value: 'gluten', label: 'Wheat / Gluten' },
  { value: 'soy', label: 'Soy' },
  { value: 'sesame', label: 'Sesame' },
  { value: 'mustard', label: 'Mustard' },
  { value: 'celery', label: 'Celery' },
  { value: 'lupin', label: 'Lupin' },
  { value: 'sulfites', label: 'Sulphites' },
]

export const dietaryRestrictionOptions: PreferenceOption[] = [
  { value: 'vegetarian', label: 'Vegetarian' },
  { value: 'vegan', label: 'Vegan' },
  { value: 'pescatarian', label: 'Pescatarian' },
  { value: 'gluten_free', label: 'Gluten-free' },
  { value: 'dairy_free', label: 'Dairy-free' },
  { value: 'lactose_free', label: 'Lactose-free' },
  { value: 'egg_free', label: 'Egg-free' },
]

export const religiousRestrictionOptions: PreferenceOption[] = [
  { value: 'halal_required', label: 'Halal' },
  { value: 'no_pork', label: 'No pork' },
  { value: 'kosher_required', label: 'Kosher' },
  { value: 'no_beef', label: 'No beef' },
  { value: 'no_alcohol', label: 'No alcohol' },
]

export const preferredProteinOptions: PreferenceOption[] = [
  { value: 'beef', label: 'Beef' },
  { value: 'lamb', label: 'Lamb' },
  { value: 'chicken', label: 'Chicken' },
  { value: 'duck', label: 'Duck' },
  { value: 'pork', label: 'Pork' },
  { value: 'fish', label: 'Fish' },
  { value: 'shellfish', label: 'Shellfish' },
  { value: 'plant_based', label: 'Plant-based' },
]

export const preferredFlavourOptions: PreferenceOption[] = [
  { value: 'savoury', label: 'Savoury' },
  { value: 'rich', label: 'Rich' },
  { value: 'light', label: 'Light' },
  { value: 'creamy', label: 'Creamy' },
  { value: 'herby', label: 'Herby' },
  { value: 'smoky', label: 'Smoky' },
  { value: 'tangy', label: 'Tangy' },
  { value: 'sweet', label: 'Sweet' },
]

export const preferredTextureOptions: PreferenceOption[] = [
  { value: 'crispy', label: 'Crispy' },
  { value: 'tender', label: 'Tender' },
  { value: 'creamy', label: 'Creamy' },
  { value: 'crunchy', label: 'Crunchy' },
  { value: 'soft', label: 'Soft' },
  { value: 'chewy', label: 'Chewy' },
  { value: 'brothy', label: 'Brothy' },
]

export const spiceLevelOptions: PreferenceOption[] = [
  { value: 'mild', label: 'Mild' },
  { value: 'medium', label: 'Medium' },
  { value: 'hot', label: 'Hot' },
]
