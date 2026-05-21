"""Document and chat session access checks."""

from app.models.document import Document
from app.models.user import User
from app.models.chat import ChatSession


def user_can_view_document(user: User, document: Document) -> bool:
    if user.role == "admin":
        return True
    if document.access_level == "public":
        return True
    return document.uploaded_by == user.id


def user_owns_chat_session(user: User, session: ChatSession) -> bool:
    return session.user_id == user.id
