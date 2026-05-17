from fastapi import APIRouter, Depends, UploadFile, File, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.api.deps import get_db, get_current_user, require_role
from app.models.user import User
from app.schemas.document import DocumentResponse
from app.services.ingestion_service import save_uploaded_file, process_document_background
from app.crud import crud_document

router = APIRouter()

@router.post("/upload", response_model=DocumentResponse)
def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db), 
    current_user: User = Depends(require_role(["admin", "hr", "legal", "employee"]))
):
    # 1. Save file and create initial DB record synchronously
    db_doc, file_path = save_uploaded_file(file=file, user_id=current_user.id, db=db)
    
    # 2. Add heavy processing to background tasks
    background_tasks.add_task(process_document_background, db_doc.id, file_path)
    
    # 3. Return immediately with 'uploaded' status
    return db_doc

@router.get("/{document_id}", response_model=DocumentResponse)
def get_document_status(
    document_id: int, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    doc = crud_document.get_document(db, document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
        
    # Check access logic: only admin or the user who uploaded it can check status 
    # unless we assume all authenticated users can check public docs
    if current_user.role != "admin" and doc.uploaded_by != current_user.id and doc.access_level != "public":
        raise HTTPException(status_code=403, detail="Not enough privileges to view this document")
        
    return doc

@router.get("/", response_model=List[DocumentResponse])
def get_documents(
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    docs = crud_document.get_documents_for_user(db, current_user.id, current_user.role)
    return docs
