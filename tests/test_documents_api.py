from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_upload_document():
    email = f"document-{uuid4()}@example.com"
    password = "TestPassword123!"

    register_response = client.post(
        "/auth/register",
        json={
            "full_name": "Document Test User",
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

    file_content = b"Test document content."

    response = client.post(
        "/documents/upload",
        headers={
            "Authorization": f"Bearer {token}",
        },
        files={
            "file": (
                "test.pdf",
                file_content,
                "application/pdf",
            ),
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["original_filename"] == "test.pdf"