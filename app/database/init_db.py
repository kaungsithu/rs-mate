from app.database.connection import DatabaseConnection

default_host = "default-workgroup.755276635383.ap-southeast-1.redshift-serverless.amazonaws.com:5439/dev"

def initialize_database(dbname, user, password, host=default_host, port="5439"):
    """
    Initialize the database connection
    """
    # Initialize database connection
    if DatabaseConnection.initialize(dbname, user, password, host, port):
        # Test the connection
        try:
            # Check if we can query the pg_user table
            query = "SELECT usename FROM pg_user LIMIT 1;"
            result = DatabaseConnection.execute_query(query)
            print(f"Database connection test successful. Found user: {result[0][0] if result else 'None'}")
            return True
        except Exception as e:
            print(f"Error testing database connection: {e}")
            return False
    return False