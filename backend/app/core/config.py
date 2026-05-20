from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "DocuGuard AI"
    API_V1_STR: str = "/api"
    
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
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    # Vector Database
    QDRANT_URL: str = "http://localhost:6333"
    
    # JWT
    # In production, SECRET_KEY must be provided via environment variable
    SECRET_KEY: str = "super_secret_key_change_in_production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 # Reduced to 1 day default
    
    # OpenAI Settings
    # In production, OPENAI_API_KEY must be provided via environment variable
    OPENAI_API_KEY: str = "sk-mock-key"
    OPENAI_API_BASE: str = "https://api.openai.com/v1"
    EMBEDDING_MODEL_NAME: str = "text-embedding-3-small"
    LLM_MODEL_NAME: str = "gpt-4o-mini"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
