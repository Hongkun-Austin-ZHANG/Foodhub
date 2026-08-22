# FoodHub API contract

## Authentication and user data

Registration and login return an opaque Bearer token. Protected requests send
`Authorization: Bearer <access_token>`.

```text
POST /api/auth/register   POST /api/auth/login
GET  /api/auth/me         POST /api/auth/logout
GET  /api/profile         PATCH /api/profile
```

Frontend registration may send `name`, `email`, `password`, and
`preferred_language`. `username` is optional and is generated when omitted.
Login accepts `email` plus `password`; the legacy `identifier` field remains
supported. Language names and common tags are normalized, for example
`Chinese` and `zh-CN` become `zh`.

The profile stores `display_name`, `gender`, `religion`, `preferred_language`,
and `timezone`. Passwords use Argon2 hashes and session tokens are stored only
as SHA-256 hashes.

## Preferences

```text
GET /api/preferences/options
GET /api/preferences/profile
PUT /api/preferences/profile
GET /api/preferences
POST /api/preferences
PATCH /api/preferences/{code}
DELETE /api/preferences/{code}
```

The grouped `PUT` has full replacement semantics. Daily overrides are sent only
with a recommendation and cannot disable hard safety restrictions.

## Backend B menu contract

B returns `menu_language`, `target_language`, and dishes containing:

```text
original_name
translated_name
canonical_guess
price
menu_description
translated_description
explicit_ingredients
canonical_ingredients_en
translated_explicit_ingredients
source_text
extraction_confidence
```

`explicit_ingredients` preserves the restaurant's menu evidence.
`canonical_guess` and `canonical_ingredients_en` are the English database/rule
matching fields. Translation fields are only for frontend display.
`canonical_ingredients_en` must be a one-to-one English rendering of the menu
evidence and must not add unstated ingredients.
`translated_explicit_ingredients` must contain a one-to-one translation of
`explicit_ingredients` in the same order and must not add culinary knowledge.
Validate B JSON with `POST /api/menu/validate`.

C normalizes confidence bands to numeric values, keeps multi-price text such as
`14/24`, and falls back to `original_name` when `canonical_guess` is null.

## Complete recommendation flow

```text
POST /api/menu/scan                     new multi-page frontend upload
POST /api/recommendations               rerank a saved menu for this meal
POST /api/recommendation/analyze-image   normal frontend upload
POST /api/recommendation/analyze         already-parsed B JSON
POST /api/recommendation/preview         isolated deterministic rule test
```

The preferred frontend flow is now:

```text
profile.preferred_language
  -> POST /api/menu/scan (one or more menu_images fields)
  -> SQL menu_scans row + menu_id
  -> POST /api/recommendations (menu_id + current_preference)
```

`POST /api/menu/scan` accepts 1–5 JPEG, PNG, or WebP files using the repeated
multipart field `menu_images`. All pages are sent to B in one structured call,
then deduplicated and analyzed as one menu. It returns the analyzed menu directly
(there is no `{ "data": ... }` wrapper) and persists it under `menu_id`.

`POST /api/recommendations` accepts:

```json
{
  "menu_id": "uuid-from-menu-scan",
  "current_preference": {
    "preferred_proteins": ["fish"],
    "preferred_flavours": ["savoury"],
    "preferred_textures": ["crispy"],
    "spice_level": "medium"
  }
}
```

Current non-empty selections override the corresponding positive long-term
preference for this meal. Allergies, dietary rules, religious rules, and disliked
ingredients continue to come from SQL and are not weakened by this request.
The response includes `target_language` and ranked `recommendations[]` with
`rank`, `preference_score`, `matched_preferences`, `preference_tags`, dish data,
image metadata, evidence, and the final decision.

All final endpoints except preview require Bearer authentication.

`analyze-image` accepts multipart form data:

```text
image             required JPEG, PNG, or WebP
daily_overrides   optional JSON string, default []
```

It reads `preferred_language` from SQL, calls B, checks MySQL then TheMealDB,
calls B once for all confirmed misses, stores new fallback records, maps
ingredients to allergens, loads the user's preferences, and returns one final
response.

`analyze-image` remains available as a backwards-compatible, one-image, one-shot
endpoint. It does not persist the menu for a later `/api/recommendations` call.

## Response and error conventions

Successful responses are the declared JSON object or array without a universal
outer wrapper. Authentication uses an opaque session Bearer token, not a JWT and
not a browser cookie. Standard errors use FastAPI's `{ "detail": ... }` shape;
validation errors use `{ "detail": [{ "loc": ..., "msg": ..., "type": ... }] }`.
An `image_url` is an optional externally accessible reference URL returned by
TheMealDB or B. It can be `null`, and the backend does not currently proxy or
host missing dish images.

## Safe demonstration mode

```text
GET  /api/capabilities
POST /api/menu/demo-scan
```

`capabilities` exposes only whether Demo and live scanning are available; it
never returns provider keys or model identifiers. `demo-scan` loads a sanitized
fixed menu from `demo_menu_templates`, localizes it using the signed-in user's
`preferred_language`, applies the normal deterministic safety rules, persists a
normal `menu_id`, and never calls OpenAI or TheMealDB.

For a public presentation deployment use:

```text
FOODHUB_DEMO_AVAILABLE=true
FOODHUB_LIVE_SCAN_ENABLED=false
```

The backend rejects `/api/menu/scan` when live scanning is disabled, so hiding
or disabling a frontend button cannot be bypassed to consume the provider key.
Both live and Demo responses use the same schema and include `mode` plus a
per-dish `enrichment` object containing `summary`, `cuisine`, `source`, and
`confidence`.

## Resolution status

```text
local_fallback      earlier B result loaded from MySQL
llm_fallback        B resolved the miss during this request
themealdb_match     sufficiently similar reference recipe
needs_llm           B is not configured; batch remains in the response
lookup_unavailable  transient TheMealDB failure; do not cache an LLM result
```

TheMealDB responses and images are not stored locally.

## Evidence and ownership

```text
explicit            directly visible restaurant-menu evidence
reference_recipe    generic TheMealDB recipe evidence
inferred            Backend B culinary inference
cached_inference    an earlier B inference loaded from MySQL
```

B never receives user preferences and does not return allergens or suitability.
C maps ingredients to allergens and makes the final personalized decision.
Only explicit menu evidence can produce `contains`; reference and inferred
evidence produce `may_contain`.

The B/C fallback v1.1 request and response are documented in
`docs/backend-b-unknown-dish-contract.md` and can be validated with
`POST /api/menu/fallback-dishes/validate`.
