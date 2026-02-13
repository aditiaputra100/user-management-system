from datetime import datetime
from pydantic import BaseModel, EmailStr, field_validator, ConfigDict
from pydantic_extra_types.phone_numbers import PhoneNumber, PhoneNumberValidator
from typing import Annotated, Union
import uuid

E164NumberType = Annotated[
    Union[str, PhoneNumber], PhoneNumberValidator(number_format="E164")
]


class EmployeeSchema(BaseModel):
    id: uuid.UUID
    full_name: str
    gender: bool
    birthday: datetime
    email_address: str
    phone_number: str
    address: str
    department: str
    job: str
    salary: int
    employee_status: str
    hire_date: datetime
    created_at: datetime
    updated_at: datetime


class EmployeesSchema(BaseModel):
    data: list[EmployeeSchema]
    count: int
    page: int


class CreateEmployeeSchema(BaseModel):
    full_name: str
    gender: bool
    birthday: datetime
    hire_date: datetime
    email_address: EmailStr
    phone_number: E164NumberType
    address: str
    department: int
    job: int
    salary: int
    employee_status: int

    @field_validator("salary")
    @classmethod
    def validate_salary(cls, v):
        if v < 0:
            raise ValueError("Salary must be a non-negative integer")
        return v


class CreateUserSchema(BaseModel):
    username: str
    password: str
    status: str
    role_id: int | None = None

    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        return v

class UpdateUserSchema(BaseModel):
    status: str | None = None
    role_id: int | None = None

class CreateEmployeeStatusSchema(BaseModel):
    name: str
    description: str = ""
    is_active: bool = True


class EmployeeStatusSchema(CreateEmployeeStatusSchema):
    id: int


class EmployeeStatusesSchema(BaseModel):
    data: list[EmployeeStatusSchema]
    count: int