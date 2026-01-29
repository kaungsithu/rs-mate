"""
Tests for the Redshift emulator setup.
Validates that the emulator is properly configured with schema and seed data.
"""
import pytest


class TestEmulatorConnection:
    """Test emulator connection and basic functionality."""

    def test_emulator_connection_succeeds(self, db_connection):
        """Test that a connection to the emulator can be established."""
        assert db_connection is not None
        cursor = db_connection.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        cursor.close()
        assert result == (1,)

    def test_seeded_db_fixture_works(self, seeded_db):
        """Test that the seeded_db fixture initializes properly."""
        assert seeded_db is not None
        cursor = seeded_db.cursor()
        cursor.execute("SELECT COUNT(*) FROM _pg_users")
        count = cursor.fetchone()[0]
        cursor.close()
        assert count > 0


class TestSchemaInitialization:
    """Test that system catalog views are properly created."""

    def test_pg_user_info_view_exists(self, seeded_db):
        """Test that pg_user_info view exists and has correct columns."""
        cursor = seeded_db.cursor()
        cursor.execute("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'pg_user_info'
            ORDER BY ordinal_position
        """)
        columns = [col[0] for col in cursor.fetchall()]
        cursor.close()

        expected_columns = ['usesysid', 'usename', 'usesuper', 'usecreatedb',
                           'usecanlogin', 'usecreaterole', 'valuntil', 'useconfig']
        assert columns == expected_columns

    def test_svv_roles_view_exists(self, seeded_db):
        """Test that svv_roles view exists with correct columns."""
        cursor = seeded_db.cursor()
        cursor.execute("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'svv_roles'
            ORDER BY ordinal_position
        """)
        columns = [col[0] for col in cursor.fetchall()]
        cursor.close()

        expected_columns = ['role_id', 'role_name', 'super', 'create_db', 'create_user']
        assert columns == expected_columns

    def test_pg_group_view_exists(self, seeded_db):
        """Test that pg_group view exists with correct columns."""
        cursor = seeded_db.cursor()
        cursor.execute("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'pg_group'
            ORDER BY ordinal_position
        """)
        columns = [col[0] for col in cursor.fetchall()]
        cursor.close()

        expected_columns = ['grosysid', 'groname', 'grolist']
        assert columns == expected_columns

    def test_svv_role_grants_view_exists(self, seeded_db):
        """Test that svv_role_grants view exists."""
        cursor = seeded_db.cursor()
        cursor.execute("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'svv_role_grants'
            ORDER BY ordinal_position
        """)
        columns = [col[0] for col in cursor.fetchall()]
        cursor.close()

        expected_columns = ['role_id', 'member_id', 'member_name', 'role_name']
        assert columns == expected_columns

    def test_svv_relation_privileges_view_exists(self, seeded_db):
        """Test that svv_relation_privileges view exists."""
        cursor = seeded_db.cursor()
        cursor.execute("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'svv_relation_privileges'
            ORDER BY ordinal_position
        """)
        columns = [col[0] for col in cursor.fetchall()]
        cursor.close()

        expected_columns = ['schema_id', 'schema_name', 'table_id', 'table_name',
                           'grantee', 'privilege_type', 'is_grantable']
        assert columns == expected_columns


class TestSeedData:
    """Test that seed data was properly inserted."""

    def test_seeded_db_has_users(self, seeded_db):
        """Test that at least 20 users were seeded."""
        cursor = seeded_db.cursor()
        cursor.execute("SELECT COUNT(*) FROM pg_user_info WHERE usesysid >= 101")
        count = cursor.fetchone()[0]
        cursor.close()
        assert count >= 20

    def test_seeded_db_has_roles(self, seeded_db):
        """Test that at least 10 roles were seeded."""
        cursor = seeded_db.cursor()
        cursor.execute("SELECT COUNT(*) FROM svv_roles WHERE role_id >= 201")
        count = cursor.fetchone()[0]
        cursor.close()
        assert count >= 10

    def test_seeded_db_has_groups(self, seeded_db):
        """Test that at least 5 groups were seeded."""
        cursor = seeded_db.cursor()
        cursor.execute("SELECT COUNT(*) FROM pg_group WHERE grosysid >= 301")
        count = cursor.fetchone()[0]
        cursor.close()
        assert count >= 5

    def test_seeded_db_has_schemas(self, seeded_db):
        """Test that at least 15 schemas were seeded."""
        cursor = seeded_db.cursor()
        cursor.execute("SELECT COUNT(*) FROM _schema_info WHERE schema_id >= 5")
        count = cursor.fetchone()[0]
        cursor.close()
        assert count >= 15

    def test_seeded_db_has_tables(self, seeded_db):
        """Test that at least 200 tables were seeded."""
        cursor = seeded_db.cursor()
        cursor.execute("SELECT COUNT(*) FROM _relation_types WHERE relkind = 'r'")
        count = cursor.fetchone()[0]
        cursor.close()
        assert count >= 200

    def test_user_details(self, seeded_db):
        """Test that user details are correct."""
        cursor = seeded_db.cursor()
        cursor.execute("SELECT usesysid, usename FROM pg_user_info WHERE usename = 'user1'")
        result = cursor.fetchone()
        cursor.close()

        assert result is not None
        assert result[1] == 'user1'

    def test_role_details(self, seeded_db):
        """Test that role details are correct."""
        cursor = seeded_db.cursor()
        cursor.execute("SELECT role_id, role_name FROM svv_roles WHERE role_name = 'analysts'")
        result = cursor.fetchone()
        cursor.close()

        assert result is not None
        assert result[1] == 'analysts'

    def test_group_details(self, seeded_db):
        """Test that group details are correct."""
        cursor = seeded_db.cursor()
        cursor.execute("SELECT grosysid, groname FROM pg_group WHERE groname = 'group_analytics'")
        result = cursor.fetchone()
        cursor.close()

        assert result is not None
        assert result[1] == 'group_analytics'

    def test_role_grants_exist(self, seeded_db):
        """Test that role grants were properly inserted."""
        cursor = seeded_db.cursor()
        cursor.execute("SELECT COUNT(*) FROM _role_grants")
        count = cursor.fetchone()[0]
        cursor.close()
        assert count > 0

    def test_role_grants_view_works(self, seeded_db):
        """Test that svv_role_grants view returns data correctly."""
        cursor = seeded_db.cursor()
        cursor.execute("SELECT COUNT(*) FROM svv_role_grants")
        count = cursor.fetchone()[0]
        cursor.close()
        assert count > 0

    def test_privilege_data_inserted(self, seeded_db):
        """Test that privilege data was inserted."""
        cursor = seeded_db.cursor()
        cursor.execute("SELECT COUNT(*) FROM _svv_relation_privileges")
        count = cursor.fetchone()[0]
        cursor.close()
        # The seed data should have privileges
        assert count > 0


class TestSystemCatalogQueries:
    """Test that common Redshift catalog queries work."""

    def test_select_all_users(self, seeded_db):
        """Test querying all users from pg_user_info."""
        cursor = seeded_db.cursor()
        cursor.execute("SELECT usesysid, usename FROM pg_user_info ORDER BY usesysid")
        results = cursor.fetchall()
        cursor.close()

        assert len(results) > 0
        # Check that admin user (ID 1) exists
        user_ids = [r[0] for r in results]
        assert 1 in user_ids

    def test_select_all_roles(self, seeded_db):
        """Test querying all roles from svv_roles."""
        cursor = seeded_db.cursor()
        cursor.execute("SELECT role_id, role_name FROM svv_roles ORDER BY role_id")
        results = cursor.fetchall()
        cursor.close()

        assert len(results) >= 10

    def test_select_all_groups(self, seeded_db):
        """Test querying all groups from pg_group."""
        cursor = seeded_db.cursor()
        cursor.execute("SELECT grosysid, groname FROM pg_group ORDER BY grosysid")
        results = cursor.fetchall()
        cursor.close()

        assert len(results) >= 5

    def test_select_user_roles(self, seeded_db):
        """Test querying roles for a specific user."""
        cursor = seeded_db.cursor()
        cursor.execute("""
            SELECT r.role_name FROM svv_role_grants sr
            JOIN svv_roles r ON r.role_id = sr.role_id
            WHERE sr.member_name = 'user1'
        """)
        results = cursor.fetchall()
        cursor.close()

        # User1 should have some roles
        assert len(results) > 0

    def test_select_table_privileges(self, seeded_db):
        """Test querying table privileges."""
        cursor = seeded_db.cursor()
        cursor.execute("""
            SELECT schema_name, table_name, grantee, privilege_type
            FROM svv_relation_privileges
            LIMIT 10
        """)
        results = cursor.fetchall()
        cursor.close()

        assert len(results) > 0

    def test_select_schema_objects(self, seeded_db):
        """Test selecting all tables in a schema."""
        cursor = seeded_db.cursor()
        cursor.execute("""
            SELECT rt.relname, si.schema_name
            FROM _relation_types rt
            JOIN _schema_info si ON si.schema_id = rt.relnamespace
            WHERE rt.relkind = 'r'
            LIMIT 20
        """)
        results = cursor.fetchall()
        cursor.close()

        assert len(results) > 0
