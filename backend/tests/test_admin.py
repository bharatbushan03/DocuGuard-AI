import pytest
from app.core.config import settings
from app.models.user import User

@pytest.fixture
def admin_header(client, db):
    # Create admin user
    from app.core.security import get_password_hash
    admin = User(
        email="admin@example.com",
        hashed_password=get_password_hash("adminpass1"),
        full_name="Admin User",
        role="admin"
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    
    response = client.post(
        f"{settings.API_V1_STR}/auth/login",
        data={"username": "admin@example.com", "password": "adminpass1"},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def user_header(client, db):
    from app.core.security import get_password_hash

    user = User(
        email="user@example.com",
        hashed_password=get_password_hash("userpass1"),
        role="user",
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    response = client.post(
        f"{settings.API_V1_STR}/auth/login",
        data={"username": "user@example.com", "password": "userpass1"},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_get_admin_stats(client, admin_header):
    response = client.get(f"{settings.API_V1_STR}/admin/stats", headers=admin_header)
    assert response.status_code == 200
    assert "total_documents" in response.json()

def test_get_admin_stats_forbidden(client, user_header):
    response = client.get(f"{settings.API_V1_STR}/admin/stats", headers=user_header)
    assert response.status_code == 403

def test_get_query_logs(client, admin_header):
    response = client.get(f"{settings.API_V1_STR}/admin/query-logs", headers=admin_header)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_high_risk_queries(client, admin_header):
    response = client.get(f"{settings.API_V1_STR}/admin/high-risk", headers=admin_header)
    assert response.status_code == 200
