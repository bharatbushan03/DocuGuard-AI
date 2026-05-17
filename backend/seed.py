import logging
from sqlalchemy.orm import Session
from app.db.session import engine, SessionLocal
from app.db.base import Base
from app.schemas.user import UserCreate
from app.schemas.document import DocumentCreate
from app.schemas.chat import ChatSessionCreate
from app.crud import crud_user, crud_document, crud_chat

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def seed_data(db: Session):
    logger.info("Creating initial data")

    # 1. Create a User
    user_in = UserCreate(email="admin@docuguard.com", password="securepassword", role="admin")
    user = crud_user.get_user_by_email(db, email=user_in.email)
    if not user:
        user = crud_user.create_user(db, user=user_in)
        logger.info(f"Created user: {user.email}")
    else:
        logger.info(f"User {user.email} already exists")

    # 2. Create a Document
    doc_in = DocumentCreate(
        title="Employee Handbook 2026",
        filename="employee_handbook.pdf",
        file_type="application/pdf",
        access_level="public",
        uploaded_by=user.id
    )
    document = crud_document.create_document(db, document=doc_in)
    logger.info(f"Created document: {document.title}")

    # 3. Create a Chat Session
    chat_in = ChatSessionCreate(title="HR Policies Inquiry", user_id=user.id)
    chat_session = crud_chat.create_chat_session(db, session=chat_in)
    logger.info(f"Created chat session: {chat_session.title}")

    logger.info("Seeding completed successfully.")

def main():
    logger.info("Starting seed process...")
    # Optional: Base.metadata.create_all(bind=engine) # Handled by Alembic
    db = SessionLocal()
    try:
        seed_data(db)
    finally:
        db.close()

if __name__ == "__main__":
    main()
