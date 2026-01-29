"""
Pytest configuration and fixtures for RSMate tests.
"""
import os
import pytest
import psycopg2
from psycopg2 import sql
from helpers.session_helper import sess_store_obj, sess_get_obj
from redshift.database import RSDatabase
from cryptography.fernet import Fernet


@pytest.fixture(scope="session")
def db_connection():
    """
    Fixture that provides a direct connection to the local PostgreSQL emulator.
    Uses psycopg2 to connect to the Redshift emulator.
    """
    # Wait for the emulator to be ready
    import time
    max_retries = 30
    retry_count = 0

    while retry_count < max_retries:
        try:
            conn = psycopg2.connect(
                host=os.getenv("REDSHIFT_HOST", "localhost"),
                port=int(os.getenv("REDSHIFT_PORT", "5439")),
                database=os.getenv("REDSHIFT_DB", "dev"),
                user=os.getenv("REDSHIFT_USER", "admin"),
                password=os.getenv("REDSHIFT_PASSWORD", "Admin123!"),
            )
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.close()
            break
        except psycopg2.OperationalError:
            retry_count += 1
            if retry_count >= max_retries:
                raise RuntimeError(f"Could not connect to emulator after {max_retries} retries")
            time.sleep(1)

    yield conn

    # Cleanup
    conn.close()


@pytest.fixture(scope="function")
def seeded_db(db_connection):
    """
    Fixture that ensures the database is seeded with test data.
    Runs before each test and optionally cleans up afterward.
    """
    cursor = db_connection.cursor()

    # Verify that the schema was initialized
    cursor.execute(
        "SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = '_pg_users')"
    )
    schema_exists = cursor.fetchone()[0]

    if not schema_exists:
        raise RuntimeError("Database schema not initialized. Check docker-compose setup.")

    cursor.close()
    yield db_connection

    # Optional: Clean up test data (not strictly necessary for unit tests)
    # For integration tests, you may want to preserve data between tests


@pytest.fixture(scope="function")
def mock_session(db_connection):
    """
    Fixture that provides a fake session dictionary with encrypted connection info.
    The connection points to the local emulator.
    """
    # Generate Fernet key if not set
    fernet_key = os.getenv("RSMATE_FERNET_KEY")
    if not fernet_key:
        fernet_key = Fernet.generate_key().decode()

    session = {
        "redshift_host": os.getenv("REDSHIFT_HOST", "localhost"),
        "redshift_port": int(os.getenv("REDSHIFT_PORT", "5439")),
        "redshift_db": os.getenv("REDSHIFT_DB", "dev"),
        "redshift_user": os.getenv("REDSHIFT_USER", "admin"),
        "redshift_password": os.getenv("REDSHIFT_PASSWORD", "Admin123!"),
        "redshift_cluster": "emulator",
    }

    return session


@pytest.fixture
def rs_database(mock_session):
    """
    Fixture that provides an RSDatabase instance connected to the emulator.
    """
    db = RSDatabase()
    db.set_connection_params(
        host=mock_session["redshift_host"],
        port=mock_session["redshift_port"],
        database=mock_session["redshift_db"],
        user=mock_session["redshift_user"],
        password=mock_session["redshift_password"],
    )
    yield db
    # Cleanup: close connection
    if hasattr(db, "cursor") and db.cursor:
        db.cursor.close()
    if hasattr(db, "connection") and db.connection:
        db.connection.close()


@pytest.fixture
def session_dict():
    """
    Fixture that provides a fresh session dictionary for testing session operations.
    """
    return {}
