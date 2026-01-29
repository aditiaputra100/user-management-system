from fastapi.testclient import TestClient
from app.database import get_session, Base
from app.policy.models import Role, Permission, role_permissions
from app.auth.models import User
from app.auth.utils import get_password_hash
from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import sessionmaker
import pytest

engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_user_with_role(username: str = "test_user", password: str = "password", role_id: int | None = None) -> User:
    """Helper to create a user with an optional role."""
    password_hashed = get_password_hash(password)
    
    new_user = User(
        username=username,
        password_hash=password_hashed,
        status="active"
    )
    
    if role_id:
        new_user.role_id = role_id
    
    with TestingSessionLocal() as db:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    
    return new_user


def create_role(role_name: str = "Test Role", 
                                 description: str = "Test Role Description") -> Role:
    """Helper to create a role."""
    new_role = Role(
        name=role_name,
        description=description
    )
    
    with TestingSessionLocal() as db:
        db.add(new_role)
        db.commit()
        db.refresh(new_role)
    
    return new_role


def create_permission(name: str = "Test Permission", resource: str = "roles", action: str = "read", description: str = "Test") -> Permission:
    """Helper to create a permission."""
    new_permission = Permission(
        name=name,
        resource=resource,
        action=action,
        description=description
    )
    
    with TestingSessionLocal() as db:
        db.add(new_permission)
        db.commit()
        db.refresh(new_permission)
    
    return new_permission

def assign_role(role_id: int, permission_id: int):
    with TestingSessionLocal() as db:
        db.execute(role_permissions.insert(), {
            "role_id": role_id,
            "permission_id": permission_id
        })
        db.commit()

def get_access_token(client: TestClient, username: str, password: str) -> str:
    """Helper to get access token."""
    resp = client.post("/login", data={"username": username, "password": password})
    assert resp.status_code == 200
    data = resp.json()
    return data["access_token"]


@pytest.fixture(scope="function")
def client_with_db():
    """Create test client with clean database for each test."""
    # Create the database tables
    Base.metadata.create_all(bind=engine)
    
    # Import app here to avoid circular imports
    from app.main import app
    from app.database import get_session as original_get_session
    
    def override_get_session():
        with TestingSessionLocal() as session:
            yield session
    
    app.dependency_overrides[original_get_session] = override_get_session
    
    yield TestClient(app)
    
    # Drop the database tables
    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides.clear()


class TestRoleEndpoints:
    """Test suite for role endpoints."""

    def __init__(self):
        self.admin_role = create_role("System Administrator", "Admin Role")
        self.admin = create_user_with_role("admin", "admin123", self.admin_role.id)
        action_list = ["create", "read", "update", "delete", "list"]

        for action in action_list:
            permission = create_permission(
                f"Admin {action}",
                "roles",
                action,
            )
        
            assign_role(self.admin_role.id, permission.id)
        
    
    def test_create_role(self, client_with_db):
        """Test creating a new role."""
        token = get_access_token(client_with_db, "admin", "admin123")
        headers = {"Authorization": f"Bearer {token}"}
        
        new_role_data = {
            "name": "Editor",
            "description": "Editor role for content management"
        }
        
        response = client_with_db.post("/roles/", json=new_role_data, headers=headers)
        assert response.status_code == 201
        assert "Successfuly created role Editor" in response.json()["msg"]
    
    def test_get_all_roles(self, client_with_db):
        """Test retrieving all roles."""
        create_role("Editor", "Editor Role") 
        
        token = get_access_token(client_with_db, "admin", "admin123")
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client_with_db.get("/roles/", headers=headers)
        assert response.status_code == 200
        roles = response.json()
        assert len(roles) >= 2
        role_names = [role["name"] for role in roles]
        assert "System Administrator" in role_names
        assert "Editor" in role_names
    
    def test_get_role_by_id(self, client_with_db):
        """Test retrieving a specific role by ID."""
        admin_role = create_role_with_permissions("System Administrator", "Admin")
        test_role = create_role_with_permissions("Viewer", "Viewer Role")
        admin_user = create_user_with_role("admin@test.com", "password", "System Administrator")
        
        token = get_access_token(client_with_db, "admin@test.com", "password")
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client_with_db.get(f"/roles/{test_role.id}", headers=headers)
        assert response.status_code == 200
        role = response.json()
        assert role["name"] == "Viewer"
        assert role["description"] == "Viewer Role"
    
    def test_get_role_not_found(self, client_with_db):
        """Test retrieving a non-existent role."""
        admin_role = create_role_with_permissions("System Administrator", "Admin")
        admin_user = create_user_with_role("admin@test.com", "password", "System Administrator")
        
        token = get_access_token(client_with_db, "admin@test.com", "password")
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client_with_db.get("/roles/9999", headers=headers)
        assert response.status_code == 404
        assert response.json()["detail"] == "Role is not found"
    
    def test_update_role(self, client_with_db):
        """Test updating an existing role."""
        admin_role = create_role_with_permissions("System Administrator", "Admin")
        test_role = create_role_with_permissions("Contributor", "Contributor Role")
        admin_user = create_user_with_role("admin@test.com", "password", "System Administrator")
        
        token = get_access_token(client_with_db, "admin@test.com", "password")
        headers = {"Authorization": f"Bearer {token}"}
        
        updated_data = {
            "name": "Contributor",
            "description": "Updated Contributor Role"
        }
        
        response = client_with_db.put(f"/roles/{test_role.id}", json=updated_data, headers=headers)
        assert response.status_code == 200
        assert "Success updated role" in response.json()["msg"]
    
    def test_delete_role(self, client_with_db):
        """Test deleting a role."""
        admin_role = create_role_with_permissions("System Administrator", "Admin")
        test_role = create_role_with_permissions("Temporary", "Temporary Role")
        admin_user = create_user_with_role("admin@test.com", "password", "System Administrator")
        
        token = get_access_token(client_with_db, "admin@test.com", "password")
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client_with_db.delete(f"/roles/{test_role.id}", headers=headers)
        assert response.status_code == 200
        assert "Success deleted role" in response.json()["msg"]


class TestPermissionEndpoints:
    """Test suite for permission endpoints."""
    
    def test_create_permission(self, client_with_db):
        """Test creating a new permission."""
        admin_role = create_role_with_permissions("System Administrator", "Admin")
        admin_user = create_user_with_role("admin@test.com", "password", "System Administrator")
        
        token = get_access_token(client_with_db, "admin@test.com", "password")
        headers = {"Authorization": f"Bearer {token}"}
        
        new_permission_data = {
            "name": "Create Reports",
            "resource": "reports",
            "action": "create",
            "description": "Permission to create reports"
        }
        
        response = client_with_db.post("/permission/", json=new_permission_data, headers=headers)
        assert response.status_code == 201
        assert "Successfuly created permission" in response.json()["msg"]
    
    def test_get_all_permissions(self, client_with_db):
        """Test retrieving all permissions."""
        admin_role = create_role_with_permissions("System Administrator", "Admin")
        perm1 = create_permission("Read Users", "users", "read")
        perm2 = create_permission("Create Users", "users", "create")
        admin_user = create_user_with_role("admin@test.com", "password", "System Administrator")
        
        token = get_access_token(client_with_db, "admin@test.com", "password")
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client_with_db.get("/permission/", headers=headers)
        assert response.status_code == 200
        permissions = response.json()
        assert len(permissions) >= 2
        permission_names = [perm["name"] for perm in permissions]
        assert "Read Users" in permission_names
        assert "Create Users" in permission_names
    
    def test_get_permission_by_id(self, client_with_db):
        """Test retrieving a specific permission by ID."""
        admin_role = create_role_with_permissions("System Administrator", "Admin")
        perm = create_permission("Delete Users", "users", "delete", "Permission to delete users")
        admin_user = create_user_with_role("admin@test.com", "password", "System Administrator")
        
        token = get_access_token(client_with_db, "admin@test.com", "password")
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client_with_db.get(f"/permission/{perm.id}", headers=headers)
        assert response.status_code == 200
        permission = response.json()
        assert permission["name"] == "Delete Users"
        assert permission["resource"] == "users"
        assert permission["action"] == "delete"
    
    def test_get_permission_not_found(self, client_with_db):
        """Test retrieving a non-existent permission."""
        admin_role = create_role_with_permissions("System Administrator", "Admin")
        admin_user = create_user_with_role("admin@test.com", "password", "System Administrator")
        
        token = get_access_token(client_with_db, "admin@test.com", "password")
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client_with_db.get("/permission/9999", headers=headers)
        assert response.status_code == 404
        assert response.json()["detail"] == "Permission is not found"
    
    def test_update_permission(self, client_with_db):
        """Test updating an existing permission."""
        admin_role = create_role_with_permissions("System Administrator", "Admin")
        perm = create_permission("Update Users", "users", "update")
        admin_user = create_user_with_role("admin@test.com", "password", "System Administrator")
        
        token = get_access_token(client_with_db, "admin@test.com", "password")
        headers = {"Authorization": f"Bearer {token}"}
        
        updated_data = {
            "name": "Update Users",
            "resource": "users",
            "action": "update",
            "description": "Updated permission to update users"
        }
        
        response = client_with_db.put(f"/permission/{perm.id}", json=updated_data, headers=headers)
        assert response.status_code == 200
        assert "Success updated permission" in response.json()["msg"]
    
    def test_delete_permission(self, client_with_db):
        """Test deleting a permission."""
        admin_role = create_role_with_permissions("System Administrator", "Admin")
        perm = create_permission("Temporary Permission", "temp", "read")
        admin_user = create_user_with_role("admin@test.com", "password", "System Administrator")
        
        token = get_access_token(client_with_db, "admin@test.com", "password")
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client_with_db.delete(f"/permission/{perm.id}", headers=headers)
        assert response.status_code == 200
        assert "Success deleted permission" in response.json()["msg"]


class TestPermissionDenied:
    """Test suite for permission denial scenarios."""
    
    def test_unauthorized_user_cannot_create_role(self, client_with_db):
        """Test that unauthorized user cannot create roles."""
        regular_role = create_role_with_permissions("User", "Regular User")
        user = create_user_with_role("user@test.com", "password", "User")
        
        token = get_access_token(client_with_db, "user@test.com", "password")
        headers = {"Authorization": f"Bearer {token}"}
        
        new_role_data = {
            "name": "Hacker",
            "description": "Should not be created"
        }
        
        response = client_with_db.post("/roles/", json=new_role_data, headers=headers)
        assert response.status_code == 403
        assert "Permission denied" in response.json()["detail"]
    
    def test_unauthorized_user_cannot_delete_role(self, client_with_db):
        """Test that unauthorized user cannot delete roles."""
        regular_role = create_role_with_permissions("User", "Regular User")
        test_role = create_role_with_permissions("ToDelete", "Test Role")
        user = create_user_with_role("user@test.com", "password", "User")
        
        token = get_access_token(client_with_db, "user@test.com", "password")
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client_with_db.delete(f"/roles/{test_role.id}", headers=headers)
        assert response.status_code == 403
        assert "Permission denied" in response.json()["detail"]
