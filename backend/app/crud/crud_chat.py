from sqlalchemy.orm import Session
from app.models.chat import ChatSession, ChatMessage
from app.schemas.chat import ChatSessionCreate, ChatMessageCreate

def get_chat_session(db: Session, session_id: int):
    return db.query(ChatSession).filter(ChatSession.id == session_id).first()

def create_chat_session(db: Session, session: ChatSessionCreate):
    db_session = ChatSession(**session.model_dump())
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session

def create_chat_message(db: Session, message: ChatMessageCreate):
    db_message = ChatMessage(**message.model_dump())
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message
