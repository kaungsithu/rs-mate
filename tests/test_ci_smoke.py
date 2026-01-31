"""
Smoke tests for CI/CD pipeline.
These are lightweight tests that verify basic imports and setup work.
"""
import pytest
import os
from cryptography.fernet import Fernet


class TestModuleImports:
    """Test that main modules can be imported without error."""

    def test_import_redshift_user(self):
        """Test importing redshift.user module."""
        from redshift import user
        assert user is not None
        assert hasattr(user, 'RSUser')

    def test_import_redshift_role(self):
        """Test importing redshift.role module."""
        from redshift import role
        assert role is not None
        assert hasattr(role, 'RSRole')

    def test_import_redshift_group(self):
        """Test importing redshift.group module."""
        from redshift import group
        assert group is not None
        assert hasattr(group, 'RSGroup')

    def test_import_redshift_database(self):
        """Test importing redshift.database module."""
        from redshift import database
        assert database is not None
        assert hasattr(database, 'RSDatabase')

    def test_import_redshift_sql_queries(self):
        """Test importing redshift.sql_queries module."""
        from redshift import sql_queries
        assert sql_queries is not None

    def test_import_session_helper(self):
        """Test importing helpers.session_helper module."""
        from helpers import session_helper
        assert session_helper is not None
        assert hasattr(session_helper, 'sess_store_obj')
        assert hasattr(session_helper, 'sess_get_obj')

    def test_import_components(self):
        """Test importing components modules."""
        from components import common
        from components import database
        from components import user
        from components import role
        from components import group

        assert common is not None
        assert database is not None
        assert user is not None
        assert role is not None
        assert group is not None


class TestFernetKeyGeneration:
    """Test that Fernet key generation works properly."""

    def test_fernet_key_can_be_generated(self):
        """Test that a Fernet key can be generated."""
        key = Fernet.generate_key()
        assert key is not None
        assert len(key) > 0

    def test_fernet_key_can_encrypt_decrypt(self):
        """Test that generated Fernet key works for encryption/decryption."""
        key = Fernet.generate_key()
        cipher = Fernet(key)

        test_data = b"test data"
        encrypted = cipher.encrypt(test_data)
        decrypted = cipher.decrypt(encrypted)

        assert decrypted == test_data

    def test_fernet_key_environment_variable(self):
        """Test that Fernet key can be read from environment."""
        # Generate a key if not set
        if not os.getenv("RSMATE_FERNET_KEY"):
            new_key = Fernet.generate_key().decode()
            os.environ["RSMATE_FERNET_KEY"] = new_key

        key_str = os.getenv("RSMATE_FERNET_KEY")
        assert key_str is not None

        # Verify it's a valid Fernet key
        key_bytes = key_str.encode() if isinstance(key_str, str) else key_str
        cipher = Fernet(key_bytes)
        assert cipher is not None


class TestDataclassDefinitions:
    """Test that dataclass definitions are properly set up."""

    def test_rsuser_dataclass_exists(self):
        """Test that RSUser dataclass is properly defined."""
        from redshift.user import RSUser
        assert hasattr(RSUser, '__dataclass_fields__')

    def test_rsrole_dataclass_exists(self):
        """Test that RSRole dataclass is properly defined."""
        from redshift.role import RSRole
        assert hasattr(RSRole, '__dataclass_fields__')

    def test_rsgroup_dataclass_exists(self):
        """Test that RSGroup dataclass is properly defined."""
        from redshift.group import RSGroup
        assert hasattr(RSGroup, '__dataclass_fields__')


class TestSessionHelper:
    """Test session helper functions."""

    def test_sess_store_obj_and_sess_get_obj_exist(self):
        """Test that session helper functions are available."""
        from helpers.session_helper import sess_store_obj, sess_get_obj
        assert callable(sess_store_obj)
        assert callable(sess_get_obj)

    def test_session_dict_operations(self, session_dict):
        """Test basic session dictionary operations."""
        from helpers.session_helper import sess_store_obj, sess_get_obj

        # Store a simple value
        test_value = {"key": "value"}
        sess_store_obj(session_dict, "test_key", test_value)

        # Verify it was stored
        assert "test_key" in session_dict

    def test_fernet_key_initialization(self):
        """Test that Fernet key can be properly initialized."""
        # This should not raise an error
        key = Fernet.generate_key()
        cipher = Fernet(key)
        assert cipher is not None
