from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class ChatMessageBase(BaseModel):
    role: str
    content: str
    citations: Optional[List[Dict[str, Any]]] = None
    confidence_score: Optional[float] = None
    risk_level: Optional[str] = None

class ChatMessageCreate(ChatMessageBase):
    session_id: int

class ChatMessageResponse(ChatMessageBase):
    id: int
    session_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class ChatSessionBase(BaseModel):
    title: Optional[str] = None

class ChatSessionCreate(ChatSessionBase):
    user_id: int

class ChatSessionResponse(ChatSessionBase):
    id: int
    user_id: int
    created_at: datetime
    messages: List[ChatMessageResponse] = []

    class Config:
        from_attributes = True

class ChatQueryRequest(BaseModel):
    question: str
    session_id: Optional[int] = None

class ChatQueryResponse(BaseModel):
    answer: str
    citations: List[Dict[str, Any]]
    confidence_score: float
    risk_level: str
    risk_reason: Optional[str] = None
    requires_human_review: bool = False
    retrieved_chunks: List[Dict[str, Any]]
    session_id: int
