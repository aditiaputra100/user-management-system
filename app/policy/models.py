from app.database import Base
from sqlalchemy.orm import Mapped, mapped_column, Relationship
from sqlalchemy import String, Text, Table, Column, Integer, ForeignKey
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from app.auth.models import User

role_permissions = Table(
    "role_permissions", 
    Base.metadata,
    Column("role_id", Integer, ForeignKey("roles.id", ondelete="CASCADE")),
    Column("permission_id", Integer, ForeignKey("permissions.id", ondelete="CASCADE"))
)


class Role(Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    users: Mapped[list["User"]] = Relationship(back_populates="role")
    permissions: Mapped[list["Permission"]] = Relationship(secondary=role_permissions, back_populates="roles")


class Permission(Base):
    __tablename__ = "permissions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    resource: Mapped[str] = mapped_column(String(100))
    action: Mapped[str] = mapped_column(String(50))
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    roles: Mapped[list["Role"]] = Relationship(secondary=role_permissions, back_populates="permissions")