from app.department.service import create, get_all, get_by_id, update, delete
from app.department.models import Department
from app.database import Base
from tests.conftest import engine
import pytest

def test_create(db):
    name: str = "New Department"
    description: str = "New Description"

    create(name, description, db)

def test_create_duplicate(db):
    name: str = "New Department"
    description: str = "New Description"

    with pytest.raises(ValueError, match=f"Duplicate entry department {name}"):
        create(name, description, db)

def test_get_all(db):
    create("New department created", "New department description", db=db)
    
    departments = get_all(db)

    department_names = [department.name for department in departments]

    assert len(departments) > 0
    assert "New department created" in department_names
    
def test_get_by_id(db):
    create_department = Department(id=55,
                                   name="New Department 55", 
                                   description="New Description")

    db.add(create_department)
    db.commit()
    db.refresh(create_department)

    department = get_by_id(55, db)

    assert department.id == 55
    assert department.name == "New Department 55"
    
    not_found_department = get_by_id(99, db)

    assert not_found_department == None

def test_update(db):
    update(department_id=55,
           name="Updated Department",
           description=None,
           is_active=None,
           db=db)
    
    department = get_by_id(55, db)

    assert department.id == 55
    assert department.name == "Updated Department"

    not_found_id = 3
    with pytest.raises(NameError, match=f"Department with ID {3} is not found"):
        update(department_id=not_found_id,
               name="Test Department",
               description=None,
               is_active=None,
               db=db)

    updated_name = "Updated Department"
    with pytest.raises(ValueError, match=f"Duplicate entry department {updated_name}"):
        update(department_id=55,
               name=updated_name,
               description=None,
               is_active=None,
               db=db)

def test_delete(db):
    delete(55, db)

    with pytest.raises(NameError, match="Department with ID 55 is not found"):
        delete(55, db)

def setup_module():
    # Create database
    Base.metadata.create_all(bind=engine)

def teardown_module():
    # Drop database
    Base.metadata.drop_all(bind=engine)