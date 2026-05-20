import os
import pytest
from typing import Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.api.deps import get_db
from app.db.base import Base
from app.core.config import settings
from unittest.mock import MagicMock, patch

# Use an in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite://"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db() -> Generator:
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def client(db) -> Generator:
    def override_get_db():
        try:
            yield db
        finally:
            pass
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

@pytest.fixture(autouse=True)
def mock_session_local():
    with patch("app.services.ingestion_service.SessionLocal", TestingSessionLocal):
        yield

@pytest.fixture(autouse=True)
def mock_password_hashing():
    # Patch where it is defined
    with patch("app.core.security.get_password_hash", side_effect=lambda p: f"hashed_{p}"), \
         patch("app.core.security.verify_password", side_effect=lambda p, h: h == f"hashed_{p}"), \
         patch("app.crud.crud_user.get_password_hash", side_effect=lambda p: f"hashed_{p}"), \
         patch("app.api.routes.auth.verify_password", side_effect=lambda p, h: h == f"hashed_{p}"):
        yield

# --- Mocks ---

@pytest.fixture(autouse=True)
def mock_openai():
    with patch("app.services.embedding.client") as mock:
        # Mock embedding response
        mock_response = MagicMock()
        mock_response.data = [MagicMock(embedding=[0.1] * 1536)]
        mock.embeddings.create.return_value = mock_response
        yield mock

@pytest.fixture(autouse=True)
def mock_openai_chat():
    with patch("app.services.chat_service.client") as mock:
        # Mock chat completion response
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(
                message=MagicMock(
                    content='{"answer": "Test answer from context.", "citations": [{"document": "test.pdf", "page": "1", "chunk_id": "1", "supporting_text": "text"}], "confidence_reasoning": "High overlap.", "requires_human_review": false}'
                )
            )
        ]
        mock.chat.completions.create.return_value = mock_response
        yield mock

@pytest.fixture(autouse=True)
def mock_citation_verifier():
    with patch("app.services.chat_service.verify_and_rewrite_answer", side_effect=lambda a, c: (a, 1.0)):
        yield

@pytest.fixture(autouse=True)
def mock_qdrant():
    with patch("app.services.vector_db.client") as mock:
        # Mock search results
        mock_res = MagicMock()
        mock_res.score = 0.95
        mock_res.payload = {
            "document_id": 1,
            "chunk_id": 1,
            "filename": "test.pdf",
            "page_number": 1,
            "content": "Test content for chunk 1.",
            "access_level": "private"
        }
        mock.search.return_value = [mock_res, mock_res, mock_res, mock_res, mock_res]
        mock.get_collections.return_value.collections = []
        yield mock
