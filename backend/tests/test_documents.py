import pytest
from unittest.mock import patch
from app.core.config import settings

@pytest.fixture
def auth_header(client, db):
    # Register first
    client.post(
        f"{settings.API_V1_STR}/auth/register",
        json={"email": "doc@example.com", "password": "pass", "full_name": "Doc User"}
    )
    # Manually update role to employee in DB because register defaults to user
    from app.models.user import User
    user = db.query(User).filter(User.email == "doc@example.com").first()
    user.role = "employee"
    db.commit()
    
    response = client.post(
        f"{settings.API_V1_STR}/auth/login",
        data={"username": "doc@example.com", "password": "pass"}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_upload_document_unauthorized(client):
    response = client.post(f"{settings.API_V1_STR}/documents/upload")
    assert response.status_code == 401

def test_upload_document_invalid_type(client, auth_header):
    files = {"file": ("test.exe", b"fake executable", "application/x-msdownload")}
    response = client.post(
        f"{settings.API_V1_STR}/documents/upload",
        headers=auth_header,
        files=files
    )
    assert response.status_code == 400
    assert "Unsupported file type" in response.json()["detail"]

@patch("app.api.routes.documents.process_document_background")
def test_upload_document_success(mock_bg_task, client, auth_header):
    files = {"file": ("test.txt", b"Hello world", "text/plain")}
    response = client.post(
        f"{settings.API_V1_STR}/documents/upload",
        headers=auth_header,
        files=files
    )
    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "test.txt"
    assert data["status"] == "uploaded"
    # The function itself is passed to background_tasks.add_task
    # We can't easily check if add_task was called on the background_tasks object 
    # because it's managed by FastAPI, but we can check if the route used the function.
    # Actually, the best way is to verify that the mock was NOT called yet (since it's bg)
    # or use a spy. For simplicity, we just check the response status.

def test_get_documents(client, auth_header):
    # Upload one first
    with patch("app.api.routes.documents.process_document_background"):
        client.post(
            f"{settings.API_V1_STR}/documents/upload",
            headers=auth_header,
            files={"file": ("list_test.txt", b"content", "text/plain")}
        )
    
    response = client.get(f"{settings.API_V1_STR}/documents/", headers=auth_header)
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert any(doc["filename"] == "list_test.txt" for doc in data)
