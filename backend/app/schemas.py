from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class DepartmentSchema(BaseModel):
    name: str
    description: Optional[str] = ""


class _JobSchema(BaseModel):
    name: str
    description: str = ""
    is_active: bool | None = None


class JobRequestSchema(_JobSchema):
    pass


class JobResponseSchema(_JobSchema):
    department: str


class JobListResponseSchema(BaseModel):
    data: list[JobResponseSchema]
    count: int


class EmployeeSchema(BaseModel):
    employee_id: str
    full_name: str
    gender: bool
    birthday: datetime
    hire_date: datetime
    phone_number: str
    address: str
    job: JobResponseSchema


class EmployeeListSchema(BaseModel):
    data: list[EmployeeSchema]
    count: int


class _EmployeeStatusSchema(BaseModel):
    name: str
    description: str = ""


class EmployeeStatusResponse(_EmployeeStatusSchema):
    id: int


class EmployeeStatusListResponse(BaseModel):
    data: list[EmployeeStatusResponse]
    count: int


class EmployeeStatusRequest(_EmployeeStatusSchema):
    pass


class UserResponse(BaseModel):
    username: str
    status: str
    last_active: datetime


class PasswordRequest(BaseModel):
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class DepartmentRequest(DepartmentSchema):
    pass


class DepartmentResponse(DepartmentSchema):
    is_active: bool


class DepartmentListResponse(BaseModel):
    data: list[DepartmentResponse]
    count: int