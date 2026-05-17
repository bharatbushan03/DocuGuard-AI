from pydantic import BaseModel
from typing import Optional, Any, Dict
from datetime import datetime

class DocumentChunkBase(BaseModel):
    chunk_index: int
    content: str
    metadata_: Optional[Dict[str, Any]] = None
    qdrant_point_id: Optional[str] = None

class DocumentChunkResponse(DocumentChunkBase):
    id: int
    document_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class DocumentBase(BaseModel):
    title: str
    filename: str
    file_type: str
    access_level: Optional[str] = "private"

class DocumentCreate(DocumentBase):
    uploaded_by: int

class DocumentResponse(DocumentBase):
    id: int
    status: str
    uploaded_by: int
    created_at: datetime

    class Config:
        from_attributes = True
