"""Tests for user-related API endpoints."""
import pytest
from fastapi.testclient import TestClient
from HomeService.app import app
from HomeService.db.session import SessionLocal
from HomeService.db.models import User, UserAddress


@pytest.fixture(scope="module")
def client():
    """Create a test client."""
    with TestClient(app) as c:
        yield c


def test_create_user(client):
    """Test creating a new user."""
    response = client.post(
        "/api/users",
        json={
            "name": "测试用户",
            "phone": "13800138001"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "测试用户"
    assert data["phone"] == "13800138001"


def test_get_user(client):
    """Test getting a user by ID."""
    # First create a user
    create_response = client.post(
        "/api/users",
        json={"name": "测试用户2", "phone": "13800138002"}
    )
    assert create_response.status_code == 201
    user_id = create_response.json()["user_id"]

    # Then get the user
    response = client.get(f"/api/users/{user_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "测试用户2"


def test_add_address(client):
    """Test adding an address for a user."""
    # First create a user
    create_response = client.post(
        "/api/users",
        json={"name": "测试用户3", "phone": "13800138003"}
    )
    user_id = create_response.json()["user_id"]

    # Add address
    response = client.post(
        f"/api/users/{user_id}/addresses",
        json={
            "city": "北京市",
            "district": "朝阳区",
            "community": "望京soho",
            "detail_address": "test address"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["address_id"] is not None


def test_get_user_addresses(client):
    """Test getting addresses for a user."""
    # First create a user and add an address
    create_response = client.post(
        "/api/users",
        json={"name": "测试用户4", "phone": "13800138004"}
    )
    user_id = create_response.json()["user_id"]

    address_response = client.post(
        f"/api/users/{user_id}/addresses",
        json={"city": "北京市", "district": "朝阳区", "community": "test", "detail_address": "test"}
    )
    assert address_response.status_code == 200

    # Get addresses
    response = client.get(f"/api/users/{user_id}/addresses")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "addresses" in data
    addresses = data["addresses"]
    assert isinstance(addresses, list)
    assert len(addresses) >= 1
