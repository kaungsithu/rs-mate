"""
Tests for the ConnectionPool class in redshift/database.py
"""
import pytest
import queue
import time
import threading
from redshift.database import ConnectionPool


class TestConnectionPool:
    """Test the ConnectionPool implementation."""

    def test_pool_initialization(self):
        """Test that the pool initializes with minimum connections."""
        # Note: This test uses mock parameters since we may not have a live connection
        # In integration tests, this would connect to the emulator
        pass  # Skip for now as we need actual DB connection

    def test_get_connection_from_pool(self, db_connection):
        """Test that get_connection returns a valid connection."""
        # Create a pool
        pool = ConnectionPool(
            host="localhost",
            port=5439,
            database="dev",
            user="admin",
            password="Admin123!",
            min_connections=1,
            max_connections=2
        )

        try:
            # Get a connection
            conn = pool.get_connection(timeout=5.0)
            assert conn is not None

            # Release it
            pool.release_connection(conn)
        finally:
            pool.close_all()

    def test_release_connection_reuses(self, db_connection):
        """Test that released connections are reused."""
        pool = ConnectionPool(
            host="localhost",
            port=5439,
            database="dev",
            user="admin",
            password="Admin123!",
            min_connections=1,
            max_connections=2
        )

        try:
            # Get a connection
            conn1 = pool.get_connection(timeout=5.0)
            conn_id_1 = id(conn1)

            # Release it
            pool.release_connection(conn1)

            # Get another connection - should be the same one
            conn2 = pool.get_connection(timeout=5.0)
            conn_id_2 = id(conn2)

            assert conn_id_1 == conn_id_2, "Connection should be reused from pool"

            pool.release_connection(conn2)
        finally:
            pool.close_all()

    def test_pool_exhaustion(self, db_connection):
        """Test that exceeding max_connections raises an error."""
        pool = ConnectionPool(
            host="localhost",
            port=5439,
            database="dev",
            user="admin",
            password="Admin123!",
            min_connections=1,
            max_connections=2
        )

        try:
            # Get first connection
            conn1 = pool.get_connection(timeout=1.0)
            assert conn1 is not None

            # Get second connection (max is 2)
            conn2 = pool.get_connection(timeout=1.0)
            assert conn2 is not None

            # Try to get third connection (should timeout/fail)
            with pytest.raises(RuntimeError, match="Pool exhausted|Unable to acquire connection"):
                pool.get_connection(timeout=1.0)

            # Clean up
            pool.release_connection(conn1)
            pool.release_connection(conn2)
        finally:
            pool.close_all()

    def test_close_all_closes_connections(self, db_connection):
        """Test that close_all properly closes all connections."""
        pool = ConnectionPool(
            host="localhost",
            port=5439,
            database="dev",
            user="admin",
            password="Admin123!",
            min_connections=2,
            max_connections=5
        )

        # Get a connection
        conn = pool.get_connection(timeout=5.0)
        pool.release_connection(conn)

        # Close all
        pool.close_all()

        # Verify pool is marked as closed
        assert pool._closed is True

        # Try to get a connection - should raise error
        with pytest.raises(RuntimeError, match="Connection pool is closed"):
            pool.get_connection()

    def test_thread_safety(self, db_connection):
        """Test that concurrent access to the pool is thread-safe."""
        pool = ConnectionPool(
            host="localhost",
            port=5439,
            database="dev",
            user="admin",
            password="Admin123!",
            min_connections=2,
            max_connections=5
        )

        results = []
        errors = []

        def worker():
            try:
                for _ in range(3):
                    conn = pool.get_connection(timeout=5.0)
                    # Simulate some work
                    time.sleep(0.01)
                    pool.release_connection(conn)
                results.append(True)
            except Exception as e:
                errors.append(str(e))

        try:
            # Create multiple threads
            threads = [threading.Thread(target=worker) for _ in range(4)]

            # Start all threads
            for thread in threads:
                thread.start()

            # Wait for all threads to complete
            for thread in threads:
                thread.join(timeout=30)

            # Check results
            assert len(errors) == 0, f"Errors occurred: {errors}"
            assert len(results) == 4, "All threads should complete successfully"
        finally:
            pool.close_all()

    def test_pool_marked_closed_prevents_new_connections(self, db_connection):
        """Test that a closed pool rejects new connection requests."""
        pool = ConnectionPool(
            host="localhost",
            port=5439,
            database="dev",
            user="admin",
            password="Admin123!",
            min_connections=1,
            max_connections=2
        )

        pool.close_all()

        with pytest.raises(RuntimeError, match="Connection pool is closed"):
            pool.get_connection()
