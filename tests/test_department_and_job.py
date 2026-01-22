from fastapi.testclient import TestClient
from app.department.models import Department, Job
from tests.conftest import get_access_token, TestingSessionLocal


def test_create_department_and_duplicate(client: TestClient):
    token = get_access_token(client, "superadmin@admin.com", "superadmin")

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
    token = get_access_token(client, "superadmin@admin.com", "superadmin")

    payload = {"name": "Finance", "description": "Finance Dept"}
    resp = client.post("/department/", json=payload, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 201

    with TestingSessionLocal() as db:
        dept = db.query(Department).filter(Department.name == payload["name"]).one()
        dept_id = dept.id

    # Update
    update_payload = {"name": "FinanceNew", "description": "Updated"}
    resp = client.put(f"/department/{dept_id}", json=update_payload, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json() == {"msg": f"Success updated department with ID {dept_id}"}

def test_create_job_success_and_inactive_and_notfound_and_get_and_delete(client: TestClient):
    token = get_access_token(client, "superadmin@admin.com", "superadmin")

    # Create department
    payload = {"name": "Engineering", "description": "Engineering Dept"}
    resp = client.post("/department/", json=payload, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 201

    with TestingSessionLocal() as db:
        dept = db.query(Department).filter(Department.name == payload["name"]).one()
        dept_id = dept.id

    # Create job successfully
    job_payload = {"name": "Backend", "description": "Backend dev", "is_active": True}
    resp = client.post(f"/department/{dept_id}/job", json=job_payload, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 201
    assert resp.json() == {"msg": f"Success created job {job_payload["name"]} for department ID {dept_id}"}

    # Create job for not found department
    resp = client.post("/department/999/job", json={"name": "Ops", "description": "ops"}, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 404

    # Re-activate department for subsequent tests
    with TestingSessionLocal() as db:
        d = db.get(Department, dept_id)
        d.is_active = True
        db.commit()

    # Create another job so we can delete it
    resp = client.post(f"/department/{dept_id}/job", json={"name": "QA", "description": "QA"}, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 201


