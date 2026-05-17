from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user, require_role
from app.models.user import User

router = APIRouter()

@router.get("/")
def get_documents(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return {"message": "List of documents for user", "user": current_user.email}

@router.post("/upload")
def upload_document(
    db: Session = Depends(get_db), 
    current_user: User = Depends(require_role(["admin", "hr", "legal", "employee"]))
):
    return {"message": "Upload document endpoint protected", "uploaded_by": current_user.email}
