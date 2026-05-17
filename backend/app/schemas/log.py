from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class QueryLogBase(BaseModel):
    query: str
    answer: Optional[str] = None
    retrieved_chunks: Optional[List[Dict[str, Any]]] = None
    confidence_score: Optional[float] = None
    risk_level: Optional[str] = None
    latency_ms: Optional[float] = None

class QueryLogCreate(QueryLogBase):
    user_id: Optional[int] = None

class QueryLogResponse(QueryLogBase):
    id: int
    user_id: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True
