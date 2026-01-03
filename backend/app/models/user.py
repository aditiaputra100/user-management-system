from app.dependencies.database import Base
from sqlalchemy import ForeignKey, String, Uuid
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy.sql import func
from datetime import datetime
import uuid


class Department(Base):
    __tablename__ = "department"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    employee: Mapped[list["Employee"]] = relationship(back_populates="department")
    job: Mapped[list["Job"]] = relationship(back_populates="department")


class Job(Base):
    __tablename__ = "job"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    department_id: Mapped[int] = mapped_column(ForeignKey("department.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    department: Mapped["Department"] = relationship(back_populates="job")
    employee: Mapped[list["Employee"]] = relationship(back_populates="job", cascade="")


class EmployeeStatus(Base):
    __tablename__ = "employee_status"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False, unique=True)
    description: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    employee: Mapped[list["Employee"]] = relationship(back_populates="employee_status")


class Employee(Base):
    __tablename__ = "employee"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    full_name: Mapped[str] = mapped_column(String(150), nullable=False)
    gender: Mapped[bool] = mapped_column(nullable=False) # 0 for woman, 1 for man
    birthday: Mapped[datetime] = mapped_column(nullable=False)
    phone_number: Mapped[str] = mapped_column(String(20), nullable=False)
    address: Mapped[str] = mapped_column(String(100))
    departmen_id: Mapped[int] = mapped_column(ForeignKey("department.id"), nullable=False)
    job_id: Mapped[int] = mapped_column(ForeignKey("job.id"), nullable=False)
    salary: Mapped[int] = mapped_column(default=0)
    employee_status_id: Mapped[int] = mapped_column(ForeignKey("employee_status.id"))
    hire_date: Mapped[datetime] = mapped_column(server_default=func.now())
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now())

    department: Mapped["Department"] = relationship(back_populates="employee")
    job: Mapped["Job"] = relationship(back_populates="employee")
    employee_status: Mapped["EmployeeStatus"] = relationship(back_populates="employee")
    user: Mapped["User"] = relationship(back_populates="employee")


class User(Base):
    __tablename__ = "user"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    employee_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("employee.id"), nullable=True)
    username: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(255), default="active")
    last_active: Mapped[datetime] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now())

    employee: Mapped["Employee"] = relationship(back_populates="user", single_parent=True)