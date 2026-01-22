from app.database import Base
from sqlalchemy import ForeignKey, Enum, Uuid
from sqlalchemy.sql import func
from sqlalchemy.orm import mapped_column, Mapped, relationship
from enum import StrEnum
from datetime import datetime
from typing import TYPE_CHECKING
import uuid

if TYPE_CHECKING:
    from app.employee.models import Employee


class StatusType(StrEnum):
    PRESENT = "present"
    ABSENT = "absent"
    ON_LEAVE = "on_leave"


class Presence(Base):
    __tablename__ = "presences"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    employee_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("employee.id"), nullable=False)
    clock_in: Mapped[datetime | None] = mapped_column(nullable=True)
    clock_out: Mapped[datetime | None] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)
    status: Mapped[StatusType] = mapped_column(Enum(StatusType), nullable=False)

    employee: Mapped["Employee"] = relationship(back_populates="presences")