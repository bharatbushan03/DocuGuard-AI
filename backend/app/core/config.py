import json
from typing import List, Union

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.core.security_constants import INSECURE_OPENAI_KEYS, INSECURE_SECRET_KEYS


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",
    )

    PROJECT_NAME: str = "DocuGuard AI"
    API_V1_STR: str = "/api"
    APP_ENV: str = "development"  # development | production
    DEBUG_MODE_ENABLED: bool = False

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000"]

    # Database
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "docuguard"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: str = "5432"

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    # Vector Database
    QDRANT_URL: str = "http://localhost:6333"

    # JWT
    SECRET_KEY: str = "super_secret_key_change_in_production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    # OpenAI
    OPENAI_API_KEY: str = "sk-mock-key"
    OPENAI_API_BASE: str = "https://api.openai.com/v1"
    EMBEDDING_MODEL_NAME: str = "text-embedding-3-small"
    LLM_MODEL_NAME: str = "gpt-4o-mini"

    # Registration
    ALLOW_PUBLIC_REGISTRATION: bool = True

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: Union[str, List[str]]) -> List[str]:
        if isinstance(value, list):
            return value
        if isinstance(value, str):
            stripped = value.strip()
            if stripped.startswith("["):
                return json.loads(stripped)
            return [origin.strip() for origin in stripped.split(",") if origin.strip()]
        return value

    @model_validator(mode="after")
    def validate_production_secrets(self) -> "Settings":
        if self.APP_ENV.lower() != "production":
            return self
        errors: List[str] = []
        if self.SECRET_KEY in INSECURE_SECRET_KEYS or len(self.SECRET_KEY) < 32:
            errors.append("SECRET_KEY must be a strong random value (32+ chars) in production.")
        if self.OPENAI_API_KEY in INSECURE_OPENAI_KEYS:
            errors.append("OPENAI_API_KEY must be set in production.")
        if self.POSTGRES_PASSWORD in ("postgres", "", "password"):
            errors.append("POSTGRES_PASSWORD must not use default values in production.")
        if errors:
            raise ValueError(" ".join(errors))
        return self


settings = Settings()
