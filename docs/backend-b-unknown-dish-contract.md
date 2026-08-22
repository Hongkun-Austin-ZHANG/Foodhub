# Backend B batched fallback-dish contract

FoodHub C checks MySQL and TheMealDB first, then sends every confirmed miss from
one menu to Backend B in one structured OpenAI call. A temporary TheMealDB
failure is not treated as a miss.

## Request

```json
{
  "schema_version": "1.1",
  "batch_id": "9a3038c8-f17c-4930-b22d-d1b18a3c46b3",
  "dishes": [
    {
      "request_id": "5e7e7260-f87c-4ad1-b305-6e3e2f33514a",
      "original_name": "Escargots Persillade",
      "canonical_name_en": "Escargots",
      "menu_description": "Escargot, Garlic and Parsley Crumbs",
      "explicit_ingredients": ["Escargot", "Garlic and Parsley Crumbs"],
      "source_text": "Escargots Persillade 14/24"
    }
  ]
}
```

## Response

The response echoes `batch_id` and returns exactly one result for every
`request_id`.

```json
{
  "schema_version": "1.1",
  "batch_id": "9a3038c8-f17c-4930-b22d-d1b18a3c46b3",
  "results": [
    {
      "request_id": "5e7e7260-f87c-4ad1-b305-6e3e2f33514a",
      "canonical_name_en": "Escargots Persillade",
      "aliases": ["Garlic Parsley Snails"],
      "description": "A French snail dish prepared with garlic and parsley.",
      "cuisine": "French",
      "inferred_ingredients": [
        {
          "name": "Butter",
          "confidence": 0.9,
          "reasoning": "Common in the traditional preparation."
        }
      ],
      "overall_confidence": 0.85,
      "model_id": "provider-model-version"
    }
  ]
}
```

## Ownership

- B returns neutral culinary facts and `inferred_ingredients` only.
- B does not receive user identity, religion, allergies, or preferences.
- B does not return allergens, dietary suitability, or recommendations.
- C maps explicit, reference, and inferred ingredients to allergens.
- Only explicit restaurant-menu evidence can become `contains`.
- TheMealDB and B inference become `may_contain` and require staff confirmation.
- C saves B results and C-generated allergen evidence in MySQL.

Validate a response with `POST /api/menu/fallback-dishes/validate`.
