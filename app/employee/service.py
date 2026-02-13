from datetime import datetime
from sqlalchemy import select
from sqlalchemy.orm import Session, load_only, selectinload
from sqlalchemy.exc import IntegrityError
from app.auth.models import User
from app.auth.utils import get_password_hash
from app.department.models import Department, Job
from .models import Employee, EmployeeStatus
from .schemas import CreateUserSchema, CreateEmployeeSchema

def get_all(limit, offset, db: Session) -> list[Employee]:
    offset = (max(1, offset) - 1) * limit

    stmt = select(Employee).limit(limit).offset(offset)
    employees: list[Employee] = db.scalars(stmt).all()
    return employees

def get_by_id(employee_id: str, db: Session):
    stmt = select(
        Employee.id,
        Employee.full_name,
        Employee.gender,
        Employee.birthday,
        Employee.email_address,
        Employee.phone_number,
        Employee.address,
        Department.name.label('department'),
        Job.name.label('job'),
        Employee.salary,
        EmployeeStatus.name.label('employee_status'),
        Employee.hire_date,
        Employee.created_at,
        Employee.updated_at,
    ).select_from(Employee).join(
        Department, Employee.department_id == Department.id
        ).join(
            Job, Employee.job_id == Job.id
            ).outerjoin(
                EmployeeStatus, Employee.employee_status_id == EmployeeStatus.id
                ).where(Employee.id == employee_id)
    
    result = db.execute(stmt).one_or_none()
    
    if result is None:
        return None
    
    return result._mapping

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
            status=user.status,
            role_id=user.role_id,
        )

        db.add(user)
        db.commit()
    except IntegrityError as err:
        db.rollback()
        raise ValueError("Duplicate entry for employee or user")
    except Exception as err:
        db.rollback()
        raise RuntimeError(str(err))
    
def update(id: str, employee: CreateEmployeeSchema, db: Session) -> None:
    find_employee = db.get(Employee, id)

    if find_employee is None:
        raise NameError(f"Employee ID {id} is not found")
    
    try:
        find_employee.full_name = employee.full_name
        find_employee.gender = employee.gender
        find_employee.birthday = employee.birthday
        find_employee.email_address = employee.email_address
        find_employee.phone_number = employee.phone_number
        find_employee.address = employee.address
        find_employee.department_id = employee.department
        find_employee.job_id = employee.job
        find_employee.salary = employee.salary
        find_employee.employee_status_id = employee.employee_status
        find_employee.hire_date = employee.hire_date
        find_employee.updated_at = datetime.now()

        db.commit()
        
    except IntegrityError as err:
        db.rollback()

        error_message = err.orig
        
        if "UNIQUE constraint failed" in error_message or "duplicate key value violates unique constraint" in error_message:
            # Handle unique constraint violation specifically
            raise ValueError(f"Email '{employee.email_address}' already exists.")
        
        elif "FOREIGN KEY constraint failed" in error_message:
            # Handle foreign key violation
            raise NameError("Error: Associated data does not exist.")
        
        else:
            # Handle other integrity errors
            print(f"An unexpected integrity error occurred: {error_message}")
            raise RuntimeError("An unexpected error occurred.")
        
    except Exception as err:
        db.rollback()
        raise RuntimeError(str(err))

def delete(id: str, db: Session) -> None:
    employee = db.get(Employee, id)

    if employee is None:
        raise NameError(f"Employee ID {id} is not found")

    try:
        db.delete(employee)
        db.commit()

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