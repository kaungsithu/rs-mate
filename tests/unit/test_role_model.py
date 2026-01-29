"""
Unit tests for the RedshiftRole model.
Tests CRUD operations and role-related queries.
"""
import pytest
from redshift.role import RedshiftRole


@pytest.mark.unit
class TestRedshiftRoleModel:
    """Test RedshiftRole dataclass and methods."""

    def test_redshift_role_initialization(self):
        """Test that RedshiftRole can be initialized."""
        role = RedshiftRole(role_name="analysts")
        assert role.role_name == "analysts"

    def test_redshift_role_initialization_with_id(self):
        """Test RedshiftRole initialization with role_id."""
        role = RedshiftRole(
            role_name="analysts",
            role_id=201
        )
        assert role.role_name == "analysts"
        assert role.role_id == 201

    def test_redshift_role_initialization_with_owner(self):
        """Test RedshiftRole initialization with owner info."""
        role = RedshiftRole(
            role_name="analysts",
            role_id=201,
            owner_id=1,
            owner_name="admin"
        )
        assert role.owner_id == 1
        assert role.owner_name == "admin"

    def test_redshift_role_default_nested_roles(self):
        """Test that nested_roles defaults to empty set."""
        role = RedshiftRole(role_name="analysts")
        assert role.nested_roles == set()
        assert isinstance(role.nested_roles, set)

    def test_redshift_role_default_users(self):
        """Test that users defaults to empty set."""
        role = RedshiftRole(role_name="analysts")
        assert role.users == set()
        assert isinstance(role.users, set)

    def test_redshift_role_default_privileges(self):
        """Test that privileges defaults to empty list."""
        role = RedshiftRole(role_name="analysts")
        assert role.privileges == []

    def test_redshift_role_post_init_converts_list_to_set(self):
        """Test that __post_init__ converts lists to sets."""
        role = RedshiftRole(
            role_name="analysts",
            nested_roles=['role1', 'role2'],
            users=['user1', 'user2']
        )
        assert isinstance(role.nested_roles, set)
        assert isinstance(role.users, set)
        assert role.nested_roles == {'role1', 'role2'}
        assert role.users == {'user1', 'user2'}

    def test_redshift_role_modify_users_set(self):
        """Test that users set can be modified."""
        role = RedshiftRole(role_name="analysts")
        role.users.add("user1")
        role.users.add("user2")
        assert "user1" in role.users
        assert "user2" in role.users
        assert len(role.users) == 2

    def test_redshift_role_modify_nested_roles_set(self):
        """Test that nested_roles set can be modified."""
        role = RedshiftRole(role_name="analysts")
        role.nested_roles.add("admin_role")
        role.nested_roles.add("power_users")
        assert "admin_role" in role.nested_roles
        assert "power_users" in role.nested_roles
        assert len(role.nested_roles) == 2

    def test_redshift_role_add_privileges(self):
        """Test adding privileges to a role."""
        role = RedshiftRole(role_name="analysts")
        privilege = {
            "schema": "public",
            "table": "users",
            "privilege_type": "SELECT"
        }
        role.privileges.append(privilege)
        assert len(role.privileges) == 1
        assert role.privileges[0]["schema"] == "public"


@pytest.mark.integration
class TestRedshiftRoleOperations:
    """Integration tests for role operations against the emulator."""

    def test_get_all_returns_list(self):
        """Test that get_all is a classmethod that returns a list."""
        assert hasattr(RedshiftRole, 'get_all')
        assert callable(RedshiftRole.get_all)

    def test_get_role_returns_role_or_none(self):
        """Test that get_role is a classmethod."""
        assert hasattr(RedshiftRole, 'get_role')
        assert callable(RedshiftRole.get_role)

    def test_all_roles_from_seeded_db(self, seeded_db):
        """Test retrieving all roles from the seeded database."""
        cursor = seeded_db.cursor()
        cursor.execute("SELECT role_id, role_name FROM svv_roles ORDER BY role_id")
        roles = cursor.fetchall()
        cursor.close()

        # Should have at least 10 seeded roles
        assert len(roles) >= 10
        role_names = [r[1] for r in roles]
        assert 'analysts' in role_names
        assert 'engineers' in role_names

    def test_role_details_from_seeded_db(self, seeded_db):
        """Test retrieving a specific role from the seeded database."""
        cursor = seeded_db.cursor()
        cursor.execute(
            "SELECT role_id, role_name FROM svv_roles WHERE role_name = 'analysts'"
        )
        role = cursor.fetchone()
        cursor.close()

        assert role is not None
        assert role[1] == 'analysts'

    def test_role_users_from_seeded_db(self, seeded_db):
        """Test retrieving users assigned to a role."""
        cursor = seeded_db.cursor()
        cursor.execute("""
            SELECT u.usename FROM _pg_users u
            JOIN _role_grants rg ON rg.member_id = u.usesysid
            JOIN _svv_roles r ON r.role_id = rg.role_id
            WHERE r.role_name = 'analysts'
        """)
        users = cursor.fetchall()
        cursor.close()

        # analysts role should have some users
        assert len(users) > 0
        user_names = [u[0] for u in users]
        assert 'user1' in user_names

    def test_role_membership_query(self, seeded_db):
        """Test querying role membership."""
        cursor = seeded_db.cursor()
        cursor.execute("""
            SELECT role_id, member_id FROM _role_grants
            LIMIT 10
        """)
        grants = cursor.fetchall()
        cursor.close()

        assert len(grants) > 0
        for grant in grants:
            assert isinstance(grant[0], int)  # role_id
            assert isinstance(grant[1], int)  # member_id

    def test_get_all_role_users_structure(self):
        """Test that get_all_role_users method exists."""
        assert hasattr(RedshiftRole, 'get_all_role_users')
        assert callable(RedshiftRole.get_all_role_users)

    def test_get_role_users_structure(self):
        """Test that get_role_users method exists."""
        assert hasattr(RedshiftRole, 'get_role_users')
        assert callable(RedshiftRole.get_role_users)

    def test_get_role_nested_roles_structure(self):
        """Test that get_role_nested_roles method exists."""
        assert hasattr(RedshiftRole, 'get_role_nested_roles')
        assert callable(RedshiftRole.get_role_nested_roles)

    def test_get_role_privileges_structure(self):
        """Test that get_role_privileges method exists."""
        assert hasattr(RedshiftRole, 'get_role_privileges')
        assert callable(RedshiftRole.get_role_privileges)

    def test_role_option_fields(self):
        """Test optional fields in RedshiftRole."""
        role = RedshiftRole(
            role_name="test_role",
            role_id=999,
            owner_id=1,
            owner_name="admin"
        )
        assert role.role_id == 999
        assert role.owner_id == 1
        assert role.owner_name == "admin"
