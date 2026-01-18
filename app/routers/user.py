from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Annotated
from app.dependencies.database import get_session
from app.routers.auth import get_current_user
from app.schemas import UserResponse, EmployeeSchema, EmployeeListSchema, EmployeeStatusRequest, EmployeeStatusResponse, EmployeeStatusListResponse
from app.models.user import Employee, EmployeeStatus
import logging

router = APIRouter(prefix="/user", tags=["Employee"])
logger = logging.getLogger('uvicorn.error')

@router.get("", response_model=EmployeeListSchema)
def get_employee(current_user: Annotated[UserResponse, Depends(get_current_user)], db: Session = Depends(get_session)):
    if current_user.status != "active":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden to get user")
    
    stmt = select(Employee)
    results: list[Employee] = db.scalars(stmt).all()

    user: list[EmployeeSchema] = []

    for result in results:
        user.append(EmployeeSchema(
            employee_id=result.id,
            full_name=result.full_name,
            gender=result.gender,
            birthday=result.birthday,
            hire_date=result.hire_date,
            phone_number=result.phone_number,
            address=result.address,
            job=result.job
        ))

    return EmployeeListSchema(
        data=user,
        count=len(user)
    )

@router.get("/status", response_model=EmployeeStatusListResponse)
def get_employee_status(current_user: Annotated[UserResponse, Depends(get_current_user)], db: Session = Depends(get_session)):
    if current_user.status != "active":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden to get user status")
    
    stmt = select(EmployeeStatus)
    results: list[EmployeeStatus] = db.scalars(stmt).all()
    
    status_list: list[EmployeeStatusResponse] = []

    for result in results:
        status_list.append(EmployeeStatusResponse(
            name=result.name,
            description=result.description,
            id=result.id
        ))
    
    return EmployeeStatusListResponse(
        data=status_list,
        count=len(status_list)
    )

@router.post("/status", status_code=status.HTTP_201_CREATED)
def create_employee_status(request: EmployeeStatusRequest, current_user: Annotated[UserResponse, Depends(get_current_user)], db: Session = Depends(get_session)):
    if current_user.status != "active":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden to get user status")

    employee_status = EmployeeStatus(
        name=request.name,
        description=request.description
    )

    try:
        db.add(employee_status)
        db.commit()
        db.flush(employee_status)
    
    except IntegrityError as err:
        logging.error(f"POST {router.prefix}/status {err}")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Duplicate entry {employee_status.name}")

    except Exception as err:
        logging.error(f"POST {router.prefix}/status {err}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(err))

    return {
        "msg": f"Success created status {employee_status.name}"
    }
