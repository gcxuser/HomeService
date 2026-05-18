"""PyTest configuration for HomeService."""
import pytest
from fastapi.testclient import TestClient
from HomeService.app import app


@pytest.fixture(scope="module")
def client():
    """Create a test client for the FastAPI app."""
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def auth_token(client):
    """Get authentication token for admin user."""
    response = client.post(
        "/api/admin/login",
        json={"username": "admin", "password": "password123"}
    )
    assert response.status_code == 200
    return response.json()["access_token"]
