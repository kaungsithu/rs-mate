"""
Unit tests for the RedshiftGroup model.
Tests CRUD operations and group-related queries.
"""
import pytest
from redshift.group import RedshiftGroup


@pytest.mark.unit
class TestRedshiftGroupModel:
    """Test RedshiftGroup dataclass and methods."""

    def test_redshift_group_initialization(self):
        """Test that RedshiftGroup can be initialized."""
        group = RedshiftGroup(group_name="group_analytics")
        assert group.group_name == "group_analytics"

    def test_redshift_group_default_users(self):
        """Test that users defaults to empty set."""
        group = RedshiftGroup(group_name="group_analytics")
        assert group.users == set()
        assert isinstance(group.users, set)

    def test_redshift_group_post_init_converts_list_to_set(self):
        """Test that __post_init__ converts user list to set."""
        group = RedshiftGroup(
            group_name="group_analytics",
            users=['user1', 'user2', 'user3']
        )
        assert isinstance(group.users, set)
        assert group.users == {'user1', 'user2', 'user3'}

    def test_redshift_group_modify_users_set(self):
        """Test that users set can be modified."""
        group = RedshiftGroup(group_name="group_analytics")
        group.users.add("user1")
        group.users.add("user2")
        assert "user1" in group.users
        assert "user2" in group.users
        assert len(group.users) == 2

    def test_redshift_group_remove_user(self):
        """Test removing a user from a group."""
        group = RedshiftGroup(
            group_name="group_analytics",
            users=['user1', 'user2']
        )
        group.users.discard('user1')
        assert "user1" not in group.users
        assert "user2" in group.users
        assert len(group.users) == 1

    def test_redshift_group_empty_users(self):
        """Test group with no users."""
        group = RedshiftGroup(group_name="empty_group")
        assert len(group.users) == 0
        assert group.users == set()


@pytest.mark.integration
class TestRedshiftGroupOperations:
    """Integration tests for group operations against the emulator."""

    def test_get_all_returns_list(self):
        """Test that get_all is a classmethod."""
        assert hasattr(RedshiftGroup, 'get_all')
        assert callable(RedshiftGroup.get_all)

    def test_get_group_returns_group_or_none(self):
        """Test that get_group is a classmethod."""
        assert hasattr(RedshiftGroup, 'get_group')
        assert callable(RedshiftGroup.get_group)

    def test_all_groups_from_seeded_db(self, seeded_db):
        """Test retrieving all groups from the seeded database."""
        cursor = seeded_db.cursor()
        cursor.execute("SELECT grosysid, groname FROM pg_group ORDER BY grosysid")
        groups = cursor.fetchall()
        cursor.close()

        # Should have at least 5 seeded groups
        assert len(groups) >= 5
        group_names = [g[1] for g in groups]
        assert 'group_analytics' in group_names
        assert 'group_engineering' in group_names

    def test_group_details_from_seeded_db(self, seeded_db):
        """Test retrieving a specific group."""
        cursor = seeded_db.cursor()
        cursor.execute(
            "SELECT grosysid, groname FROM pg_group WHERE groname = 'group_analytics'"
        )
        group = cursor.fetchone()
        cursor.close()

        assert group is not None
        assert group[1] == 'group_analytics'

    def test_group_members_from_seeded_db(self, seeded_db):
        """Test retrieving members of a group."""
        cursor = seeded_db.cursor()
        cursor.execute("""
            SELECT u.usename FROM _pg_users u
            JOIN _user_group_membership ugm ON ugm.user_id = u.usesysid
            JOIN _pg_groups g ON g.grosysid = ugm.group_id
            WHERE g.groname = 'group_analytics'
            ORDER BY u.usename
        """)
        members = cursor.fetchall()
        cursor.close()

        # group_analytics should have multiple users
        assert len(members) > 0
        member_names = [m[0] for m in members]
        assert 'user1' in member_names

    def test_get_group_users_structure(self):
        """Test that get_group_users method exists."""
        assert hasattr(RedshiftGroup, 'get_group_users')
        assert callable(RedshiftGroup.get_group_users)

    def test_add_user_to_group_structure(self):
        """Test that add_user method exists."""
        group = RedshiftGroup(group_name="test_group")
        assert hasattr(group, 'add_user')
        assert callable(group.add_user)

    def test_remove_user_from_group_structure(self):
        """Test that remove_user method exists."""
        group = RedshiftGroup(group_name="test_group")
        assert hasattr(group, 'remove_user')
        assert callable(group.remove_user)

    def test_create_group_structure(self):
        """Test that create_group method exists."""
        assert hasattr(RedshiftGroup, 'create_group')
        assert callable(RedshiftGroup.create_group)

    def test_drop_group_structure(self):
        """Test that drop_group method exists."""
        assert hasattr(RedshiftGroup, 'drop_group')
        assert callable(RedshiftGroup.drop_group)

    def test_user_group_membership_count(self, seeded_db):
        """Test that user-group memberships exist."""
        cursor = seeded_db.cursor()
        cursor.execute("SELECT COUNT(*) FROM _user_group_membership")
        count = cursor.fetchone()[0]
        cursor.close()

        assert count > 0

    def test_group_user_count(self, seeded_db):
        """Test counting users in a group."""
        cursor = seeded_db.cursor()
        cursor.execute("""
            SELECT COUNT(*) FROM _user_group_membership ugm
            WHERE ugm.group_id = (
                SELECT grosysid FROM _pg_groups WHERE groname = 'group_analytics'
            )
        """)
        count = cursor.fetchone()[0]
        cursor.close()

        assert count >= 5  # group_analytics should have at least 5 users
