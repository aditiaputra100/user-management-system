from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated
from sqlalchemy.orm import Session
from app.policy.dependencies import require_permission
from app.database import get_session
from .schemas import CreateDepartmentSchema, DepartmentSchema, DepartmentsSchema, UpdateDepartmentSchema, JobSchema, CreateJobSchema
from .service import create, get_all, get_by_id, update, delete, create_job

router = APIRouter(prefix="/department", tags=["Department"])

@router.post("/", dependencies=[Depends(require_permission("department", "create"))], status_code=status.HTTP_201_CREATED)
def create_department(department: CreateDepartmentSchema, db: Annotated[Session, Depends(get_session)]):
    try:
        create(
            name=department.name,
            description=department.description,
            is_active=department.is_active,
            db=db
        )
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(ve))
    except RuntimeError as re:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(re))


    return {
        "msg": f"Success created department {department.name}"
    }

@router.get("/")
def get_all_departments(db: Annotated[Session, Depends(get_session)]) -> DepartmentsSchema:

    departments = get_all(db)

    return DepartmentsSchema(
        data=[DepartmentSchema(
            name=dp.name,
            description=dp.description,
            is_active=dp.is_active,
            id=dp.id,
            jobs=[JobSchema(
                id=job.id,
                name=job.name,
                description=job.description,
                is_active=job.is_active
            ) for job in dp.job]
        ) for dp in departments],
        count=len(departments)
    )

@router.get("/{id}", response_model=DepartmentSchema)
def get_department(id: int, db: Annotated[Session, Depends(get_session)]) -> DepartmentSchema:
    department = get_by_id(id, db)

    if not department:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Department not found")
    
    return DepartmentSchema(
        name=department.name,
        description=department.description,
        is_active=department.is_active,
        id=department.id
    )

@router.put("/{id}", dependencies=[Depends(require_permission("department", "update"))])
def update_department(id: int, department: UpdateDepartmentSchema, db: Annotated[Session, Depends(get_session)]):
    try:
        update(
            department_id=id,
            name=department.name,
            description=department.description,
            is_active=department.is_active,
            db=db
        )
    except NameError as ne:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ne))
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(ve))
    except RuntimeError as re:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(re))

    return {
        "msg": f"Success updated department with ID {id}"
    }

@router.delete("/{id}", dependencies=[Depends(require_permission("department", "delete"))])
def delete_department(id: int, db: Annotated[Session, Depends(get_session)]):
    try:
        delete(
            department_id=id,
            db=db
        )
    except NameError as ne:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ne))
    except RuntimeError as re:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(re))

    return {
        "msg": f"Success deleted department with ID {id}"
    }

@router.post("/{id}/job", status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permission("job", "create"))])
def create_job_for_department(id: int, job: CreateJobSchema, db: Annotated[Session, Depends(get_session)]):
    try:
        create_job(
            department_id=id,
            name=job.name,
            description=job.description,
            is_active=job.is_active,
            db=db
        )
    except NameError as ne:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ne))
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(ve))
    except RuntimeError as re:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(re))
    
    return {
        "msg": f"Success created job {job.name} for department ID {id}"
    }