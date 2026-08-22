from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import Annotated

import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import get_settings
from core.security import hash_session_token
from services.ai.menu_parser import (
    MenuParser,
    MenuUnderstandingError,
    OpenAIMenuParser,
)
from services.ai.unknown_dish import OpenAIUnknownDishResolver, UnknownDishResolver
from services.database.models import AuthSession, User
from services.database.session import get_session
from services.database.themealdb_client import TheMealDBClient

bearer_scheme = HTTPBearer(auto_error=False)
SessionDep = Annotated[AsyncSession, Depends(get_session)]
BearerCredentialsDep = Annotated[
    HTTPAuthorizationCredentials | None,
    Depends(bearer_scheme),
]


@dataclass(slots=True)
class AuthContext:
    user: User
    auth_session: AuthSession


def unauthorized() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired authentication token",
        headers={"WWW-Authenticate": "Bearer"},
    )


async def get_auth_context(
    credentials: BearerCredentialsDep,
    session: SessionDep,
) -> AuthContext:
    if credentials is None or credentials.scheme.casefold() != "bearer":
        raise unauthorized()

    statement = (
        select(User, AuthSession)
        .join(AuthSession, AuthSession.user_id == User.id)
        .where(
            AuthSession.token_hash == hash_session_token(credentials.credentials),
            AuthSession.revoked_at.is_(None),
            AuthSession.expires_at > func.now(),
            User.is_active.is_(True),
        )
    )
    row = (await session.execute(statement)).one_or_none()
    if row is None:
        raise unauthorized()
    return AuthContext(user=row[0], auth_session=row[1])


async def get_current_user(
    context: Annotated[AuthContext, Depends(get_auth_context)],
) -> User:
    return context.user


AuthContextDep = Annotated[AuthContext, Depends(get_auth_context)]
CurrentUserDep = Annotated[User, Depends(get_current_user)]


async def get_themealdb_client() -> AsyncIterator[TheMealDBClient]:
    settings = get_settings()
    async with httpx.AsyncClient(timeout=settings.themealdb_timeout_seconds) as client:
        yield TheMealDBClient(
            http_client=client,
            base_url=settings.themealdb_base_url,
            api_key=settings.themealdb_api_key,
        )


TheMealDBDep = Annotated[TheMealDBClient, Depends(get_themealdb_client)]


def get_menu_parser() -> MenuParser:
    settings = get_settings()
    api_key = (
        settings.openai_api_key.get_secret_value().strip()
        if settings.openai_api_key is not None
        else ""
    )
    model = settings.openai_model.strip() if settings.openai_model else ""
    if not api_key or not model:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "Backend B is not configured. Set FOODHUB_OPENAI_API_KEY and "
                "FOODHUB_OPENAI_MODEL."
            ),
        )
    try:
        return OpenAIMenuParser(
            api_key=api_key,
            model=model,
            timeout_seconds=settings.openai_timeout_seconds,
        )
    except MenuUnderstandingError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(error),
        ) from error


def get_unknown_dish_resolver() -> UnknownDishResolver | None:
    settings = get_settings()
    api_key = (
        settings.openai_api_key.get_secret_value().strip()
        if settings.openai_api_key is not None
        else ""
    )
    model = settings.openai_model.strip() if settings.openai_model else ""
    if not api_key or not model:
        return None
    try:
        return OpenAIUnknownDishResolver(
            api_key=api_key,
            model=model,
            timeout_seconds=settings.openai_timeout_seconds,
        )
    except MenuUnderstandingError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(error),
        ) from error


MenuParserDep = Annotated[MenuParser, Depends(get_menu_parser)]
UnknownDishResolverDep = Annotated[
    UnknownDishResolver | None,
    Depends(get_unknown_dish_resolver),
]
