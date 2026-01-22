from app.database import Base
from sqlalchemy import ForeignKey, String, Uuid
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy.sql import func
from datetime import datetime
from .utils import get_password_hash
from typing import TYPE_CHECKING
import uuid
# import re

if TYPE_CHECKING:
    from app.employee.models import Employee


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

    def reset_password(self, new_password: str):
        # password_pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"

        # if not re.match(password_pattern, new_password):
        #     raise ValueError("Password must be at least 8 characters long, contain at least one uppercase letter, one lowercase letter, one number, and one special character.")
    

        if len(new_password) < 8:
            raise ValueError("Password must be at least 8 characters long.")
    
        new_password_hash = get_password_hash(new_password)

        self.password_hash = new_password_hash