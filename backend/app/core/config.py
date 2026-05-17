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
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
