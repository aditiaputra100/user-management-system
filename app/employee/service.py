from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.auth.models import User
from app.auth.utils import get_password_hash
from .models import Employee, EmployeeStatus
from .schemas import CreateUserSchema, CreateEmployeeSchema

def get_all(db: Session) -> list[Employee]:
    stmt = select(Employee)
    employees: list[Employee] = db.scalars(stmt).all()
    return employees

def get_by_id(employee_id: str, db: Session) -> Employee | None:
    stmt = select(Employee).where(Employee.id == employee_id)
    employee: Employee | None = db.scalars(stmt).one_or_none()
    
    return employee

def get_by_email(email: str, db: Session) -> Employee | None:
    stmt = select(Employee).where(Employee.email_address == email)
    employee: Employee | None = db.scalars(stmt).one_or_none()
    
    return employee

def create(employee: CreateEmployeeSchema, user: CreateUserSchema, db: Session) -> None:
    try:
        new_emplopyee = Employee(
            full_name=employee.full_name,
            gender=employee.gender,
            birthday=employee.birthday,
            email_address=employee.email_address,
            phone_number=employee.phone_number,
            address=employee.address,
            department_id=employee.department,
            job_id=employee.job,
            salary=employee.salary,
            employee_status_id=employee.employee_status,
            hire_date=employee.hire_date
        )

        db.add(new_emplopyee)
        db.flush()

        password_hashed = get_password_hash(user.password)

        user = User(
            employee_id=new_emplopyee.id,
            username=user.username,
            password_hash=password_hashed,
            status=user.status
        )

        db.add(user)
        db.commit()
    except IntegrityError as err:
        db.rollback()
        raise ValueError("Duplicate entry for employee or user")
    except Exception as err:
        db.rollback()
        raise RuntimeError(str(err))
    
def create_status(name: str, description: str, db: Session, is_active: bool = True) -> None:
    try:
        employee_status = EmployeeStatus(
            name=name,
            description=description,
            is_active=is_active
        )

        db.add(employee_status)
        db.commit()
    except IntegrityError as err:
        db.rollback()
        raise ValueError(f"Duplicate entry {name}")
    except Exception as err:
        db.rollback()
        raise RuntimeError(str(err))

def get_all_status(db: Session) -> list[EmployeeStatus]:
    stmt = select(EmployeeStatus)
    status: list[EmployeeStatus] = db.scalars(stmt).all()
    
    return status

def update_status(id: int, name: str, description: str | None, is_active: bool | None, db: Session):
    emp_status = db.get(EmployeeStatus, id)

    if not emp_status:
        raise NameError(f"Employee status ID {id} is not found")
    
    emp_status.name = name

    if description is not None:
        emp_status.description = description
    
    if is_active is not None:
        emp_status.is_active = is_active

    try:
        db.commit()
    
    except IntegrityError:
        db.rollback()
        raise ValueError(f"Employee status with name {name} had already exists")

    except Exception as err:
        db.rollback()
        raise RuntimeError(str(err))
    
def delete_status(id: int, db: Session):
    emp_status = db.get(EmployeeStatus, id)

    if emp_status is None:
        raise NameError(f"Employee status ID {id} is not found")
    
    try:
        db.delete(emp_status)
        db.commit()
    
    except Exception as err:
        db.rollback()
        raise RuntimeError(str(err))