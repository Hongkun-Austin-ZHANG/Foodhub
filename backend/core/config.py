from functools import lru_cache

from pydantic import AliasChoices, Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="FOODHUB_",
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "FoodHub API"
    app_env: str = "local"
    debug: bool = True
    api_prefix: str = "/api"
    database_url: str = (
        "mysql+asyncmy://foodhub:foodhub_local_password@localhost:3306/"
        "foodhub?charset=utf8mb4"
    )
    database_echo: bool = False
    auth_session_hours: int = Field(default=168, ge=1, le=24 * 90)
    themealdb_base_url: str = "https://www.themealdb.com/api/json/v1"
    themealdb_api_key: str = "1"
    themealdb_timeout_seconds: float = Field(default=6.0, gt=0, le=30)
    themealdb_max_concurrency: int = Field(default=5, ge=1, le=20)
    dish_match_threshold: float = Field(default=0.85, ge=0, le=1)
    openai_api_key: SecretStr | None = Field(
        default=None,
        validation_alias="FOODHUB_OPENAI_API_KEY",
    )
    openai_model: str | None = Field(
        default=None,
        validation_alias=AliasChoices("FOODHUB_OPENAI_MODEL", "OPENAI_MODEL"),
    )
    openai_timeout_seconds: float = Field(default=90.0, gt=0, le=300)
    demo_available: bool = True
    live_scan_enabled: bool = True
    menu_image_max_bytes: int = Field(default=10 * 1024 * 1024, ge=1024)
    menu_image_max_count: int = Field(default=5, ge=1, le=10)
    menu_images_total_max_bytes: int = Field(
        default=30 * 1024 * 1024,
        ge=1024,
    )
    cors_origins: list[str] = Field(
        default_factory=lambda: [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://localhost:5173",
            "http://127.0.0.1:5173",
        ]
    )

    @property
    def live_scan_available(self) -> bool:
        api_key = (
            self.openai_api_key.get_secret_value().strip()
            if self.openai_api_key is not None
            else ""
        )
        return bool(
            self.live_scan_enabled
            and api_key
            and self.openai_model
            and self.openai_model.strip()
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()
