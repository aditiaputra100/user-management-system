from app.database import Base
from tests.conftest import engine
from tests.utils import get_access_token


class TestRoleEndpoints:
    """Test suite for role endpoints."""
    
    def test_create_role(self, client):
        """Test creating a new role."""
        token = get_access_token(client, "admin", "admin")
        headers = {"Authorization": f"Bearer {token}"}
        
        new_role_data = {
            "name": "Editor",
            "description": "Editor role for content management"
        }
        
        response = client.post("/roles/", json=new_role_data, headers=headers)
        assert response.status_code == 201
        assert "Successfuly created role Editor" in response.json()["msg"]
    
    def test_get_all_roles(self, client):
        """Test retrieving all roles."""
        token = get_access_token(client, "admin", "admin")
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.get("/roles/", headers=headers)
        assert response.status_code == 200
        roles = response.json()

        assert len(roles) > 0
        role_names = [role["name"] for role in roles]
        assert "Editor" in role_names
    
    def test_get_role_by_id(self, client):
        """Test retrieving a specific role by ID."""
        
        token = get_access_token(client, "admin", "admin")
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.get(f"/roles/44", headers=headers)
        assert response.status_code == 200

        role = response.json()

        assert role["name"] == "Testing Role"
        assert role["description"] == "Testing Description"
    
    def test_get_role_not_found(self, client):
        """Test retrieving a non-existent role."""
        token = get_access_token(client, "admin", "admin")
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.get("/roles/9999", headers=headers)

        assert response.status_code == 404
        assert response.json()["detail"] == "Role is not found"
    
    def test_update_role(self, client):
        """Test updating an existing role."""        
        token = get_access_token(client, "admin", "admin")
        headers = {"Authorization": f"Bearer {token}"}
        
        updated_data = {
            "name": "Contributor",
            "description": "Updated Contributor Role"
        }
        
        response = client.put(f"/roles/44", json=updated_data, headers=headers)

        assert response.status_code == 200
        assert "Success updated role" in response.json()["msg"]
    
    def test_delete_role(self, client):
        """Test deleting a role."""
        token = get_access_token(client, "admin", "admin")
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.delete(f"/roles/44", headers=headers)

        assert response.status_code == 200
        assert "Success deleted role" in response.json()["msg"]


class TestPermissionEndpoints:
    """Test suite for permission endpoints."""
    
    def test_create_permission(self, client):
        """Test creating a new permission."""
        token = get_access_token(client, "admin", "admin")
        headers = {"Authorization": f"Bearer {token}"}
        
        new_permission_data = {
            "name": "Create Reports",
            "resource": "reports",
            "action": "create",
            "description": "Permission to create reports"
        }
        
        response = client.post("/permission/", json=new_permission_data, headers=headers)
        assert response.status_code == 201
        assert "Successfuly created permission" in response.json()["msg"]
    
    def test_get_all_permissions(self, client):
        """Test retrieving all permissions."""
        token = get_access_token(client, "admin", "admin")
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.get("/permission/", headers=headers)
        assert response.status_code == 200

        permissions = response.json()

        assert len(permissions) > 0

        permission_names = [perm["name"] for perm in permissions]

        assert "Create Reports" in permission_names
    
    def test_get_permission_by_id(self, client):
        """Test retrieving a specific permission by ID."""        
        token = get_access_token(client, "admin", "admin")
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.get(f"/permission/33", headers=headers)

        assert response.status_code == 200

        permission = response.json()

        assert permission["name"] == "Testing Permission"
        assert permission["resource"] == "testing"
        assert permission["action"] == "read"
    
    def test_get_permission_not_found(self, client):
        """Test retrieving a non-existent permission."""        
        token = get_access_token(client, "admin", "admin")
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.get("/permission/9999", headers=headers)

        assert response.status_code == 404
        assert response.json()["detail"] == "Permission is not found"
    
    def test_update_permission(self, client):
        """Test updating an existing permission."""        
        token = get_access_token(client, "admin", "admin")
        headers = {"Authorization": f"Bearer {token}"}
        
        updated_data = {
            "name": "Update Users",
            "resource": "users",
            "action": "update",
            "description": "Updated permission to update users"
        }
        
        response = client.put(f"/permission/33", json=updated_data, headers=headers)

        assert response.status_code == 200
        assert "Success updated permission" in response.json()["msg"]
    
    def test_delete_permission(self, client):
        """Test deleting a permission."""
        token = get_access_token(client, "admin", "admin")
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.delete(f"/permission/33", headers=headers)

        assert response.status_code == 200
        assert "Success deleted permission" in response.json()["msg"]


class TestPermissionDenied:
    """Test suite for permission denial scenarios."""
    
    def test_unauthorized_user_cannot_create_role(self, client):
        """Test that unauthorized user cannot create roles."""        
        token = get_access_token(client, "user", "user")
        headers = {"Authorization": f"Bearer {token}"}
        
        new_role_data = {
            "name": "Hacker",
            "description": "Should not be created"
        }
        
        response = client.post("/roles/", json=new_role_data, headers=headers)
        assert response.status_code == 403
        assert "Permission denied" in response.json()["detail"]
    
    def test_unauthorized_user_cannot_delete_role(self, client):
        """Test that unauthorized user cannot delete roles."""
        token = get_access_token(client, "user", "user")
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.delete(f"/roles/45", headers=headers)

        assert response.status_code == 403
        
        assert "Permission denied" in response.json()["detail"]

def setup_module():
    from tests.utils import create_user, create_role, create_permission

    # Create the database tables 
    Base.metadata.create_all(bind=engine)

    # Create role
    create_role(44, "Testing Role", "Testing Description")
    create_role(45, "Testing Role 2", "Testing Description 2")

    # Create permission
    create_permission(33, "Testing Permission", "testing", "read", "testing")

    # Create admin
    create_user("admin", "admin", "active", is_superuser=True)

    # Create user
    create_user("user", "user")


def teardown_module():
    # Drop the database tables 
    Base.metadata.drop_all(bind=engine)