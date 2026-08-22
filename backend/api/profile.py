from fastapi import APIRouter
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import CurrentUserDep, SessionDep
from schemas.profile import ProfileResponse, ProfileUpdateRequest
from services.database.models import UserProfile

router = APIRouter(tags=["profile"])


async def load_or_create_profile(
    session: AsyncSession,
    user_id: str,
) -> UserProfile:
    profile = await session.scalar(
        select(UserProfile).where(UserProfile.user_id == user_id)
    )
    if profile is None:
        profile = UserProfile(user_id=user_id)
        session.add(profile)
        await session.commit()
        await session.refresh(profile)
    return profile


@router.get("/profile", response_model=ProfileResponse)
async def get_profile(
    user: CurrentUserDep,
    session: SessionDep,
) -> UserProfile:
    return await load_or_create_profile(session, user.id)


@router.patch("/profile", response_model=ProfileResponse)
async def update_profile(
    payload: ProfileUpdateRequest,
    user: CurrentUserDep,
    session: SessionDep,
) -> UserProfile:
    profile = await load_or_create_profile(session, user.id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(profile, field, value)
    await session.commit()
    await session.refresh(profile)
    return profile
