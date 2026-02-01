from app.database import Base
from app.department.models import Department, Job
from fastapi.testclient import TestClient
from tests.utils import get_access_token
from tests.conftest import engine

def test_create_department_and_duplicate(client: TestClient):
    token = get_access_token(client, "admin", "admin")

    payload = {"name": "HR", "description": "Human Resources"}

    resp = client.post("/department/", json=payload, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 201
    assert resp.json() == {"msg": f"Success created department {payload['name']}"}

    # Duplicate
    resp2 = client.post("/department/", json=payload, headers={"Authorization": f"Bearer {token}"})
    assert resp2.status_code == 409

def test_get_department_not_found(client: TestClient):
    resp = client.get("/department/999")

    assert resp.status_code == 404

def test_update_department(client: TestClient):
    token = get_access_token(client, "admin", "admin")

    update_payload = {"name": "Finance New", "description": "Updated"}
    resp = client.put("/department/1", json=update_payload, headers={"Authorization": f"Bearer {token}"})

    assert resp.status_code == 200
    assert resp.json() == {"msg": "Success updated department with ID 1"}

def test_create_job_success_and_notfound(client: TestClient):
    token = get_access_token(client, "admin", "admin")

    # Create job successfully
    job_payload = {"name": "Backend", "description": "Backend dev", "is_active": True}
    resp = client.post("/department/1/job", json=job_payload, headers={"Authorization": f"Bearer {token}"})

    assert resp.status_code == 201
    assert resp.json() == {"msg": f"Success created job {job_payload["name"]} for department ID 1"}

    # Create job for not found department
    resp = client.post("/department/999/job", json={"name": "Ops", "description": "ops"}, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 404

def setup_module():
    from tests.utils import create_user, create_department, create_job

    # Create the database tables 
    Base.metadata.create_all(bind=engine)

    # Create superadmin
    create_user("admin", "admin", "active", is_superuser=True)

    create_department(id=1, name="IT", description="Description")
    create_job(id=1, department_id=1)

def teardown_module():
    # Drop the database tables 
    Base.metadata.drop_all(bind=engine)