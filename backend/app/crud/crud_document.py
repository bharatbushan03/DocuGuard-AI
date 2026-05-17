from sqlalchemy.orm import Session
from app.models.document import Document
from app.schemas.document import DocumentCreate

def get_document(db: Session, document_id: int):
    return db.query(Document).filter(Document.id == document_id).first()

def create_document(db: Session, document: DocumentCreate):
    db_document = Document(**document.model_dump())
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    return db_document
