from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Annotated
from app.database import get_session
from app.policy.dependencies import require_permission
from .service import get_all, get_by_id, create, create_status, get_all_status, update_status, delete_status
from .schemas import EmployeesSchema, EmployeeSchema, CreateEmployeeSchema, CreateUserSchema, CreateEmployeeStatusSchema, EmployeeStatusSchema, EmployeeStatusesSchema
import uuid

router = APIRouter(prefix="/employee", tags=["Employee"], dependencies=[Depends(require_permission("employee_status", "list"))])

@router.get("/status")
def get_employee_status(db: Session = Depends(get_session)) -> EmployeeStatusesSchema:
    
    statuses = get_all_status(db=db)

    return EmployeeStatusesSchema(
        data=[EmployeeStatusSchema(
            name=st.name,
            description=st.description,
            is_active=st.is_active,
            id=st.id
        ) for st in statuses],
        count=len(statuses)
    )

@router.post("/status", status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permission("employee_status", "create"))])
def create_employee_status(employee_status: CreateEmployeeStatusSchema, db: Session = Depends(get_session)):

    try:
        create_status(
            name=employee_status.name,
            description=employee_status.description,
            is_active=employee_status.is_active,
            db=db
        )
    except ValueError as err:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(err)
        )
    except RuntimeError as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(err)
        )

    return {
        "msg": f"Success created status {employee_status.name}"
    }

@router.put("/status/{id}", dependencies=[Depends(require_permission("employee_status", "update"))])
def update_employee_status(id: int, employee_status: CreateEmployeeStatusSchema, db: Annotated[Session, Depends(get_session)]):
    try:
        update_status(
            id=id,
            name=employee_status.name,
            description=employee_status.description,
            is_active=employee_status.is_active,
            db=db
        )

    except NameError as err:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(err))
    
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(err))
    
    except RuntimeError as err:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(err))

    return {
        "mgs": "Employee status updated successfully"
    }

@router.delete("/status/{id}", dependencies=[Depends(require_permission("employee_status", "delete"))])
def delete_employee_status(id: int, db: Annotated[Session, Depends(get_session)]):
    try:
        delete_status(id, db)
    
    except NameError as err:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(err))

    except RuntimeError as err:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(err))
    
    return {
        "mgs": "Employee status deleted successfully"
    }

@router.get("/{id}", dependencies=[Depends(require_permission("employee", "read"))])
def get_employee(id: uuid.UUID, db: Annotated[Session, Depends(get_session)]) -> EmployeeSchema:
    employee = get_by_id(id, db)

    if employee is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )

    return EmployeeSchema(
        id=employee.id,
        full_name=employee.full_name,
        gender=employee.gender,
        birthday=employee.birthday,
        email_address=employee.email_address,
        phone_number=employee.phone_number,
        address=employee.address,
        department=employee.department.name,
        job=employee.job.name,
        salary=employee.salary,
        employee_status=employee.employee_status.name,
        hire_date=employee.hire_date,
        created_at=employee.created_at,
        updated_at=employee.updated_at
    )

@router.get("", dependencies=[Depends(require_permission("employee", "list"))])
def get_all_employees(db: Annotated[Session, Depends(get_session)]) -> EmployeesSchema:
    employees = get_all(db)

    return EmployeesSchema(
        data=[EmployeeSchema(
            id=emp.id,
            full_name=emp.full_name,
            gender=emp.gender,
            birthday=emp.birthday,
            email_address=emp.email_address,
            phone_number=emp.phone_number,
            address=emp.address,
            department=emp.department.name,
            job=emp.job.name,
            salary=emp.salary,
            employee_status=emp.employee_status.name,
            hire_date=emp.hire_date,
            created_at=emp.created_at,
            updated_at=emp.updated_at
        ) for emp in employees],
        count=len(employees)
    )

@router.post("", status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permission("employee", "create"))])
def create_employee(employee: CreateEmployeeSchema, user: CreateUserSchema, db: Annotated[Session, Depends(get_session)]):
    try:
        create(employee, user, db)
    except ValueError as err:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(err)
        )
    except RuntimeError as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(err)
        )

    return {"msg": "Employee and user created successfully"}