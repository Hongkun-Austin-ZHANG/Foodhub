import type { MenuDish } from '../types/MenuDish'

export const mockMenu: MenuDish[] = [
  {
    original_name: 'Tartare de Boeuf',
    translated_name: 'Beef Tartare',
    canonical_guess: 'Beef Tartare',
    price: '€24',
    menu_description: 'Câpres, échalotes, moutarde',
    translated_description: 'Capers, shallots and mustard',
    explicit_ingredients: ['capers', 'shallots', 'mustard'],
    source_text: 'Tartare de Boeuf €24 — Câpres, échalotes, moutarde',
    extraction_confidence: 'high',
    menu_language: 'French',
    image_url: 'https://images.immediate.co.uk/production/volatile/sites/30/2023/09/Steak-Tartare-c0d766e.jpg?quality=90&webp=true&resize=800,726',
  },
  {
    original_name: 'Soupe à l’Oignon',
    translated_name: 'French Onion Soup',
    canonical_guess: 'French Onion Soup',
    price: '€14',
    menu_description: 'Oignons, bouillon, pain grillé, fromage',
    translated_description: 'Onions, broth, toasted bread and cheese',
    explicit_ingredients: ['onions', 'broth', 'toasted bread', 'cheese'],
    source_text:
      'Soupe à l’Oignon €14 — Oignons, bouillon, pain grillé, fromage',
    extraction_confidence: 'high',
    menu_language: 'French',
    image_url: null,
  },
  {
    original_name: 'Ratatouille',
    translated_name: 'Ratatouille',
    canonical_guess: 'Ratatouille',
    price: '€18',
    menu_description: 'Courgette, aubergine, tomate, poivron',
    translated_description: 'Zucchini, eggplant, tomato and bell pepper',
    explicit_ingredients: [
      'zucchini',
      'eggplant',
      'tomato',
      'bell pepper',
    ],
    source_text:
      'Ratatouille €18 — Courgette, aubergine, tomate, poivron',
    extraction_confidence: 'high',
    menu_language: 'French',
    image_url: null,
  },
]