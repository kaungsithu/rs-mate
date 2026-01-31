from ast import Tuple
from dataclasses import dataclass, asdict, field
from cryptography.fernet import Fernet
import redshift_connector
import json
import os
import queue
import threading
from typing import Optional
from .sql_queries import *

# TODO: Add proper logging mechnism instead of prints

redshift_connector.paramstyle = 'pyformat'


class ConnectionPool:
    """Thread-safe connection pool for Redshift connections."""

    def __init__(self, host: str, port: int, database: str, user: str, password: str,
                 min_connections: int = 2, max_connections: int = 10):
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self.min_connections = min_connections
        self.max_connections = max_connections
        self._pool = queue.Queue(maxsize=max_connections)
        self._lock = threading.Lock()
        self._connection_count = 0
        self._closed = False

        # Create minimum number of connections
        for _ in range(min_connections):
            self._create_connection()

    def _create_connection(self):
        """Create a new connection and add it to the pool."""
        if self._connection_count >= self.max_connections:
            return

        try:
            conn = redshift_connector.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password
            )
            with self._lock:
                self._pool.put(conn, block=False)
                self._connection_count += 1
        except Exception as e:
            print(f"Failed to create connection: {e}")

    def get_connection(self, timeout: float = 5.0):
        """Get a connection from the pool or create a new one."""
        if self._closed:
            raise RuntimeError("Connection pool is closed")

        try:
            # Try to get a connection from the pool
            return self._pool.get(block=True, timeout=timeout)
        except queue.Empty:
            # If pool is empty and we haven't reached max, create a new connection
            with self._lock:
                if self._connection_count < self.max_connections:
                    self._create_connection()
                    try:
                        return self._pool.get(block=True, timeout=timeout)
                    except queue.Empty:
                        raise RuntimeError("Unable to acquire connection from pool")
                else:
                    raise RuntimeError("Connection pool exhausted")

    def release_connection(self, conn):
        """Return a connection to the pool."""
        if conn and not self._closed:
            try:
                self._pool.put(conn, block=False)
            except queue.Full:
                # Pool is full, close the connection
                try:
                    conn.close()
                except Exception as e:
                    print(f"Error closing connection: {e}")

    def close_all(self):
        """Close all connections in the pool."""
        with self._lock:
            self._closed = True
            # Drain the queue and close all connections
            while not self._pool.empty():
                try:
                    conn = self._pool.get_nowait()
                    try:
                        conn.close()
                    except Exception as e:
                        print(f"Error closing connection: {e}")
                except queue.Empty:
                    break
            self._connection_count = 0


@dataclass
class Redshift:
    host: Optional[str] = None
    port: Optional[int] = 5439
    name: str = 'dev'
    user: Optional[str] = None
    pwd: Optional[str] = None
    _pool: Optional[ConnectionPool] = field(default=None, repr=False, init=False)
    # _password: bytes = field(default=b'', repr=False)

    # @property
    # def password(self) -> bytes:
    #     return Redshift.get_fernet().decrypt(self._password).decode()
    
    # @password.setter
    # def password(self, val: str) -> None:
    #     self._password = Redshift.get_fernet().encrypt(val.encode())

    # def __post_init__(self):
    #     if self.pwd:
    #         self.password = self.pwd
    #         self.pwd = None


    @staticmethod
    def get_fernet() -> Fernet:
        env_key = 'RSMATE_FERNET_KEY'
        # get fernet object with key from env var. key created if none 
        if env_key in os.environ:
            key = bytes.fromhex(os.environ.get(env_key))
        else:
            key = Fernet.generate_key()
            os.environ[env_key] = key.hex()
        return Fernet(key)

    def store_db_info(self, session):
        session['dbinfo'] = Redshift.get_fernet().encrypt(json.dumps(asdict(self)).encode()).decode()

    def load_db_info(self, session):
        try:
            return Redshift(**json.loads(Redshift.get_fernet().decrypt(session.get('dbinfo').encode()).decode()))
        except Exception as e:
            print(e)
            return None

    def _get_pool(self) -> ConnectionPool:
        """Get or create the connection pool."""
        if self._pool is None:
            self._pool = ConnectionPool(
                host=self.host,
                port=self.port,
                database=self.name,
                user=self.user,
                password=self.pwd
            )
        return self._pool

    def run_sql(self, query: str, args=None, fetch=True) -> Tuple | int | None:
        try:
            pool = self._get_pool()
            conn = pool.get_connection()
            try:
                with conn.cursor() as cursor:
                    cursor.execute(query, args=args)

                    if fetch:
                        results = cursor.fetchall()
                        return results
                    else:
                        conn.commit()
                        return cursor.rowcount
            finally:
                pool.release_connection(conn)
        except Exception as e:
            print(f"Database error: {e}")
            return None

    def close(self):
        """Close the connection pool and all active connections."""
        if self._pool is not None:
            self._pool.close_all()
            self._pool = None 

    def execute_query(self, query: str, args=None) -> Tuple | None:
        try:
            return self.run_sql(query, args, fetch=True)
        except Exception as e:
            print(e)
            return None 

    def execute_cmd(self, query: str, args=None) -> bool:
        try:
            return self.run_sql(query, args, fetch=False) == -1
        except Exception as e:
            print(e)
            return False

    def test_conn(self) -> bool:
        'Test connection by selecting 1. Returns True if successful.'
        return self.execute_query('SELECT 1') is not None
    
    def get_all_schemas(self) -> list:
        results = self.execute_query(GET_ALL_SCHEMAS, (self.name,))
        return [row[0] for row in results] if results else []
    
    def get_schema_tables(self, schema: str) -> list:
        results = self.execute_query(GET_SCHEMA_TABLES, (self.name, schema,))
        return [row[0] for row in results] if results else []
    
    def get_schema_views(self, schema: str) -> list:
        results = self.execute_query(GET_SCHEMA_VIEWS, (self.name, schema,))
        return [row[0] for row in results] if results else []
    
    def get_schema_functions(self, schema: str) -> list:
        results = self.execute_query(GET_SCHEMA_FUNCTIONS, (self.name, schema,))
        return [row[0] for row in results] if results else []
    
    def get_schema_procedures(self, schema: str) -> list:
        results = self.execute_query(GET_SCHEMA_PROCEDURES, (self.name, schema,))
        return [row[0] for row in results] if results else []
        
    def determine_object_type(self, schema_name: str, object_name: str, privilege_type: str, schema_relations: dict) -> str:
        """
        Determine the type of database object based on schema relations and privilege type
        
        Args:
            schema_name: The name of the schema
            object_name: The name of the object
            privilege_type: The type of privilege (SELECT, INSERT, UPDATE, DELETE, EXECUTE)
            schema_relations: Dictionary of schema relations from session
            
        Returns:
            str: The object type (TABLE, VIEW, FUNCTION, PROCEDURE, SCHEMA)
        """
        # Check if we have schema relations for this schema
        if schema_name in schema_relations:
            schema_data = schema_relations[schema_name]
            
            # For EXECUTE privilege, check if it's a function or procedure
            if privilege_type == 'EXECUTE':
                if object_name in schema_data.get('functions', []):
                    return 'FUNCTION'
                elif object_name in schema_data.get('procedures', []):
                    return 'PROCEDURE'
                else:
                    # If not found in cached data, query the database directly
                    functions = self.get_schema_functions(schema_name)
                    if object_name in functions:
                        return 'FUNCTION'
                    
                    procedures = self.get_schema_procedures(schema_name)
                    if object_name in procedures:
                        return 'PROCEDURE'
                    
                    # Default to FUNCTION if we can't determine
                    return 'FUNCTION'
            
            # For other privileges, check if it's a table or view
            else:
                if object_name in schema_data.get('tables', []):
                    return 'TABLE'
                elif object_name in schema_data.get('views', []):
                    return 'VIEW'
                else:
                    # If not found in cached data, query the database directly
                    tables = self.get_schema_tables(schema_name)
                    if object_name in tables:
                        return 'TABLE'
                    
                    views = self.get_schema_views(schema_name)
                    if object_name in views:
                        return 'VIEW'
                    
                    # If object name is empty or special value, it might be a schema-level privilege
                    if not object_name or object_name == schema_name:
                        return 'SCHEMA'
                    
                    # Default to TABLE if we can't determine
                    # This is a reasonable default since tables are more common than views
                    return 'TABLE'
        else:
            # If we don't have schema relations, query the database directly
            if privilege_type == 'EXECUTE':
                functions = self.get_schema_functions(schema_name)
                if object_name in functions:
                    return 'FUNCTION'
                
                procedures = self.get_schema_procedures(schema_name)
                if object_name in procedures:
                    return 'PROCEDURE'
                
                return 'FUNCTION'  # Default
            else:
                tables = self.get_schema_tables(schema_name)
                if object_name in tables:
                    return 'TABLE'
                
                views = self.get_schema_views(schema_name)
                if object_name in views:
                    return 'VIEW'
                
                # If object name is empty or special value, it might be a schema-level privilege
                if not object_name or object_name == schema_name:
                    return 'SCHEMA'

                return 'TABLE'  # Default


# Alias for backwards compatibility
RSDatabase = Redshift
