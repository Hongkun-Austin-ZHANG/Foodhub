# FoodHub frontend integration contract

## Authentication

Register or log in, then send the token on protected requests:

```http
Authorization: Bearer <access_token>
```

```text
POST /api/auth/register   POST /api/auth/login
GET /api/auth/me          POST /api/auth/logout
GET /api/profile          PATCH /api/profile
```

Recommended payloads:

```json
{
  "name": "Mao",
  "email": "mao@example.com",
  "password": "StrongPassword_2026!",
  "preferred_language": "zh"
}
```

```json
{
  "email": "mao@example.com",
  "password": "StrongPassword_2026!"
}
```

The frontend sets `preferred_language` through the profile. It does not send a
translation language with every menu image.

## Preference form

Fetch stable codes from `GET /api/preferences/options`. Save the complete form
with `PUT /api/preferences/profile` and load it with
`GET /api/preferences/profile`.

```json
{
  "allergies": ["peanut", "molluscs"],
  "dietary_restrictions": ["vegetarian"],
  "religious_restrictions": ["no_pork"],
  "preferred_proteins": ["chicken"],
  "preferred_flavours": ["savoury"],
  "preferred_textures": ["crispy"],
  "spice_level": "medium",
  "disliked_ingredients": ["mushroom"]
}
```

Canonical allergens are:

```text
peanut, tree_nuts, milk, egg, fish, shellfish, molluscs, gluten, soy,
sesame, mustard, celery, lupin, sulfites
```

The API temporarily accepts `peanuts`, `eggs`, and `sulphites`, but the frontend
should store the canonical values returned by the API. `PUT` replaces the whole
preference profile, so always send every field.

## Final menu upload and recommendation

The frontend calls only the main backend:

```http
POST /api/menu/scan
Authorization: Bearer <access_token>
Content-Type: multipart/form-data
```

Form fields:

```text
menu_images       repeat this field for 1–5 JPEG, PNG, or WebP pages
```

The backend internally calls B, TheMealDB, MySQL, fallback analysis, allergen
mapping, and recommendation rules. The browser does not orchestrate those
services. It stores the result under the returned `menu_id`.

The response contains:

```text
menu_id
source_language
target_language
analysis_complete
effective_preferences
dishes[]
fallback_batch_request
```

Each dish contains:

```text
dish.original_name
dish.translated_name
dish.canonical_name_en
dish.menu_description
dish.translated_description
resolution_status
match_score
image_url
image_is_reference
evidence.explicit_ingredients
evidence.reference_ingredients
evidence.inferred_ingredients
evidence.allergen_assessments
decision.status
decision.reasons
decision.warnings
```

The frontend displays the evidence but does not recalculate the recommendation.
Keep explicit, reference, and inferred evidence visually distinct. The three
decision values are `good_match`, `check_with_staff`, and `avoid`.

For the user's current-meal choices, call:

```http
POST /api/recommendations
Authorization: Bearer <access_token>
Content-Type: application/json
```

```json
{
  "menu_id": "uuid-from-scan",
  "current_preference": {
    "preferred_proteins": ["fish"],
    "preferred_flavours": ["savoury"],
    "preferred_textures": ["crispy"],
    "spice_level": "medium"
  }
}
```

Render `recommendations[]` in `rank` order. Each item contains the same nested
`dish`, `evidence`, `decision`, and optional `image_url` fields plus
`preference_score`, `matched_preferences`, and `preference_tags`. Display
`dish.translated_name` and `dish.translated_description` when present; fall back
to the original fields. Recommendation reasons and warnings are also localized
for English, Chinese, and French according to the saved `preferred_language`.

There is no universal `{ data: ... }` response wrapper. Normal API errors use
`{ "detail": "message" }`; validation errors have a `detail` array.

`POST /api/recommendation/analyze-image` remains as a backwards-compatible
single-image endpoint. `POST /api/recommendation/analyze` remains available for
testing already parsed B JSON. Neither is the preferred browser flow.
