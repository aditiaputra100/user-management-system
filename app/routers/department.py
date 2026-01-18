from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Optional
from app.routers.auth import get_current_user
from app.models.user import Department, Job
from app.dependencies.database import get_session
from app.schemas import UserResponse, DepartmentRequest, DepartmentResponse, DepartmentSchema, DepartmentListResponse, JobRequestSchema, JobResponseSchema, JobListResponseSchema

router = APIRouter(prefix="/department", tags=["Department"])

@router.post("/")
def create_department(department: DepartmentRequest, current_user: Annotated[UserResponse, Depends(get_current_user)], db: Session = Depends(get_session)):
    name: str = department.name
    description: Optional[str] = department.description

    new_department = Department(
        name=name,
        description=description
    )

    try:
        db.add(new_department)
        db.commit()
        db.flush(new_department)
    
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Duplicate entry {name}")
    
    except Exception as err:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(err))

    return {
        "msg": f"Success created department {name}"
    }


@router.get("/", response_model=DepartmentListResponse)
def get_all_departments(db: Session = Depends(get_session)):
    stmt = select(Department)
    results: list[Department] = db.scalars(stmt).all()
    
    departments: list[DepartmentResponse] = []

    for department in results:
        departments.append(DepartmentResponse(
            name=department.name,
            description=department.description,
            is_active=department.is_active
        ))

    return DepartmentListResponse(
        data=departments,
        count=len(results)
    )

@router.get("/{id}", response_model=DepartmentResponse)
def get_department(id: int, db: Session = Depends(get_session)):
    result: Department = db.get(Department, id)
    
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Department with ID {id} is not found")
    
    return DepartmentResponse(
        name=result.name,
        description=result.description,
        is_active=result.is_active
    )

@router.put("/{id}")
def update_department(id: int, department: DepartmentRequest, current_user: Annotated[UserResponse, Depends(get_current_user)], db: Session = Depends(get_session)):
    result: Department = db.get(Department, id)
    
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Department with ID {id} is not found")
    
    result.name = department.name
    result.description = department.description

    db.commit()
    db.flush(result)

    return {
        "msg": f"Update department with ID {id} was successfully"
    }

@router.patch("/{id}")
def update_department_status(id: int, activated: bool, current_user: Annotated[UserResponse, Depends(get_current_user)], db: Session = Depends(get_session)):
    if current_user.status != "active":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden to update status department")
    
    department: Department | None = db.get(Department, id)

    if not department:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Department with ID {id} is not found")
    
    department.is_active = activated

    db.commit()
    db.flush(department)

    return {
        "msg":  f"Update department status with ID {id} was successfully"
    }


@router.delete("/{id}")
def delete_department(id: int, current_user: Annotated[UserResponse, Depends(get_current_user)], db: Session = Depends(get_session)):
    result: Department = db.get(Department, id)
    result.is_active = False
    
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Department with ID {id} is not found")
    
    db.commit()
    db.flush(result)
    
    return {
        "msg": f"Success delete department with ID {id}"
    }

@router.post("/{id}/job", status_code=status.HTTP_201_CREATED)
def create_department_job(id: int, request: JobRequestSchema, current_user: Annotated[UserResponse, Depends(get_current_user)], db: Session = Depends(get_session)):
    if current_user.status != "active":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden to create job")

    department: Department | None = db.get(Department, id)

    if not department:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=f"Department with ID {id} is not found")

    if not department.is_active:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=f"Department {department.name} is no longer active")

    new_job = Job(**request.model_dump(), department_id=id)
    
    try:
        db.add(new_job)
        db.commit()
        db.flush(new_job)
    except IntegrityError as err:
        
        if "foreign key" in str(err).lower():
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=f"Department with ID {id} is not found")

        print(err)
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="Unknown database integrity error")
    except Exception as err:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(err))

    return {
        "msg": f"Success created job {new_job.name} in {new_job.department.name}"
    }

@router.get("/{id}/job", response_model=JobListResponseSchema)
def get_job(id: int, current_user: Annotated[UserResponse, Depends(get_current_user)], db: Session = Depends(get_session)):
    if current_user.status != "active":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden to get job")

    result: Optional[Department] = db.get(Department, id)
    
    if not result:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="Department is not found")
    
    stmt = select(Job).where(Job.department_id == id)
    jobs: list[Job] = db.scalars(stmt).all()

    response: list[JobResponseSchema] = []
    for job in jobs:
        response.append(
            JobResponseSchema(
                name=job.name,
                description=job.description,
                department=job.department.name
            )
        )
    
    return JobListResponseSchema(
        data=response,
        count=len(response)
    )

@router.delete("/{department_id}/job/{job_id}")
def delete_job(department_id: int, job_id: int, current_user: Annotated[UserResponse, Depends(get_current_user)], db: Session = Depends(get_session)):
    if current_user.status != "active":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden to delete job")
    
    result: Job = db.get(Job, job_id)
    result.is_active = False

    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Job with ID {job_id} was not found")

    if result.department_id != department_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Can't delete job {job_id} using department {department_id}")

    try:
        db.commit()
        db.flush(result)
    except Exception as err:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(err))

    return {
        "msg": f"Success delete job {result.name} in {result.department.name}"
    }