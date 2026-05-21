from pydantic import BaseModel, Field
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
    question: str = Field(min_length=1, max_length=4000)
    session_id: Optional[int] = None


class RetrievedChunkSummary(BaseModel):
    score: Optional[float] = None
    document_id: Optional[int] = None
    chunk_id: Optional[int] = None
    filename: Optional[str] = None
    page_number: Optional[int] = None
    access_level: Optional[str] = "private"
    content_preview: Optional[str] = None


class ChatQueryResponse(BaseModel):
    answer: str
    citations: List[Dict[str, Any]]
    confidence_score: float
    risk_level: str
    risk_reason: Optional[str] = None
    requires_human_review: bool = False
    injection_detected: bool = False
    injection_categories: List[str] = []
    retrieved_chunks: List[RetrievedChunkSummary]
    session_id: int
