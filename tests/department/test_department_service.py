from app.department.service import create, get_all, get_by_id, update, delete
from app.department.models import Department
import pytest

def test_create(db):
    name: str = "New Department"
    description: str = "New Description"

    create(name, description, db)

def test_create_duplicate(db):
    name: str = "New Department"
    description: str = "New Description"

    create(name, description, db)

    with pytest.raises(ValueError, match=f"Duplicate entry department {name}"):
        create(name, description, db)

def test_get_all(db):
    departments = get_all(db)

    assert departments == []

    new_departments = [
        {
            "name": "Department A",
            "description": "Description A",
        },
        {
            "name": "Department B",
            "description": "Description B",
        },
        {
            "name": "Department C",
            "description": "Description C",
        },
    ]

    add_departments_to_db: list[Department] = []

    for new_department in new_departments:
        add_departments_to_db.append(
            Department(
                name=new_department["name"],
                description=new_department["description"]
            )
        )
    
    db.add_all(add_departments_to_db)
    db.commit()
    
    for department in add_departments_to_db:
        db.refresh(department)

    departments = get_all(db)

    assert len(departments) == 3
    assert departments[0].id == add_departments_to_db[0].id

def test_get_by_id(db):
    create_department = Department(name="New Department", 
                                   description="New Description")

    db.add(create_department)
    db.commit()
    db.refresh(create_department)

    department = get_by_id(create_department.id, db)

    assert department.id == create_department.id
    assert department.name == create_department.name
    
    not_found_department = get_by_id(2, db)

    assert not_found_department == None

def test_update(db):
    create_department = Department(name="New Department", 
                                   description="New Description")

    db.add(create_department)
    db.commit()
    db.refresh(create_department)

    update(department_id=create_department.id,
           name="Updated Department",
           description=None,
           is_active=None,
           db=db)
    
    department = get_by_id(create_department.id, db)

    assert department.name == "Updated Department"
    assert department.description == "New Description"

    not_found_id = 3
    with pytest.raises(NameError, match=f"Department with ID {3} is not found"):
        update(department_id=not_found_id,
               name="Test Department",
               description=None,
               is_active=None,
               db=db)

    updated_name = "Updated Department"
    with pytest.raises(ValueError, match=f"Duplicate entry department {updated_name}"):
        update(department_id=create_department.id,
               name=updated_name,
               description=None,
               is_active=None,
               db=db)

def test_delete(db):
    create_department = Department(name="New Department", 
                                   description="New Description")

    db.add(create_department)
    db.commit()
    db.refresh(create_department)

    delete(create_department.id, db)

    with pytest.raises(NameError, match=f"Department with ID {create_department.id} is not found"):
        delete(create_department.id, db)