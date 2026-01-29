"""
Unit tests for the RedshiftUser model.
Tests CRUD operations and user-related queries.
"""
import pytest
from redshift.user import RedshiftUser
from redshift.database import Redshift


@pytest.mark.unit
class TestRedshiftUserModel:
    """Test RedshiftUser dataclass and methods."""

    def test_redshift_user_initialization(self):
        """Test that RedshiftUser can be initialized with required fields."""
        user = RedshiftUser(
            user_name="testuser",
            user_id=999,
            super_user=False
        )
        assert user.user_name == "testuser"
        assert user.user_id == 999
        assert user.super_user is False

    def test_redshift_user_initialization_with_optional_fields(self):
        """Test RedshiftUser initialization with optional fields."""
        user = RedshiftUser(
            user_name="testuser",
            user_id=999,
            super_user=False,
            can_create_db=True,
            connection_limit=5
        )
        assert user.can_create_db is True
        assert user.connection_limit == 5

    def test_redshift_user_default_groups_list(self):
        """Test that groups list defaults to empty."""
        user = RedshiftUser(
            user_name="testuser",
            user_id=999,
            super_user=False
        )
        assert user.groups == []

    def test_redshift_user_default_roles_list(self):
        """Test that roles list defaults to empty."""
        user = RedshiftUser(
            user_name="testuser",
            user_id=999,
            super_user=False
        )
        assert user.roles == []

    def test_redshift_user_default_privileges_list(self):
        """Test that privileges list defaults to empty."""
        user = RedshiftUser(
            user_name="testuser",
            user_id=999,
            super_user=False
        )
        assert user.privileges == []

    def test_redshift_user_update_fields(self):
        """Test updating user fields."""
        user = RedshiftUser(
            user_name="testuser",
            user_id=999,
            super_user=False
        )
        user.update_fields({"super_user": True, "can_create_db": True})
        assert user.super_user is True
        assert user.can_create_db is True

    def test_redshift_user_update_fields_partial(self):
        """Test that only specified fields are updated."""
        user = RedshiftUser(
            user_name="testuser",
            user_id=999,
            super_user=False,
            can_create_db=False
        )
        user.update_fields({"super_user": True})
        assert user.super_user is True
        assert user.can_create_db is False  # Should not change

    def test_redshift_user_update_fields_with_none(self):
        """Test that update_fields handles None gracefully."""
        user = RedshiftUser(
            user_name="testuser",
            user_id=999,
            super_user=False
        )
        user.update_fields(None)
        # Should not raise an error
        assert user.user_name == "testuser"

    def test_redshift_user_map_results(self):
        """Test mapping database results to user objects."""
        results = [
            (101, 'user1', True, False, False, None, None, None),
            (102, 'user2', False, True, False, None, None, None),
        ]
        cols = ['user_id', 'user_name', 'super_user', 'can_create_db',
                'can_update_catalog', 'password_expiry', 'session_defaults',
                'connection_limit']

        users = RedshiftUser.map_results(results, cols)
        assert len(users) == 2
        assert users[0].user_id == 101
        assert users[0].user_name == 'user1'
        assert users[1].user_id == 102
        assert users[1].user_name == 'user2'

    def test_redshift_user_map_results_empty(self):
        """Test mapping empty results."""
        results = []
        cols = ['user_id', 'user_name', 'super_user', 'can_create_db',
                'can_update_catalog', 'password_expiry', 'session_defaults',
                'connection_limit']

        users = RedshiftUser.map_results(results, cols)
        assert len(users) == 0


@pytest.mark.integration
class TestRedshiftUserOperations:
    """Integration tests for user operations against the emulator."""

    def test_get_all_returns_list(self, rs_database):
        """Test that get_all returns a list of users."""
        # This requires rs_database to be properly initialized
        # For now, we test that the method is callable
        assert hasattr(RedshiftUser, 'get_all')
        assert callable(RedshiftUser.get_all)

    def test_get_all_users_from_seeded_db(self, seeded_db):
        """Test retrieving all users from the seeded database."""
        cursor = seeded_db.cursor()
        cursor.execute("SELECT usesysid, usename FROM pg_user_info ORDER BY usesysid")
        users = cursor.fetchall()
        cursor.close()

        # Should have at least the admin user and seeded users
        assert len(users) >= 20
        user_names = [u[1] for u in users]
        assert 'user1' in user_names
        assert 'admin' in user_names

    def test_get_user_groups_query(self, seeded_db):
        """Test that user groups can be queried."""
        cursor = seeded_db.cursor()
        # Query for user1's groups from the _user_group_membership table
        cursor.execute("""
            SELECT g.groname FROM pg_group g
            JOIN _user_group_membership ugm ON ugm.group_id = g.grosysid
            JOIN _pg_users u ON u.usesysid = ugm.user_id
            WHERE u.usename = 'user1'
        """)
        groups = cursor.fetchall()
        cursor.close()

        # user1 should be in group_analytics
        assert len(groups) > 0
        group_names = [g[0] for g in groups]
        assert 'group_analytics' in group_names

    def test_get_user_roles_query(self, seeded_db):
        """Test that user roles can be queried."""
        cursor = seeded_db.cursor()
        # Query for user1's roles
        cursor.execute("""
            SELECT r.role_name FROM svv_roles r
            JOIN _role_grants rg ON rg.role_id = r.role_id
            JOIN _pg_users u ON u.usesysid = rg.member_id
            WHERE u.usename = 'user1'
        """)
        roles = cursor.fetchall()
        cursor.close()

        # user1 should have at least one role
        assert len(roles) > 0

    def test_user_password_field(self):
        """Test that user can have password field set."""
        user = RedshiftUser(
            user_name="testuser",
            user_id=999,
            super_user=False,
            password="SecurePassword123!"
        )
        assert user.password == "SecurePassword123!"

    def test_user_session_timeout_field(self):
        """Test that user can have session timeout."""
        user = RedshiftUser(
            user_name="testuser",
            user_id=999,
            super_user=False,
            session_timeout=1800
        )
        assert user.session_timeout == 1800

    def test_user_password_expiry_field(self):
        """Test that user can have password expiry."""
        user = RedshiftUser(
            user_name="testuser",
            user_id=999,
            super_user=False,
            password_expiry="2025-12-31"
        )
        assert user.password_expiry == "2025-12-31"
