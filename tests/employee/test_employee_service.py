from app.database import Base
from app.employee.models import Employee, EmployeeStatus
from app.employee.schemas import CreateEmployeeSchema, CreateUserSchema
from app.department.models import Department, Job
from tests.conftest import TestingSessionLocal, engine
from datetime import datetime
from sqlalchemy import select
import uuid

def test_get_all(db):
    from app.employee.service import get_all

    employees = get_all(10, 1, db)

    assert len(employees) > 0
    assert employees[0].id == uuid.UUID("00000000-0000-0000-0000-000000000001", version=4)
    assert employees[0].full_name == "John Doe"
    assert employees[0].department.name == "Information Technology"
    assert employees[1].salary == 3000000

def test_get_by_id(db):
    from app.employee.service import get_by_id

    employee = get_by_id(uuid.UUID("00000000-0000-0000-0000-000000000002", version=4), db)

    assert employee != None
    assert employee.full_name == "Doe John"
    assert employee.job == "Software Engineer"

def test_get_by_email(db):
    from app.employee.service import get_by_email

    employee = get_by_email("john.doe@email.com", db)

    assert employee != None
    assert employee.full_name == "John Doe"
    assert employee.gender
    assert employee.employee_status.name == "Full Time"

def test_create(db):
    from app.employee.service import create
    from app.auth.models import User
    from app.auth.utils import verify_password

    new_employee = CreateEmployeeSchema(
        full_name="New employee",
        gender=False,
        birthday=datetime(year=2003, month=12, day=1),
        hire_date=datetime.now(),
        email_address="new_employee@email.com",
        phone_number="+6285555555555",
        address="new address",
        department=11,
        job=3,
        salary=5000000,
        employee_status=10
    )

    new_user = CreateUserSchema(
        username="new_employee",
        password="new_employee123",
        status="active"
    )

    create(
        new_employee,
        new_user,
        db=db
    )

    stmt = select(Employee).where(Employee.full_name == "New employee")
    employee = db.scalars(stmt).one_or_none()

    assert employee is not None
    assert employee.full_name == "New employee"
    assert employee.salary == 5000000
    assert employee.employee_status.name == "Full Time"

    stmt = select(User).where(User.username == "new_employee")
    user = db.scalars(stmt).one_or_none()

    assert user is not None
    assert user.username == "new_employee"
    assert verify_password("new_employee123", user.password_hash)

def test_update(db):
    from app.employee.service import update

    update_employee = CreateEmployeeSchema(
        full_name="John Doe Updated",
        gender=True,
        birthday=datetime(year=1999, month=3, day=18),
        hire_date=datetime.now(),
        email_address="john.doe@email.com",
        phone_number="+62812345678910",
        address="Simple address",
        department=11,
        job=3,
        salary=3000000,
        employee_status=10,
    )

    update(
        id=uuid.UUID("00000000-0000-0000-0000-000000000001", version=4),
        employee=update_employee,
        db=db
    )

    employee = db.get(Employee, uuid.UUID("00000000-0000-0000-0000-000000000001", version=4))

    assert employee is not None
    assert employee.full_name == "John Doe Updated"
    assert employee.updated_at.hour == datetime.now().hour

def test_delete(db):
    from app.employee.service import delete

    delete(
        id=uuid.UUID("00000000-0000-0000-0000-000000000001", version=4),
        db=db
    )

    employee = db.get(Employee, uuid.UUID("00000000-0000-0000-0000-000000000001", version=4))

    assert employee is None

def setup_module():
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

    employee_john = Employee(
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
    employee_doe = Employee(
        id=uuid.UUID("00000000-0000-0000-0000-000000000002", version=4),
        full_name="Doe John",
        gender=True,
        birthday=datetime(year=1999, month=3, day=18),
        email_address="doe.john@email.com",
        phone_number="+6281111111111",
        address="Simple address",
        department_id=11,
        job_id=3,
        salary=3000000,
        employee_status_id=10,
    )

    session.add_all([employee_john, employee_doe])
    session.commit()

    session.close()


def teardown_module():
    # Drop the database tables
    Base.metadata.drop_all(bind=engine)