from pydantic import BaseModel
from typing import Optional


class CreateJobSchema(BaseModel):
    name: str
    description: Optional[str] = None
    is_active: bool = True


class JobSchema(CreateJobSchema):
    id: int


class CreateDepartmentSchema(BaseModel):
    name: str
    description: Optional[str] = ""
    is_active: bool = True


class DepartmentSchema(CreateDepartmentSchema):
    id: int
    jobs: list[JobSchema]


class DepartmentsSchema(BaseModel):
    data: list[DepartmentSchema]
    count: int


class UpdateDepartmentSchema(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None