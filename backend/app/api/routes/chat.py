from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.models.user import User

from app.schemas.chat import ChatQueryRequest, ChatQueryResponse
from app.services.chat_service import process_chat_query

router = APIRouter()

@router.get("/sessions")
def get_chat_sessions(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return {"message": f"List of chat sessions for {current_user.email}"}

@router.post("/query", response_model=ChatQueryResponse)
def query_chat(
    request: ChatQueryRequest, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    return process_chat_query(db, request, current_user)
