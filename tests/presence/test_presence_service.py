from app.database import Base
from app.employee.models import Employee
from tests.conftest import engine, TestingSessionLocal
from sqlalchemy import select
from datetime import datetime
import pytest
import uuid

def test_create_presence(db):
    from app.presence.service import create_presence
    from app.presence.models import StatusType, Presence

    create_presence(
        status=StatusType.PRESENT,
        employee_id=uuid.UUID("00000000-0000-0000-0000-000000000001", version=4),
        db=db
    )

    stmt = select(Presence).where(Presence.employee_id == uuid.UUID("00000000-0000-0000-0000-000000000001", version=4))
    presence = db.scalars(stmt).one_or_none()

    assert presence is not None
    assert presence.clock_in is not None
    assert presence.status == StatusType.PRESENT.value
    assert presence.clock_out is None

    with pytest.raises(ValueError, match="Have filled in today's attendance"):
        create_presence(
        status=StatusType.ABSENT,
        employee_id=uuid.UUID("00000000-0000-0000-0000-000000000001", version=4),
        db=db
    )
        
    create_presence(
        status=StatusType.PRESENT,
        employee_id=uuid.UUID("00000000-0000-0000-0000-000000000001", version=4),
        db=db
    )

    presence = db.scalars(stmt).one_or_none()

    assert presence is not None
    assert presence.clock_in is not None
    assert presence.status == StatusType.PRESENT.value
    assert presence.clock_out is not None  

    db.delete(presence)       
    db.commit()

def test_create_presence_absent(db):
    from app.presence.service import create_presence
    from app.presence.models import StatusType, Presence

    create_presence(
        status=StatusType.ABSENT,
        employee_id=uuid.UUID("00000000-0000-0000-0000-000000000001", version=4),
        db=db
    )

    stmt = select(Presence).where(Presence.employee_id == uuid.UUID("00000000-0000-0000-0000-000000000001", version=4))
    presence = db.scalars(stmt).one_or_none()

    assert presence is not None
    assert presence.clock_in is None
    assert presence.status == StatusType.ABSENT.value
    assert presence.clock_out is None  

    with pytest.raises(ValueError, match="Have filled in today's attendance"):
        create_presence(
        status=StatusType.ON_LEAVE,
        employee_id=uuid.UUID("00000000-0000-0000-0000-000000000001", version=4),
        db=db
    )
        
    with pytest.raises(ValueError, match="Have filled in today's attendance"):
        create_presence(
        status=StatusType.ABSENT,
        employee_id=uuid.UUID("00000000-0000-0000-0000-000000000001", version=4),
        db=db
    )
        
    with pytest.raises(ValueError, match="Have filled in today's attendance"):
        create_presence(
        status=StatusType.PRESENT,
        employee_id=uuid.UUID("00000000-0000-0000-0000-000000000001", version=4),
        db=db
    )

def setup_module():
    from app.department.models import Department, Job
    from app.employee.models import EmployeeStatus
    # Create the database tables 
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()

    department = Department(
        id=11,
        name="Information Technology",
        description="Description of Department"
    )

    session.add(department)
    session.commit()

    job = Job(
        id=3,
        department_id=11,
        name="Software Engineer",
        description="Description of Job"
    )

    session.add(job)
    session.commit()

    employee_status = EmployeeStatus(
        id=10,
        name="Full Time",
        description="Description of Employee Status"
    )

    session.add(employee_status)
    session.commit()

    employee = Employee(
        id=uuid.UUID("00000000-0000-0000-0000-000000000001", version=4),
        full_name="John Doe",
        gender=True,
        birthday=datetime(year=1999, month=3, day=18),
        email_address="john.doe@email.com",
        phone_number="+62812345678910",
        address="Simple address",
        department_id=11,
        job_id=3,
        salary=3000000,
        employee_status_id=10,
    )

    session.add(employee)
    session.commit()

def teardown_module():
    # Drop the database tables
    Base.metadata.drop_all(bind=engine)