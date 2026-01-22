from fastapi.testclient import TestClient
from app.main import app, create_first_superuser
from app.database import get_session, Base
from app.auth.models import User
from app.auth.utils import get_password_hash
from app.employee.models import EmployeeStatus
from app.department.models import Department, Job
from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import sessionmaker
import pytest

client = TestClient(app)

engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_session():
    with TestingSessionLocal() as session:
        yield session

def create_user(username="user@user.com", password="p", status="active") -> User:
    password_hashed = get_password_hash(password)

    new_user = User(
        username=username,
        password_hash=password_hashed,
        status=status
    )

    with TestingSessionLocal() as db:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    
    return new_user

def create_department(name: str = "HR", description: str = "Human Resources") -> Department:
    new_department = Department(
        name=name,
        description=description
    )

    with TestingSessionLocal() as db:
        db.add(new_department)
        db.commit()
        db.refresh(new_department)
    
    return new_department

def create_job(department_id: int, name: str = "Software Engineer", description: str = "Software Engineer Job") -> Job:
    new_job = Job(
        department_id=department_id,
        name=name,
        description=description
    )

    with TestingSessionLocal() as db:
        db.add(new_job)
        db.commit()
        db.refresh(new_job)

    return new_job

def create_status_employee(name: str = "Full Time", description: str = "Full Time Employee") -> EmployeeStatus:
    new_status = EmployeeStatus(
        name=name,
        description=description
    )

    with TestingSessionLocal() as db:
        db.add(new_status)
        db.commit()
        db.refresh(new_status)

    return new_status

def get_access_token(client: TestClient, username: str, password: str, status_code: int = 200) -> str:
    resp = client.post("/login", data={"username": username, "password": password})
    assert resp.status_code == status_code
    
    if resp.status_code == 200:
        data = resp.json()
        return data["access_token"]

@pytest.fixture(scope="session")
def client():
    print("Setting up test client...")
    # Create the database tables
    Base.metadata.create_all(bind=engine)

    app.dependency_overrides[get_session] = override_get_session
    create_first_superuser(next(override_get_session()))

    yield TestClient(app)
    # Drop the database tables
    print("Tearing down test client...")
    Base.metadata.drop_all(bind=engine)

    app.dependency_overrides.clear()