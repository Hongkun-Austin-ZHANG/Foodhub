from datetime import UTC, datetime, timedelta
from uuid import uuid4

from fastapi import APIRouter, HTTPException, status
from fastapi.concurrency import run_in_threadpool
from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError

from api.dependencies import AuthContextDep, CurrentUserDep, SessionDep
from core.config import get_settings
from core.security import (
    create_session_token,
    hash_password,
    hash_session_token,
    verify_password,
)
from schemas.auth import (
    AuthResponse,
    LoginRequest,
    LogoutResponse,
    RegisterRequest,
    UserResponse,
)
from services.database.models import AuthSession, User, UserProfile

router = APIRouter(prefix="/auth", tags=["auth"])


def build_auth_response(user: User, token: str, expires_at: datetime) -> AuthResponse:
    return AuthResponse(
        access_token=token,
        expires_at=expires_at,
        user=UserResponse.model_validate(user),
    )


def create_auth_session(user_id: str) -> tuple[str, datetime, AuthSession]:
    token = create_session_token()
    expires_at = datetime.now(UTC) + timedelta(hours=get_settings().auth_session_hours)
    auth_session = AuthSession(
        user_id=user_id,
        token_hash=hash_session_token(token),
        expires_at=expires_at,
    )
    return token, expires_at, auth_session


@router.post(
    "/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED
)
async def register(
    payload: RegisterRequest,
    session: SessionDep,
) -> AuthResponse:
    email = str(payload.email).casefold()
    username = payload.username or f"user_{uuid4().hex[:12]}"
    normalized_username = username.casefold()
    duplicate_statement = select(User.id).where(
        or_(
            func.lower(User.email) == email,
            func.lower(User.username) == normalized_username,
        )
    )
    if await session.scalar(duplicate_statement):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email or username is already registered",
        )

    user = User(
        email=email,
        username=username,
        password_hash=await run_in_threadpool(hash_password, payload.password),
    )
    user.profile = UserProfile(
        display_name=payload.name or payload.username,
        preferred_language=payload.preferred_language,
    )
    session.add(user)
    try:
        await session.flush()
        token, expires_at, auth_session = create_auth_session(user.id)
        session.add(auth_session)
        await session.commit()
    except IntegrityError as error:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email or username is already registered",
        ) from error
    return build_auth_response(user, token, expires_at)


@router.post("/login", response_model=AuthResponse)
async def login(
    payload: LoginRequest,
    session: SessionDep,
) -> AuthResponse:
    identifier = payload.login_identifier.casefold()
    statement = select(User).where(
        or_(
            func.lower(User.email) == identifier,
            func.lower(User.username) == identifier,
        )
    )
    user = await session.scalar(statement)
    password_valid = user is not None and await run_in_threadpool(
        verify_password,
        payload.password,
        user.password_hash,
    )
    if not password_valid or user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email, username, or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token, expires_at, auth_session = create_auth_session(user.id)
    session.add(auth_session)
    await session.commit()
    return build_auth_response(user, token, expires_at)


@router.get("/me", response_model=UserResponse)
async def current_user(user: CurrentUserDep) -> User:
    return user


@router.post("/logout", response_model=LogoutResponse)
async def logout(
    context: AuthContextDep,
    session: SessionDep,
) -> LogoutResponse:
    context.auth_session.revoked_at = datetime.now(UTC)
    await session.commit()
    return LogoutResponse()
