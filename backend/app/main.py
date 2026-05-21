import logging

from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.security_constants import INSECURE_SECRET_KEYS
from app.api.routes import documents, chat, admin, auth

logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="DocuGuard AI Enterprise Assistant API",
)

if settings.SECRET_KEY in INSECURE_SECRET_KEYS:
    logger.warning(
        "SECRET_KEY is using a default value. Set a strong SECRET_KEY before production deployment."
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept"],
)

@app.get("/health")
def health_check():
    return {"status": "ok"}

api_router = APIRouter()
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])

app.include_router(api_router, prefix=settings.API_V1_STR)
