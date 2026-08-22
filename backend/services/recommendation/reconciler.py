from schemas.preference import (
    EffectivePreferences,
    PreferenceContext,
    PreferenceKind,
    PreferenceStrength,
    UserPreference,
)
from services.recommendation.preference_catalog import get_preference_option


def resolve_preferences(context: PreferenceContext) -> EffectivePreferences:
    """Merge daily choices without allowing them to disable hard constraints."""
    resolved = {
        preference.code: preference.model_copy() for preference in context.persistent
    }

    for override in context.daily_overrides:
        existing = resolved.get(override.code)
        if existing is not None:
            if existing.strength == PreferenceStrength.HARD and not override.enabled:
                continue
            resolved[override.code] = existing.model_copy(
                update={"enabled": override.enabled}
            )
        elif override.enabled:
            option = get_preference_option(override.code)
            resolved[override.code] = UserPreference(
                code=override.code,
                kind=option.kind if option else PreferenceKind.PREFERENCE,
                strength=(
                    option.default_strength if option else PreferenceStrength.SOFT
                ),
                enabled=True,
            )

    enabled = sorted(
        (preference for preference in resolved.values() if preference.enabled),
        key=lambda preference: preference.code,
    )
    return EffectivePreferences(preferences=enabled)
