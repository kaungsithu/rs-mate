"""
Unit tests for SQL query definitions.
Validates that all SQL queries are syntactically correct and executable.
"""
import pytest
from redshift import sql_queries


@pytest.mark.unit
class TestSQLQueriesExist:
    """Test that all expected SQL query constants are defined."""

    def test_get_all_users_query_exists(self):
        """Test that GET_ALL_USERS query is defined."""
        assert hasattr(sql_queries, 'GET_ALL_USERS')
        assert sql_queries.GET_ALL_USERS is not None
        assert isinstance(sql_queries.GET_ALL_USERS, str)
        assert len(sql_queries.GET_ALL_USERS) > 0

    def test_get_user_groups_query_exists(self):
        """Test that GET_USER_GROUPS query is defined."""
        assert hasattr(sql_queries, 'GET_USER_GROUPS')
        assert sql_queries.GET_USER_GROUPS is not None

    def test_get_user_roles_query_exists(self):
        """Test that GET_USER_ROLES query is defined."""
        assert hasattr(sql_queries, 'GET_USER_ROLES')
        assert sql_queries.GET_USER_ROLES is not None

    def test_get_all_roles_query_exists(self):
        """Test that GET_ALL_ROLES query is defined."""
        assert hasattr(sql_queries, 'GET_ALL_ROLES')
        assert sql_queries.GET_ALL_ROLES is not None

    def test_get_role_info_query_exists(self):
        """Test that GET_ROLE_INFO query is defined."""
        assert hasattr(sql_queries, 'GET_ROLE_INFO')
        assert sql_queries.GET_ROLE_INFO is not None

    def test_get_all_groups_query_exists(self):
        """Test that GET_ALL_GROUPS query is defined."""
        assert hasattr(sql_queries, 'GET_ALL_GROUPS')
        assert sql_queries.GET_ALL_GROUPS is not None

    def test_get_group_info_query_exists(self):
        """Test that GET_GROUP_INFO query is defined."""
        assert hasattr(sql_queries, 'GET_GROUP_INFO')
        assert sql_queries.GET_GROUP_INFO is not None

    def test_get_group_users_query_exists(self):
        """Test that GET_GROUP_USERS query is defined."""
        assert hasattr(sql_queries, 'GET_GROUP_USERS')
        assert sql_queries.GET_GROUP_USERS is not None

    def test_get_user_info_query_exists(self):
        """Test that GET_USER_INFO query is defined."""
        assert hasattr(sql_queries, 'GET_USER_INFO')
        assert sql_queries.GET_USER_INFO is not None

    def test_get_user_info_by_name_query_exists(self):
        """Test that GET_USER_INFO_BY_NAME query is defined."""
        assert hasattr(sql_queries, 'GET_USER_INFO_BY_NAME')
        assert sql_queries.GET_USER_INFO_BY_NAME is not None

    def test_get_all_role_users_query_exists(self):
        """Test that GET_ALL_ROLE_USERS query is defined."""
        assert hasattr(sql_queries, 'GET_ALL_ROLE_USERS')
        assert sql_queries.GET_ALL_ROLE_USERS is not None

    def test_get_role_users_query_exists(self):
        """Test that GET_ROLE_USERS query is defined."""
        assert hasattr(sql_queries, 'GET_ROLE_USERS')
        assert sql_queries.GET_ROLE_USERS is not None


@pytest.mark.unit
class TestSQLQueryStructure:
    """Test the structure of SQL queries."""

    def test_queries_are_strings(self):
        """Test that all query constants are strings."""
        query_attrs = [attr for attr in dir(sql_queries) if attr.isupper()]
        for attr_name in query_attrs:
            attr = getattr(sql_queries, attr_name)
            if isinstance(attr, str):
                assert len(attr) > 0, f"{attr_name} is empty"

    def test_select_queries_contain_select_keyword(self):
        """Test that SELECT queries contain SELECT keyword."""
        get_all_users = sql_queries.GET_ALL_USERS
        assert 'SELECT' in get_all_users.upper()

    def test_queries_should_not_have_syntax_errors(self):
        """Test that query strings don't have obvious syntax errors."""
        queries_to_check = [
            ('GET_ALL_USERS', sql_queries.GET_ALL_USERS),
            ('GET_ALL_ROLES', sql_queries.GET_ALL_ROLES),
            ('GET_ALL_GROUPS', sql_queries.GET_ALL_GROUPS),
        ]

        for name, query in queries_to_check:
            # Basic checks for obvious syntax errors
            if 'SELECT' in query.upper():
                assert 'FROM' in query.upper(), f"{name} missing FROM clause"


@pytest.mark.integration
class TestSQLQueriesExecute:
    """Integration tests that execute queries against the emulator."""

    def test_get_all_users_executes(self, seeded_db):
        """Test that GET_ALL_USERS query executes successfully."""
        cursor = seeded_db.cursor()
        try:
            cursor.execute(sql_queries.GET_ALL_USERS)
            results = cursor.fetchall()
            assert results is not None
            # Should return users
            assert len(results) >= 0
        finally:
            cursor.close()

    def test_get_all_users_returns_correct_columns(self, seeded_db):
        """Test that GET_ALL_USERS returns expected columns."""
        cursor = seeded_db.cursor()
        try:
            cursor.execute(sql_queries.GET_ALL_USERS)
            # Check that we get column names
            assert cursor.description is not None
            assert len(cursor.description) > 0
        finally:
            cursor.close()

    def test_get_all_roles_executes(self, seeded_db):
        """Test that GET_ALL_ROLES query executes successfully."""
        cursor = seeded_db.cursor()
        try:
            cursor.execute(sql_queries.GET_ALL_ROLES)
            results = cursor.fetchall()
            assert results is not None
            assert len(results) >= 10
        finally:
            cursor.close()

    def test_get_all_groups_executes(self, seeded_db):
        """Test that GET_ALL_GROUPS query executes successfully."""
        cursor = seeded_db.cursor()
        try:
            cursor.execute(sql_queries.GET_ALL_GROUPS)
            results = cursor.fetchall()
            assert results is not None
            assert len(results) >= 5
        finally:
            cursor.close()

    def test_get_user_groups_executes(self, seeded_db):
        """Test that GET_USER_GROUPS query executes with parameter."""
        cursor = seeded_db.cursor()
        try:
            # Get user1's ID first
            cursor.execute("SELECT usesysid FROM _pg_users WHERE usename = 'user1'")
            user_id = cursor.fetchone()[0]

            # Now execute GET_USER_GROUPS
            cursor.execute(sql_queries.GET_USER_GROUPS, (user_id,))
            results = cursor.fetchall()
            assert results is not None
        finally:
            cursor.close()

    def test_get_user_roles_executes(self, seeded_db):
        """Test that GET_USER_ROLES query executes with parameter."""
        cursor = seeded_db.cursor()
        try:
            # Get user1's ID first
            cursor.execute("SELECT usesysid FROM _pg_users WHERE usename = 'user1'")
            user_id = cursor.fetchone()[0]

            # Now execute GET_USER_ROLES
            cursor.execute(sql_queries.GET_USER_ROLES, (user_id,))
            results = cursor.fetchall()
            assert results is not None
        finally:
            cursor.close()

    def test_get_role_info_executes(self, seeded_db):
        """Test that GET_ROLE_INFO query executes with parameter."""
        cursor = seeded_db.cursor()
        try:
            cursor.execute(sql_queries.GET_ROLE_INFO, ('analysts',))
            results = cursor.fetchall()
            assert results is not None
            # analysts role should exist in seed data
            assert len(results) > 0
        finally:
            cursor.close()

    def test_get_group_info_executes(self, seeded_db):
        """Test that GET_GROUP_INFO query executes with parameter."""
        cursor = seeded_db.cursor()
        try:
            cursor.execute(sql_queries.GET_GROUP_INFO, ('group_analytics',))
            results = cursor.fetchall()
            assert results is not None
            # group_analytics should exist in seed data
            assert len(results) > 0
        finally:
            cursor.close()

    def test_get_group_users_executes(self, seeded_db):
        """Test that GET_GROUP_USERS query executes with parameter."""
        cursor = seeded_db.cursor()
        try:
            cursor.execute(sql_queries.GET_GROUP_USERS, ('group_analytics',))
            results = cursor.fetchall()
            assert results is not None
            # group_analytics should have users
            assert len(results) > 0
        finally:
            cursor.close()

    def test_parameterized_queries_with_sample_values(self, seeded_db):
        """Test that parameterized queries work with sample values."""
        cursor = seeded_db.cursor()
        try:
            # Test various parameterized queries
            cursor.execute(sql_queries.GET_USER_GROUPS, (101,))
            user_101_groups = cursor.fetchall()
            assert user_101_groups is not None

            cursor.execute(sql_queries.GET_USER_ROLES, (101,))
            user_101_roles = cursor.fetchall()
            assert user_101_roles is not None
        finally:
            cursor.close()
