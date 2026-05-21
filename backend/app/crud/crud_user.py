from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.core.security_constants import ALLOWED_ROLES, DEFAULT_USER_ROLE
from app.models.user import User
from app.schemas.user import UserCreate, UserRegister


def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


def create_user(db: Session, user: UserCreate) -> User:
    role = user.role if user.role in ALLOWED_ROLES else DEFAULT_USER_ROLE
    hashed_password = get_password_hash(user.password)
    db_user = User(email=user.email, hashed_password=hashed_password, role=role)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def register_user(db: Session, user: UserRegister) -> User:
    """Create a user with the default role only (no client-controlled escalation)."""
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        hashed_password=hashed_password,
        role=DEFAULT_USER_ROLE,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
