import pytest
from app.core.config import settings

def test_register_user(client):
    response = client.post(
        f"{settings.API_V1_STR}/auth/register",
        json={
            "email": "test@example.com",
            "password": "password123",
            "full_name": "Test User"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "id" in data

def test_login_user(client):
    # Register first
    client.post(
        f"{settings.API_V1_STR}/auth/register",
        json={
            "email": "login@example.com",
            "password": "password123",
            "full_name": "Login User"
        }
    )
    
    # Login
    response = client.post(
        f"{settings.API_V1_STR}/auth/login",
        data={
            "username": "login@example.com",
            "password": "password123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_wrong_password(client):
    # Register first
    client.post(
        f"{settings.API_V1_STR}/auth/register",
        json={
            "email": "wrong@example.com",
            "password": "password123",
            "full_name": "Wrong User"
        }
    )
    
    # Login with wrong password
    response = client.post(
        f"{settings.API_V1_STR}/auth/login",
        data={
            "username": "wrong@example.com",
            "password": "wrongpassword"
        }
    )
    assert response.status_code == 401
