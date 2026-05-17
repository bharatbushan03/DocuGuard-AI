from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.models.user import User

router = APIRouter()

@router.get("/sessions")
def get_chat_sessions(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return {"message": f"List of chat sessions for {current_user.email}"}

@router.post("/message")
def send_message(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return {"message": "Send a message endpoint protected"}
