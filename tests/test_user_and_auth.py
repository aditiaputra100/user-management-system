from fastapi.testclient import TestClient
from tests.conftest import get_access_token, create_user, create_department, create_job, create_status_employee

def test_signin_success(client: TestClient):
    # Login for super user
    response = client.post("/login", data={"username": "superadmin@admin.com", "password": "superadmin"})
    assert response.status_code == 200

    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_signin_wrong_password(client: TestClient):
    response = client.post("/login", data={"username": "superadmin@admin.com", "password": "wrongpassword"})
    assert response.status_code == 401


def test_get_user_requires_auth(client: TestClient):
    resp = client.get("/me")
    assert resp.status_code == 401


def test_get_user_empty_list_for_active_user(client: TestClient):
    token = get_access_token(client, "superadmin@admin.com", "superadmin")

    resp = client.get("/employee", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json() == {"data": [], "count": 0}


def test_get_employee_status_empty_list(client: TestClient):
    token = get_access_token(client, "superadmin@admin.com", "superadmin")

    resp = client.get("/employee/status", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json() == {"data": [], "count": 0}


def test_post_employee_status_create_and_duplicate(client: TestClient):
    token = get_access_token(client, "superadmin@admin.com", "superadmin")

    payload = {"name": "Active", "description": "Active employee"}

    # Create
    resp = client.post("/employee/status", json=payload, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 201
    assert resp.json() == {"msg": f"Success created status {payload['name']}"}

    # Duplicate
    resp2 = client.post("/employee/status", json=payload, headers={"Authorization": f"Bearer {token}"})
    assert resp2.status_code == 409


def test_post_employee_status_inactive_user_forbidden(client: TestClient):
    create_user(username="inactive@user.com", password="p", status="inactive")
    get_access_token(client, "inactive@user.com", "p", status_code=423)

def test_signup_new_user(client: TestClient):
    token = get_access_token(client, "superadmin@admin.com", "superadmin")
    department = create_department(name="IT", description="Information Technology")
    job = create_job(department_id=department.id, name="Developer", description="Software Developer")
    employee_status = create_status_employee()

    employee_payload = {
        "full_name": "John Doe",
        "gender": True,
        "birthday": "1990-01-01T00:00:00Z",
        "email_address": "john.doe@google.com",
        "phone_number": "+6285156681103",
        "address": "123 Main St",
        "department": department.id,
        "job": job.id,
        "salary": 50000,
        "employee_status": employee_status.id,
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
    department = create_department(name="Random Department", description="Some Description")
    job = create_job(department_id=department.id, name="Manager", description="HR Manager")
    employee_status = create_status_employee(name="Part Time", description="Part Time Employee")

    employee_payload = {
        "full_name": "Jane Smith",
        "gender": False,
        "birthday": "1992-05-15T00:00:00Z",
        "email_address": "jane.smith@google.com",
        "phone_number": "+6285156681104",
        "address": "456 Oak Ave",
        "department": department.id,
        "job": job.id,
        "salary": 60000,
        "employee_status": employee_status.id,
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
    token = get_access_token(client, "superadmin@admin.com", "superadmin")
    department = create_department(name="Some Department", description="Finance Department")
    job = create_job(department_id=department.id, name="Accountant", description="Accountant")
    employee_status = create_status_employee(name="Contract", description="Contract Employee")

    employee_payload = {
        "full_name": "Bob Johnson",
        "gender": True,
        "birthday": "1988-03-20T00:00:00Z",
        "email_address": "bob.johnson@google.com",
        "phone_number": "+6285156681105",
        "address": "789 Pine Rd",
        "department": department.id,
        "job": job.id,
        "salary": 55000,
        "employee_status": employee_status.id,
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
    token = get_access_token(client, "superadmin@admin.com", "superadmin")
    department = create_department(name="Operations", description="Operations Department")
    job = create_job(department_id=department.id, name="Operator", description="Operations Specialist")
    employee_status = create_status_employee(name="Seasonal", description="Seasonal Employee")

    employee_payload = {
        "full_name": "Diana Evans",
        "gender": False,
        "birthday": "1991-07-14T00:00:00Z",
        "email_address": "not-an-email",  # Invalid email
        "phone_number": "+6285156681108",
        "address": "987 Cedar Ln",
        "department": department.id,
        "job": job.id,
        "salary": 52000,
        "employee_status": employee_status.id,
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
    token = get_access_token(client, "superadmin@admin.com", "superadmin")
    department = create_department(name="Support", description="Support Department")
    job = create_job(department_id=department.id, name="Support Agent", description="Customer Support")
    employee_status = create_status_employee(name="Probation", description="Probation Employee")

    employee_payload = {
        "full_name": "Edward Franklin",
        "gender": True,
        "birthday": "1986-12-02T00:00:00Z",
        "email_address": "edward.franklin@google.com",
        "phone_number": "12345",  # Invalid phone format
        "address": "159 Birch Ave",
        "department": department.id,
        "job": job.id,
        "salary": 40000,
        "employee_status": employee_status.id,
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