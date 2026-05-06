from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class ProductionSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env.prod", env_file_encoding="utf-8")

    APP_ENV: str = "production"
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    DEBUG: bool = False
    LOG_LEVEL: str = "WARNING"

    DATABASE_URL: str
    REDIS_URL: str

    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALGORITHM: str = "HS256"

    ALLOWED_ORIGINS: str
    MAX_UPLOAD_SIZE_MB: int = 10
    UPLOAD_DIR: str = "uploads/"

    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str = "servicehub"

    @property
    def allowed_origins_list(self) -> list[str]:
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",")]


@lru_cache
def get_production_settings() -> ProductionSettings:
    return ProductionSettings()
