from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.chat import ChatSession
from app.schemas.chat import ChatQueryRequest, ChatQueryResponse, ChatSessionResponse
from app.services.chat_service import process_chat_query

router = APIRouter()


@router.get("/sessions", response_model=list[ChatSessionResponse])
def get_chat_sessions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    sessions = (
        db.query(ChatSession)
        .filter(ChatSession.user_id == current_user.id)
        .order_by(ChatSession.created_at.desc())
        .all()
    )
    return sessions


@router.post("/query", response_model=ChatQueryResponse)
def query_chat(
    request: ChatQueryRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return process_chat_query(db, request, current_user)
