from app.database import Base
from tests.utils import get_access_token
from tests.conftest import engine
from fastapi.testclient import TestClient

def test_signin_success(client: TestClient):
    # Login for super user
    response = client.post("/login", data={"username": "admin", "password": "admin"})
    assert response.status_code == 200

    data = response.json()
    
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_signin_wrong_password(client: TestClient):
    response = client.post("/login", data={"username": "admin", "password": "admin123"})
    assert response.status_code == 401

def test_signin_inactive_user(client: TestClient):
    response = client.post("/login", data={"username": "inactive", "password": "inactive"})
    assert response.status_code == 423

def test_get_user_requires_auth(client: TestClient):
    resp = client.get("/me")
    assert resp.status_code == 401

    token = get_access_token(client, "admin", "admin")

    resp = client.get("/me", headers={"Authorization": f"Bearer {token}"})
    data = resp.json()
    assert resp.status_code == 200
    assert data["username"] == "admin"
    assert data["status"] == "active"

def test_get_user_empty_list_for_active_user(client: TestClient):
    token = get_access_token(client, "admin", "admin")

    resp = client.get("/employee", headers={"Authorization": f"Bearer {token}"})

    assert resp.status_code == 200
    assert resp.json() == {"data": [], "count": 0}

def test_get_employee_status(client: TestClient):
    token = get_access_token(client, "admin", "admin")

    resp = client.get("/employee/status", headers={"Authorization": f"Bearer {token}"})

    assert resp.status_code == 200
    assert resp.json() == {"data": [
        {
            "name": "Full Time",
            "description": "Description",
            "is_active": True,
            "id": 77
        }
    ], "count": 1}

def test_post_employee_status_create_and_duplicate(client: TestClient):
    token = get_access_token(client, "admin", "admin")

    payload = {"name": "Internship", "description": "Internship employee"}

    resp = client.post("/employee/status", json=payload, headers={"Authorization": f"Bearer {token}"})

    assert resp.status_code == 201
    assert resp.json() == {"msg": f"Success created status {payload['name']}"}

    # Duplicate
    resp2 = client.post("/employee/status", json=payload, headers={"Authorization": f"Bearer {token}"})
    assert resp2.status_code == 409

def test_signup_new_user(client: TestClient):
    token = get_access_token(client, "admin", "admin")

    employee_payload = {
        "full_name": "John Doe",
        "gender": True,
        "birthday": "1990-01-01T00:00:00Z",
        "email_address": "john.doe@google.com",
        "phone_number": "+6285156681103",
        "address": "123 Main St",
        "department": 1,
        "job": 1,
        "salary": 5000000,
        "employee_status": 77,
        "hire_date": "2023-01-01T00:00:00Z"
    }
    user_payload = {
        "username": "johndoe",
        "password": "SecurePass@123",
        "status": "active"
    }
    
    payload = {
        "employee": employee_payload,
        "user": user_payload
    }

    resp = client.post("/employee", json=payload, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 201
    assert resp.json() == {"msg": "Employee and user created successfully"}

def test_signup_requires_auth(client: TestClient):
    """Test that signup requires authentication"""

    employee_payload = {
        "full_name": "Jane Smith",
        "gender": False,
        "birthday": "1992-05-15T00:00:00Z",
        "email_address": "jane.smith@google.com",
        "phone_number": "+6285156681104",
        "address": "456 Oak Ave",
        "department": 1,
        "job": 1,
        "salary": 60000,
        "employee_status": 77,
        "hire_date": "2023-06-01T00:00:00Z"
    }
    user_payload = {
        "username": "janesmith",
        "password": "SecurePass@456",
        "status": "active"
    }
    
    payload = {
        "employee": employee_payload,
        "user": user_payload
    }

    resp = client.post("/employee", json=payload)
    assert resp.status_code == 401

def test_signup_weak_password(client: TestClient):
    """Test that weak passwords are rejected"""
    token = get_access_token(client, "admin", "admin")

    employee_payload = {
        "full_name": "Bob Johnson",
        "gender": True,
        "birthday": "1988-03-20T00:00:00Z",
        "email_address": "bob.johnson@google.com",
        "phone_number": "+6285156681105",
        "address": "789 Pine Rd",
        "department": 1,
        "job": 1,
        "salary": 55000,
        "employee_status": 77,
        "hire_date": "2023-07-01T00:00:00Z"
    }
    user_payload = {
        "username": "bobjohnson",
        "password": "weak",  #less than 8
        "status": "active"
    }
    
    payload = {
        "employee": employee_payload,
        "user": user_payload
    }

    resp = client.post("/employee", json=payload, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 422

    resp_json = resp.json()

    assert "Password must be at least 8 characters long" in resp_json["detail"][0]["msg"]

def test_signup_invalid_email(client: TestClient):
    """Test that invalid email addresses are rejected"""
    token = get_access_token(client, "admin", "admin")

    employee_payload = {
        "full_name": "Diana Evans",
        "gender": False,
        "birthday": "1991-07-14T00:00:00Z",
        "email_address": "not-an-email",  # Invalid email
        "phone_number": "+6285156681108",
        "address": "987 Cedar Ln",
        "department": 1,
        "job": 1,
        "salary": 52000,
        "employee_status": 77,
        "hire_date": "2023-10-01T00:00:00Z"
    }
    user_payload = {
        "username": "dianaevans",
        "password": "SecurePass@789",
        "status": "active"
    }
    
    payload = {
        "employee": employee_payload,
        "user": user_payload
    }

    resp = client.post("/employee", json=payload, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 422


def test_signup_invalid_phone(client: TestClient):
    """Test that invalid phone numbers are rejected"""
    token = get_access_token(client, "admin", "admin")

    employee_payload = {
        "full_name": "Edward Franklin",
        "gender": True,
        "birthday": "1986-12-02T00:00:00Z",
        "email_address": "edward.franklin@google.com",
        "phone_number": "12345",  # Invalid phone format
        "address": "159 Birch Ave",
        "department": 1,
        "job": 1,
        "salary": 40000,
        "employee_status": 77,
        "hire_date": "2023-11-01T00:00:00Z"
    }
    user_payload = {
        "username": "edwardfranklin",
        "password": "SecurePass@456",
        "status": "active"
    }
    
    payload = {
        "employee": employee_payload,
        "user": user_payload
    }

    resp = client.post("/employee", json=payload, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 422

def setup_module():
    from tests.utils import create_user, create_department, create_job, create_status_employee

    # Create the database tables 
    Base.metadata.create_all(bind=engine)
    # session = TestingSessionLocal()

    # Create superadmin
    # admin = User(
    #     id=uuid.UUID("00000000-0000-0000-0000-000000000001", version=4),
    #     username="admin",
    #     passhowrd_has=get_password_hash("admin"),
    #     is_superuser=True,
    # )
    create_user("admin", "admin", "active", is_superuser=True)

    # Create inactive user
    # inactive = User(
    #     id=uuid.UUID("00000000-0000-0000-0000-000000000002", version=4),
    #     username="inactive",
    #     passhowrd_has=get_password_hash("inactive"),
    #     is_superuser=True,
    # )
    create_user("inactive", "inactive", "inactive")

    create_department(id=1, name="IT", description="Description")
    create_job(id=1, department_id=1)
    create_status_employee(id=77, name="Full Time", description="Description")

    # session.add_all([admin, inactive])
    # session.commit()
    
    # session.close()


def teardown_module():
    # Drop the database tables 
    Base.metadata.drop_all(bind=engine)