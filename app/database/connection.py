import psycopg2
from psycopg2 import pool

class DatabaseConnection:
    """
    A class to manage database connections using connection pooling
    """
    _connection_pool = None

    @classmethod
    def initialize(cls, dbname, user, password, host="0.0.0.0", port="5432", min_connections=1, max_connections=10):
        """
        Initialize the connection pool
        """
        try:
            cls._connection_pool = pool.ThreadedConnectionPool(
                min_connections,
                max_connections,
                user=user,
                password=password,
                host=host,
                port=port,
                dbname=dbname
            )
            print(f"Connection pool created successfully")
            
            # Test the connection
            conn = cls.get_connection()
            if conn:
                print("Database connection test successful")
                cls.return_connection(conn)
            return True
        except Exception as e:
            print(f"Error initializing database connection pool: {e}")
            return False

    @classmethod
    def get_connection(cls):
        """
        Get a connection from the pool
        """
        if cls._connection_pool is None:
            raise Exception("Connection pool not initialized")
        return cls._connection_pool.getconn()

    @classmethod
    def return_connection(cls, connection):
        """
        Return a connection to the pool
        """
        if cls._connection_pool is None:
            raise Exception("Connection pool not initialized")
        cls._connection_pool.putconn(connection)

    @classmethod
    def close_all_connections(cls):
        """
        Close all connections in the pool
        """
        if cls._connection_pool is None:
            return
        cls._connection_pool.closeall()
        print("All database connections closed")

    @classmethod
    def execute_query(cls, query, params=None, fetch=True):
        """
        Execute a query and return the results
        
        Args:
            query (str): SQL query to execute
            params (tuple): Parameters for the query
            fetch (bool): Whether to fetch results or not
            
        Returns:
            list: Query results if fetch is True, otherwise None
        """
        connection = None
        cursor = None
        try:
            connection = cls.get_connection()
            cursor = connection.cursor()
            cursor.execute(query, params)
            
            if fetch:
                results = cursor.fetchall()
                return results
            else:
                connection.commit()
                return cursor.rowcount
        except Exception as e:
            if connection:
                connection.rollback()
            print(f"Database error: {e}")
            raise
        finally:
            if cursor:
                cursor.close()
            if connection:
                cls.return_connection(connection)