from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_db, require_role
from app.models.user import User

router = APIRouter()

@router.get("/users")
def get_all_users(db: Session = Depends(get_db), current_user: User = Depends(require_role(["admin"]))):
    return {"message": "List of users for admin only"}
