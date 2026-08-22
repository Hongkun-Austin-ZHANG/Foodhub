import type { MenuDish } from '../types/MenuDish'

export const mockMenu: MenuDish[] = [
  {
    original_name: 'Tartare de Boeuf',
    translated_name: 'Beef Tartare',
    canonical_guess: 'Beef Tartare',

    price: '€24',

    menu_description: 'Câpres, échalotes, moutarde',
    translated_description: 'Capers, shallots and mustard',

    explicit_ingredients: [
      'capers',
      'shallots',
      'mustard',
    ],

    source_text: 'Tartare de Boeuf €24 — Câpres, échalotes, moutarde',

    extraction_confidence: 'high',
    menu_language: 'French',
  },
]