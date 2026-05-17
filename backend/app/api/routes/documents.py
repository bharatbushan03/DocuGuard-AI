from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user, require_role
from app.models.user import User
from app.schemas.document import DocumentResponse
from app.services.ingestion import process_upload

router = APIRouter()

@router.get("/")
def get_documents(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return {"message": "List of documents for user", "user": current_user.email}

@router.post("/upload", response_model=DocumentResponse)
def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db), 
    current_user: User = Depends(require_role(["admin", "hr", "legal", "employee"]))
):
    doc = process_upload(file=file, user_id=current_user.id, db=db)
    return doc
