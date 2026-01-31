from fastapi.testclient import TestClient
from app.auth.models import User
from app.auth.utils import get_password_hash
from app.employee.models import EmployeeStatus
from app.department.models import Department, Job
from app.policy.models import Role, Permission, role_permissions
from tests.conftest import TestingSessionLocal

def get_access_token(client: TestClient, username: str, password: str, status_code: int = 200) -> str:
    resp = client.post("/login", data={"username": username, "password": password})
    assert resp.status_code == status_code
    
    if resp.status_code == 200:
        data = resp.json()
        return data["access_token"]
    
def create_user(username="user@user.com", password="p", status="active", role_id=None, is_superuser=False) -> User:
    password_hashed = get_password_hash(password)

    new_user = User(
        username=username,
        password_hash=password_hashed,
        status=status,
        role_id=role_id,
        is_superuser=is_superuser
    )

    with TestingSessionLocal() as db:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    
    return new_user

def create_department(id: int, name: str = "HR", description: str = "Human Resources") -> Department:
    new_department = Department(
        id=id,
        name=name,
        description=description
    )

    with TestingSessionLocal() as db:
        db.add(new_department)
        db.commit()
        db.refresh(new_department)
    
    return new_department

def create_job(id: int, department_id: int, name: str = "Software Engineer", description: str = "Software Engineer Job") -> Job:
    new_job = Job(
        id=id,
        department_id=department_id,
        name=name,
        description=description
    )

    with TestingSessionLocal() as db:
        db.add(new_job)
        db.commit()
        db.refresh(new_job)

    return new_job

def create_status_employee(id: int, name: str = "Full Time", description: str = "Full Time Employee") -> EmployeeStatus:
    new_status = EmployeeStatus(
        id=id,
        name=name,
        description=description
    )

    with TestingSessionLocal() as db:
        db.add(new_status)
        db.commit()
        db.refresh(new_status)

    return new_status

def create_role(id:int, role_name: str = "Test Role", 
                                 description: str = "Test Role Description") -> Role:
    """Helper to create a role."""
    new_role = Role(
        id=id,
        name=role_name,
        description=description
    )
    
    with TestingSessionLocal() as db:
        db.add(new_role)
        db.commit()
        db.refresh(new_role)
    
    return new_role

def create_permission(id: int, name: str = "Test Permission", resource: str = "roles", action: str = "read", description: str = "Test") -> Permission:
    """Helper to create a permission."""
    new_permission = Permission(
        id=id,
        name=name,
        resource=resource,
        action=action,
        description=description
    )
    
    with TestingSessionLocal() as db:
        db.add(new_permission)
        db.commit()
        db.refresh(new_permission)
    
    return new_permission

def assign_role(role_id: int, permission_id: int):
    with TestingSessionLocal() as db:
        db.execute(role_permissions.insert(), {
            "role_id": role_id,
            "permission_id": permission_id
        })
        db.commit()