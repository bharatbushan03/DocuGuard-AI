import pytest
from app.core.config import settings
from app.core.file_validation import validate_upload_content
from app.models.user import User
from app.models.chat import ChatSession
from app.models.document import Document


@pytest.fixture
def auth_header(client):
    client.post(
        f"{settings.API_V1_STR}/auth/register",
        json={"email": "security@example.com", "password": "password123"},
    )
    response = client.post(
        f"{settings.API_V1_STR}/auth/login",
        data={"username": "security@example.com", "password": "password123"},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_register_rejects_role_escalation(client):
    response = client.post(
        f"{settings.API_V1_STR}/auth/register",
        json={
            "email": "attacker@example.com",
            "password": "password123",
            "role": "admin",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["role"] == "user"


def test_register_weak_password_rejected(client):
    response = client.post(
        f"{settings.API_V1_STR}/auth/register",
        json={"email": "weak@example.com", "password": "short"},
    )
    assert response.status_code == 422


def test_magic_byte_validation_rejects_spoofed_pdf():
    with pytest.raises(ValueError, match="does not match"):
        validate_upload_content(b"not a pdf", "application/pdf")


def test_document_access_denied_returns_403(client, db):
    client.post(
        f"{settings.API_V1_STR}/auth/register",
        json={"email": "owner@example.com", "password": "password123"},
    )
    owner_login = client.post(
        f"{settings.API_V1_STR}/auth/login",
        data={"username": "owner@example.com", "password": "password123"},
    )
    owner_headers = {"Authorization": f"Bearer {owner_login.json()['access_token']}"}

    client.post(
        f"{settings.API_V1_STR}/auth/register",
        json={"email": "other@example.com", "password": "password123"},
    )
    other_login = client.post(
        f"{settings.API_V1_STR}/auth/login",
        data={"username": "other@example.com", "password": "password123"},
    )
    other_headers = {"Authorization": f"Bearer {other_login.json()['access_token']}"}

    owner = db.query(User).filter(User.email == "owner@example.com").first()
    private_doc = Document(
        title="Private",
        filename="secret.txt",
        file_type="text/plain",
        access_level="private",
        uploaded_by=owner.id,
        status="indexed",
    )
    db.add(private_doc)
    db.commit()
    db.refresh(private_doc)

    response = client.get(
        f"{settings.API_V1_STR}/documents/{private_doc.id}",
        headers=other_headers,
    )
    assert response.status_code == 403


def test_chat_session_idor_blocked(client, db, auth_header):
    other_user = User(email="idor@example.com", hashed_password="x", role="user")
    db.add(other_user)
    db.commit()
    db.refresh(other_user)

    foreign_session = ChatSession(title="Foreign", user_id=other_user.id)
    db.add(foreign_session)
    db.commit()
    db.refresh(foreign_session)

    response = client.post(
        f"{settings.API_V1_STR}/chat/query",
        headers=auth_header,
        json={
            "question": "What is the policy?",
            "session_id": foreign_session.id,
        },
    )
    assert response.status_code == 403


def test_chat_response_redacts_full_chunk_content(client, auth_header):
    response = client.post(
        f"{settings.API_V1_STR}/chat/query",
        headers=auth_header,
        json={"question": "What is the company policy on remote work?"},
    )
    assert response.status_code == 200
    data = response.json()
    for chunk in data["retrieved_chunks"]:
        assert "content" not in chunk
        assert "content_preview" in chunk
