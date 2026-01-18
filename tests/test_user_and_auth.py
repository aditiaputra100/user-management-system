from fastapi.testclient import TestClient
from tests.conftest import get_access_token, create_user

def test_signin_success(client: TestClient):
    # Login for super user
    response = client.post("/auth/signin", data={"username": "superadmin@admin.com", "password": "superadmin"})
    assert response.status_code == 200

    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_signin_wrong_password(client: TestClient):
    response = client.post("/auth/signin", data={"username": "superadmin@admin.com", "password": "wrongpassword"})
    assert response.status_code == 401


def test_get_user_requires_auth(client: TestClient):
    resp = client.get("/user")
    assert resp.status_code == 401


def test_get_user_empty_list_for_active_user(client: TestClient):
    token = get_access_token(client, "superadmin@admin.com", "superadmin")

    resp = client.get("/user", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json() == {"data": [], "count": 0}


def test_get_employee_status_empty_list(client: TestClient):
    token = get_access_token(client, "superadmin@admin.com", "superadmin")

    resp = client.get("/user/status", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json() == {"data": [], "count": 0}


def test_post_employee_status_create_and_duplicate(client: TestClient):
    token = get_access_token(client, "superadmin@admin.com", "superadmin")

    payload = {"name": "Active", "description": "Active employee"}

    # Create
    resp = client.post("/user/status", json=payload, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 201
    assert resp.json() == {"msg": f"Success created status {payload['name']}"}

    # Duplicate
    resp2 = client.post("/user/status", json=payload, headers={"Authorization": f"Bearer {token}"})
    assert resp2.status_code == 409


def test_post_employee_status_inactive_user_forbidden(client: TestClient):
    create_user(username="inactive@user.com", password="p", status="inactive")
    token = get_access_token(client, "inactive@user.com", "p")

    payload = {"name": "On Leave", "description": "Employee on leave"}
    resp = client.post("/user/status", json=payload, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 403