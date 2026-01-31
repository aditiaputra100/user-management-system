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

engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_session():
    with TestingSessionLocal() as session:
        yield session

@pytest.fixture(scope="session")
def client():
    app.dependency_overrides[get_session] = override_get_session

    yield TestClient(app)

    app.dependency_overrides.clear()

@pytest.fixture
def db():
    # Create the database tables
    # Base.metadata.create_all(bind=engine)

    with TestingSessionLocal() as Session:
        yield Session
    
    # Drop the database tables
    # Base.metadata.drop_all(bind=engine)