# Import all models here to ensure they are registered with SQLAlchemy for Alembic
from app.db.base_class import Base
from app.models.user import User
from app.models.document import Document, DocumentChunk
from app.models.chat import ChatSession, ChatMessage
from app.models.log import QueryLog
