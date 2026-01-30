from app.department.models import Department, Job
from app.database import Base
from tests.conftest import engine, TestingSessionLocal
from sqlalchemy.orm import Session
from sqlalchemy import select
import pytest

def test_create_job(db):
    from app.department.service import create_job

    create_job(
        department_id=67,
        name="Job on Department IT",
        description="Description of Job",
        db=db
    )

    stmt = select(Job).where(Job.name == "Job on Department IT")
    job: Job | None = db.scalars(stmt).one_or_none()

    assert job != None
    assert job.department_id == 67
    assert job.name == "Job on Department IT"
    assert job.is_active == True

def test_create_job_duplicate(db):
    from app.department.service import create_job

    create_job(
        department_id=67,
        name="Software Developer",
        description="Description of Job",
        db=db
    )
    create_job(
        department_id=69,
        name="Software Developer",
        description="Description of Job",
        db=db
    )

    with pytest.raises(ValueError, match="Duplicate entry job Software Developer"):
        create_job(
        department_id=67,
        name="Software Developer",
        description="Description of Job",
        db=db
    )

def setup_module():
    # Create the database tables
    Base.metadata.create_all(bind=engine)

    department_it = Department(
        id=67,
        name="IT",
        description="Description of Department"
    )
    department_if = Department(
        id=69,
        name="IF",
        description="Description of Department"
    )

    session: Session = TestingSessionLocal()
    session.add_all([department_it, department_if])
    session.commit()
    session.close()

def teardown_module():
    # Drop the database tables
    Base.metadata.drop_all(bind=engine)