from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.auth import router as auth_router
from api.menu import router as menu_router
from api.preferences import router as preferences_router
from api.profile import router as profile_router
from api.recommendation import router as recommendation_router
from api.recommendations import router as recommendations_router
from api.system import router as system_router
from core.config import get_settings
from core.logging import configure_logging


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(settings.app_env)

    application = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        debug=settings.debug,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    application.include_router(auth_router, prefix=settings.api_prefix)
    application.include_router(system_router, prefix=settings.api_prefix)
    application.include_router(profile_router, prefix=settings.api_prefix)
    application.include_router(preferences_router, prefix=settings.api_prefix)
    application.include_router(menu_router, prefix=settings.api_prefix)
    application.include_router(recommendation_router, prefix=settings.api_prefix)
    application.include_router(recommendations_router, prefix=settings.api_prefix)

    @application.get("/health", tags=["health"])
    async def health() -> dict[str, str]:
        return {"status": "ok", "service": settings.app_name}

    return application


app = create_app()
