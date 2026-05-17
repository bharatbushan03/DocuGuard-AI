from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models.document import Document
from app.schemas.document import DocumentCreate

def get_document(db: Session, document_id: int):
    return db.query(Document).filter(Document.id == document_id).first()

def get_documents_for_user(db: Session, user_id: int, user_role: str):
    if user_role == "admin":
        return db.query(Document).all()
    else:
        return db.query(Document).filter(
            or_(
                Document.uploaded_by == user_id,
                Document.access_level == "public"
            )
        ).all()

def create_document(db: Session, document: DocumentCreate):
    db_document = Document(**document.model_dump())
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    return db_document
