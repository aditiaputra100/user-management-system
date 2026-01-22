from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from .models import Department, Job


def create(name: str, description: str | None, db: Session, is_active: bool = True) -> None:
    """Create a new department in the database."""
    new_department = Department(
        name=name,
        description=description,
        is_active=is_active
    )

    try:
        db.add(new_department)
        db.commit()

    except IntegrityError:
        db.rollback()
        raise ValueError(f"Duplicate entry {name}")

    except Exception as err:
        db.rollback()
        raise RuntimeError(str(err))
    
def get_all(db: Session) -> list[Department]:
    """Retrieve all departments from the database."""
    return db.query(Department).all()

def get_by_id(department_id: int, db: Session) -> Department | None:
    """Retrieve a department by its ID."""
    return db.get(Department, department_id)

def update(department_id: int, name: str | None, description: str | None, is_active: bool | None, db: Session) -> None:
    """Update an existing department in the database."""
    department = db.get(Department, department_id)

    if not department:
        raise NameError(f"Department with ID {department_id} not found")

    if name is not None:
        department.name = name
    if description is not None:
        department.description = description
    if is_active is not None:
        department.is_active = is_active

    try:
        db.commit()

    except IntegrityError:
        db.rollback()
        raise ValueError(f"Duplicate entry {name}")

    except Exception as err:
        db.rollback()
        raise RuntimeError(str(err))

def delete(department_id: int, db: Session) -> None:
    """Delete a department from the database."""
    department = db.get(Department, department_id)

    if not department:
        raise NameError(f"Department with ID {department_id} not found")

    try:
        db.delete(department)
        db.commit()

    except Exception as err:
        db.rollback()
        raise RuntimeError(str(err))

def create_job(department_id: int, name: str, description: str | None, db: Session, is_active: bool = True) -> None:
    """Create a new job for a specific department."""
    department = db.get(Department, department_id)

    if not department:
        raise NameError(f"Department with ID {department_id} not found")

    new_job = Job(
        name=name,
        description=description,
        is_active=is_active,
        department_id=department.id
    )

    try:
        db.add(new_job)
        db.commit()

    except IntegrityError:
        db.rollback()
        raise ValueError(f"Duplicate entry {name}")

    except Exception as err:
        db.rollback()
        raise RuntimeError(str(err))