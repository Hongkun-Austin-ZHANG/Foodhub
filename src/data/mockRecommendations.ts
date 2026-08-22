import type { Recommendation } from '../types/Recommendation'

export const mockRecommendations: Recommendation[] = [
  {
    name: 'Beef Tartare',
    price: '€24',
    match_status: 'best_match',
    image_url: 'https://images.immediate.co.uk/production/volatile/sites/30/2023/09/Steak-Tartare-c0d766e.jpg?quality=90&webp=true&resize=800,726',
    taste: ['savoury', 'rich'],
    texture: ['tender'],
    ingredients: ['beef', 'capers', 'shallots', 'mustard'],
    reasons: [
      'Matches your beef preference',
      'Matches your savoury flavour preference',
    ],
    warnings: [],
    source: 'database',
    confidence: 'high',
  },
  {
    name: 'Ratatouille',
    price: '€18',
    match_status: 'good_match',
    image_url: null,
    taste: ['savoury', 'light'],
    texture: ['soft'],
    ingredients: [
      'zucchini',
      'eggplant',
      'tomato',
      'bell pepper',
    ],
    reasons: [
      'Matches your savoury flavour preference',
      'A lighter option from this menu',
    ],
    warnings: [],
    source: 'database',
    confidence: 'high',
  },
  {
    name: 'French Onion Soup',
    price: '€14',
    match_status: 'check_with_staff',
    image_url: null,
    taste: ['savoury', 'rich'],
    texture: ['brothy'],
    ingredients: [
      'onions',
      'broth',
      'toasted bread',
      'cheese',
    ],
    reasons: [
      'Matches your savoury flavour preference',
    ],
    warnings: [
      'The menu does not provide enough information to confirm all dietary requirements.',
      'Please check with staff before ordering.',
    ],
    source: 'menu',
    confidence: 'medium',
  },
]