import pytest
from app.core.config import settings

@pytest.fixture
def auth_header(client):
    client.post(
        f"{settings.API_V1_STR}/auth/register",
        json={"email": "chat@example.com", "password": "password123"},
    )
    response = client.post(
        f"{settings.API_V1_STR}/auth/login",
        data={"username": "chat@example.com", "password": "password123"},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_chat_query_success(client, auth_header):
    response = client.post(
        f"{settings.API_V1_STR}/chat/query",
        headers=auth_header,
        json={"question": "What is the company policy on remote work?"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "citations" in data
    assert data["answer"] == "Test answer from context."
    assert "session_id" in data

def test_chat_query_high_risk(client, auth_header, mock_openai_chat):
    # Mock a high-risk question/answer
    mock_openai_chat.chat.completions.create.return_value.choices[0].message.content = \
        '{"answer": "To terminate an employee, you must...", "citations": [], "confidence_reasoning": "Rules.", "requires_human_review": true}'
    
    response = client.post(
        f"{settings.API_V1_STR}/chat/query",
        headers=auth_header,
        json={"question": "How do I fire someone?"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["risk_level"] == "high"
    assert data["requires_human_review"] == True

def test_chat_sessions(client, auth_header):
    # Create a session by querying
    client.post(
        f"{settings.API_V1_STR}/chat/query",
        headers=auth_header,
        json={"question": "Question 1"}
    )
    
    response = client.get(f"{settings.API_V1_STR}/chat/sessions", headers=auth_header)
    assert response.status_code == 200
    assert len(response.json()) >= 1
