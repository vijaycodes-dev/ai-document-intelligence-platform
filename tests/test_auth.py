from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_register_user():
    email = f"test-{uuid4()}@example.com"

    response = client.post(
        "/auth/register",
        json={
            "full_name": "Test User",
            "email": email,
            "password": "TestPassword123!",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["email"] == email
    assert data["full_name"] == "Test User"
    
    
def test_login_user():
    email = f"login-{uuid4()}@example.com"
    password = "TestPassword123!"

    register_response = client.post(
        "/auth/register",
        json={
            "full_name": "Login Test User",
            "email": email,
            "password": password,
        },
    )

    assert register_response.status_code == 201

    login_response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": password,
        },
    )

    assert login_response.status_code == 200

    data = login_response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"
    
    
def test_get_current_user():
    email = f"me-{uuid4()}@example.com"
    password = "TestPassword123!"

    register_response = client.post(
        "/auth/register",
        json={
            "full_name": "Current User",
            "email": email,
            "password": password,
        },
    )

    assert register_response.status_code == 201

    login_response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": password,
        },
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    me_response = client.get(
        "/auth/me",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert me_response.status_code == 200

    data = me_response.json()

    assert data["email"] == email
    assert data["full_name"] == "Current User"