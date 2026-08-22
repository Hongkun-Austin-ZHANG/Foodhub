from fastapi import APIRouter, HTTPException, Response, status
from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import CurrentUserDep, SessionDep
from schemas.preference import (
    PreferenceKind,
    PreferenceOption,
    PreferenceProfile,
    PreferenceStrength,
    PreferenceUpdateRequest,
    StoredPreferenceResponse,
    normalize_preference_code,
)
from schemas.preference import (
    UserPreference as UserPreferenceRequest,
)
from services.database.models import UserPreference
from services.recommendation.preference_catalog import list_preference_options

router = APIRouter(tags=["preferences"])

PROFILE_PREFIXES = {
    "preferred_proteins": "protein_",
    "preferred_flavours": "flavour_",
    "preferred_textures": "texture_",
}


@router.get("/preferences/options", response_model=list[PreferenceOption])
async def get_preference_options() -> list[PreferenceOption]:
    return list_preference_options()


def normalize_path_code(code: str) -> str:
    try:
        return normalize_preference_code(code)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(error),
        ) from error


async def find_preference(
    session: AsyncSession,
    user_id: str,
    code: str,
) -> UserPreference:
    preference = await session.scalar(
        select(UserPreference).where(
            UserPreference.user_id == user_id,
            UserPreference.code == normalize_path_code(code),
        )
    )
    if preference is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Preference not found",
        )
    return preference


@router.get("/preferences", response_model=list[StoredPreferenceResponse])
async def list_preferences(
    user: CurrentUserDep,
    session: SessionDep,
) -> list[UserPreference]:
    result = await session.scalars(
        select(UserPreference)
        .where(UserPreference.user_id == user.id)
        .order_by(UserPreference.code)
    )
    return list(result)


def _profile_from_preferences(preferences: list[UserPreference]) -> PreferenceProfile:
    values: dict[str, object] = {
        "allergies": [],
        "dietary_restrictions": [],
        "religious_restrictions": [],
        "preferred_proteins": [],
        "preferred_flavours": [],
        "preferred_textures": [],
        "spice_level": None,
        "disliked_ingredients": [],
    }
    kind_fields = {
        PreferenceKind.ALLERGY.value: "allergies",
        PreferenceKind.DIETARY.value: "dietary_restrictions",
        PreferenceKind.RELIGIOUS.value: "religious_restrictions",
        PreferenceKind.AVOID.value: "disliked_ingredients",
    }
    for preference in preferences:
        if not preference.enabled:
            continue
        field = kind_fields.get(preference.kind)
        if field is not None:
            group = values[field]
            assert isinstance(group, list)
            group.append(preference.code)
            continue
        if preference.kind != PreferenceKind.PREFERENCE.value:
            continue
        if preference.code.startswith("spice_level_"):
            values["spice_level"] = preference.code.removeprefix("spice_level_")
            continue
        for profile_field, prefix in PROFILE_PREFIXES.items():
            if preference.code.startswith(prefix):
                group = values[profile_field]
                assert isinstance(group, list)
                group.append(preference.code.removeprefix(prefix))
                break
    for value in values.values():
        if isinstance(value, list):
            value.sort()
    return PreferenceProfile.model_validate(values)


def _preference_rows(payload: PreferenceProfile) -> list[dict[str, str | bool]]:
    rows: dict[str, dict[str, str | bool]] = {}

    def add(code: str, kind: PreferenceKind, strength: PreferenceStrength) -> None:
        # A safety restriction takes precedence over a duplicate soft dislike.
        rows.setdefault(
            code,
            {
                "code": code,
                "kind": kind.value,
                "strength": strength.value,
                "enabled": True,
            },
        )

    for code in payload.allergies:
        add(code, PreferenceKind.ALLERGY, PreferenceStrength.HARD)
    for code in payload.dietary_restrictions:
        add(code, PreferenceKind.DIETARY, PreferenceStrength.HARD)
    for code in payload.religious_restrictions:
        add(code, PreferenceKind.RELIGIOUS, PreferenceStrength.HARD)
    for code in payload.disliked_ingredients:
        add(code, PreferenceKind.AVOID, PreferenceStrength.SOFT)
    for profile_field, prefix in PROFILE_PREFIXES.items():
        for code in getattr(payload, profile_field):
            add(f"{prefix}{code}", PreferenceKind.PREFERENCE, PreferenceStrength.SOFT)
    if payload.spice_level is not None:
        add(
            f"spice_level_{payload.spice_level}",
            PreferenceKind.PREFERENCE,
            PreferenceStrength.SOFT,
        )
    return list(rows.values())


@router.get("/preferences/profile", response_model=PreferenceProfile)
async def get_preference_profile(
    user: CurrentUserDep,
    session: SessionDep,
) -> PreferenceProfile:
    result = await session.scalars(
        select(UserPreference)
        .where(UserPreference.user_id == user.id)
        .order_by(UserPreference.code)
    )
    return _profile_from_preferences(list(result))


@router.put("/preferences/profile", response_model=PreferenceProfile)
async def replace_preference_profile(
    payload: PreferenceProfile,
    user: CurrentUserDep,
    session: SessionDep,
) -> PreferenceProfile:
    """Replace all saved preferences with the grouped frontend payload."""

    await session.execute(
        delete(UserPreference).where(UserPreference.user_id == user.id)
    )
    session.add_all(
        [UserPreference(user_id=user.id, **row) for row in _preference_rows(payload)]
    )
    await session.commit()

    result = await session.scalars(
        select(UserPreference)
        .where(UserPreference.user_id == user.id)
        .order_by(UserPreference.code)
    )
    return _profile_from_preferences(list(result))


@router.post(
    "/preferences",
    response_model=StoredPreferenceResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_preference(
    payload: UserPreferenceRequest,
    user: CurrentUserDep,
    session: SessionDep,
) -> UserPreference:
    preference = UserPreference(
        user_id=user.id,
        code=payload.code,
        kind=payload.kind.value,
        strength=payload.strength.value,
        enabled=payload.enabled,
    )
    session.add(preference)
    try:
        await session.commit()
    except IntegrityError as error:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Preference already exists",
        ) from error
    await session.refresh(preference)
    return preference


@router.patch("/preferences/{code}", response_model=StoredPreferenceResponse)
async def update_preference(
    code: str,
    payload: PreferenceUpdateRequest,
    user: CurrentUserDep,
    session: SessionDep,
) -> UserPreference:
    preference = await find_preference(session, user.id, code)
    updates = payload.model_dump(exclude_unset=True)
    for field in ("kind", "strength"):
        if field in updates:
            updates[field] = updates[field].value
    for field, value in updates.items():
        setattr(preference, field, value)
    await session.commit()
    await session.refresh(preference)
    return preference


@router.delete("/preferences/{code}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_preference(
    code: str,
    user: CurrentUserDep,
    session: SessionDep,
) -> Response:
    preference = await find_preference(session, user.id, code)
    await session.delete(preference)
    await session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
