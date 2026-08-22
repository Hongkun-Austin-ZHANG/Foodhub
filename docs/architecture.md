# FoodHub architecture

## Complete flow

```text
Frontend image upload
  -> authenticated C endpoint
  -> SQL user profile preferred_language
  -> Backend B image parsing and translation
  -> MySQL fallback cache
  -> TheMealDB live matching
  -> one Backend B fallback call for every confirmed miss
  -> C ingredient-to-allergen mapping
  -> C persistent + daily preference reconciliation
  -> C deterministic recommendation
  -> frontend dish cards
```

TheMealDB is a live generic reference source. Its recipes and images are never
stored. Only B-generated unknown-dish knowledge is cached so later requests can
avoid another model call.

The resolver limits concurrent TheMealDB requests. An empty or low-similarity
result is a confirmed miss; a timeout is `lookup_unavailable` and never triggers
durable fallback caching.

## MySQL ownership

```text
users              login identity and password hash
user_profiles      personal data, preferred language, timezone
user_preferences   allergies, diets, religious rules, dislikes, likes
auth_sessions      hashed session tokens and expiry/revocation
fallback_dishes    B inference plus C-generated allergen evidence
```

Daily overrides are request-scoped and do not overwrite persistent defaults.

## Responsibility boundary

- B owns menu OCR/understanding, user-facing translation, conservative English
  matching names, and neutral unknown-dish culinary inference.
- C owns authentication, SQL, TheMealDB matching, caching, ingredient-to-allergen
  mapping, user preferences, safety status, and final recommendations.
- B receives no user identity, allergy, religion, or preference data.
- The frontend calls C once and renders the combined result.
