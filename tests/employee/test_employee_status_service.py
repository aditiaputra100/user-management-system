from app.database import Base
from app.employee.models import EmployeeStatus
from tests.conftest import TestingSessionLocal, engine
from sqlalchemy import select

def test_create_status(db):
    from app.employee.service import create_status

    create_status(
        name="Internship",
        description="Internship description",
        db=db
    )

    stmt = select(EmployeeStatus).where(EmployeeStatus.name == "Internship")
    employee_status = db.scalars(stmt).one_or_none()

    assert employee_status is not None
    assert employee_status.name == "Internship"
    assert employee_status.is_active

def test_get_all_status(db):
    from app.employee.service import get_all_status

    employee_statuses = get_all_status(db)

    assert len(employee_statuses) > 0
    assert employee_statuses[0].id == 10
    assert employee_statuses[0].name == "Full Time"

def setup_module():
    # Create the database tables 
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()

    employee_status = EmployeeStatus(
        id=10,
        name="Full Time",
        description="Description of Employee Status"
    )

    session.add(employee_status)
    session.commit()
    session.close()


def teardown_module():
    # Drop the database tables
    Base.metadata.drop_all(bind=engine)