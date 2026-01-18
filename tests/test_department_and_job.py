from fastapi.testclient import TestClient
from app.models.user import Department, Job
from tests.conftest import get_access_token, TestingSessionLocal


def test_create_department_and_duplicate(client: TestClient):
    token = get_access_token(client, "superadmin@admin.com", "superadmin")

    payload = {"name": "HR", "description": "Human Resources"}

    resp = client.post("/department/", json=payload, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json() == {"msg": f"Success created department {payload['name']}"}

    # Duplicate
    resp2 = client.post("/department/", json=payload, headers={"Authorization": f"Bearer {token}"})
    assert resp2.status_code == 409


def test_get_department_not_found(client: TestClient):
    resp = client.get("/department/999")
    assert resp.status_code == 404


def test_update_and_patch_and_delete_department(client: TestClient):
    token = get_access_token(client, "superadmin@admin.com", "superadmin")

    payload = {"name": "Finance", "description": "Finance Dept"}
    resp = client.post("/department/", json=payload, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200

    with TestingSessionLocal() as db:
        dept = db.query(Department).filter(Department.name == payload["name"]).one()
        dept_id = dept.id

    # Update
    update_payload = {"name": "FinanceNew", "description": "Updated"}
    resp = client.put(f"/department/{dept_id}", json=update_payload, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json() == {"msg": f"Update department with ID {dept_id} was successfully"}

    # Patch status deactivate
    resp = client.patch(f"/department/{dept_id}?activated=false", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json() == {"msg": f"Update department status with ID {dept_id} was successfully"}

    # Delete -> sets is_active False
    resp = client.delete(f"/department/{dept_id}", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json() == {"msg": f"Success delete department with ID {dept_id}"}


def test_create_job_success_and_inactive_and_notfound_and_get_and_delete(client: TestClient):
    token = get_access_token(client, "superadmin@admin.com", "superadmin")

    # Create department
    payload = {"name": "Engineering", "description": "Engineering Dept"}
    resp = client.post("/department/", json=payload, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200

    with TestingSessionLocal() as db:
        dept = db.query(Department).filter(Department.name == payload["name"]).one()
        dept_id = dept.id

    # Create job successfully
    job_payload = {"name": "Backend", "description": "Backend dev", "is_active": True}
    resp = client.post(f"/department/{dept_id}/job", json=job_payload, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 201
    assert resp.json() == {"msg": f"Success created job {job_payload['name']} in {payload['name']}"}

    # Get jobs
    resp = client.get(f"/department/{dept_id}/job", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["count"] == 1
    assert data["data"][0]["name"] == job_payload["name"]

    # Deactivate department and ensure creating job fails with 406
    resp = client.patch(f"/department/{dept_id}?activated=false", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200

    resp = client.post(f"/department/{dept_id}/job", json={"name": "Frontend", "description": "FE"}, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 406

    # Create job for not found department -> current behavior produces 500
    resp = client.post("/department/999/job", json={"name": "Ops", "description": "ops"}, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 422

    # Re-activate department for subsequent tests
    with TestingSessionLocal() as db:
        d = db.get(Department, dept_id)
        d.is_active = True
        db.commit()

    # Create another job so we can delete it
    resp = client.post(f"/department/{dept_id}/job", json={"name": "QA", "description": "QA"}, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 201

    with TestingSessionLocal() as db:
        job = db.query(Job).filter(Job.name == "QA").one()
        job_id = job.id

    # Create another department to test mismatch deletion
    resp = client.post("/department/", json={"name": "Other", "description": "Other"}, headers={"Authorization": f"Bearer {token}"})
    with TestingSessionLocal() as db:
        other = db.query(Department).filter(Department.name == "Other").one()
        other_id = other.id

    resp = client.delete(f"/department/{other_id}/job/{job_id}", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 403

    # Delete job with correct department id
    resp = client.delete(f"/department/{dept_id}/job/{job_id}", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert "Success delete job" in resp.json()["msg"]
