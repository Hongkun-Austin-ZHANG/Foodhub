# FoodHub Architecture — 40-Second Presentation Draft

FoodHub turns a photographed menu into personalized, explainable
recommendations. The React frontend handles authentication, language selection,
saved preferences, multi-image upload, and result presentation. Requests go
through a FastAPI backend, while MySQL stores user profiles, menu sessions, and
reusable fallback dishes. For each dish, the resolver checks our local cache
first, then TheMealDB, and sends all remaining misses to OpenAI in one batch. A
deterministic rules engine combines ingredient evidence with allergies, dietary
requirements, and current-meal choices. The final results explain why each dish
is a match or should be avoided, and are displayed in English, Chinese, or
French. A database-backed demo mode can run without any external AI call.
