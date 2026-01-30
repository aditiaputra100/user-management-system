from sqlalchemy import select
from sqlalchemy.orm import Session
from .models import Presence, StatusType
from datetime import datetime, date

def create_presence(status: str, employee_id: str, db: Session) -> None:
    stmt = select(Presence).where(Presence.employee_id == employee_id
                                    and Presence.created_at == date.today())
    already_clock = db.scalars(stmt).one_or_none()
    
    if status == StatusType.PRESENT:

        if not already_clock:
            new_presence = Presence(
                employee_id=employee_id,
                clock_in=datetime.now(),
                status=status
            )

            db.add(new_presence)
            db.commit()

            return
        
        if already_clock.clock_out:
            raise ValueError("Have filled in today's attendance")

        already_clock.clock_out = datetime.now()
        db.commit()

        return
    
    # If already presence today
    if already_clock:
        raise ValueError("Have filled in today's attendance")

    new_presence = Presence(
        employee_id=employee_id,
        status=status
    )

    db.add(new_presence)
    db.commit()