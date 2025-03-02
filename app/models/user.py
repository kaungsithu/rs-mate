from app.database.connection import DatabaseConnection

class PostgresUser:
    """
    PostgreSQL user model for handling database user operations
    """
    def __init__(self, username=None, superuser=False, createdb=False, createrole=False, 
                 inherit=True, login=True, connection_limit=-1, password=None, valid_until=None):
        self.username = username
        self.superuser = superuser
        self.createdb = createdb
        self.createrole = createrole
        self.inherit = inherit
        self.login = login
        self.connection_limit = connection_limit
        self.password = password
        self.valid_until = valid_until
        self.groups = []
    
    @classmethod
    def create(cls, username, password, superuser=False, createdb=False, createrole=False, 
               inherit=True, login=True, connection_limit=-1, valid_until=None):
        """
        Create a new PostgreSQL user
        
        Args:
            username (str): Username
            password (str): Password
            superuser (bool): Whether the user is a superuser
            createdb (bool): Whether the user can create databases
            createrole (bool): Whether the user can create roles
            inherit (bool): Whether the user inherits privileges
            login (bool): Whether the user can login
            connection_limit (int): Connection limit (-1 for unlimited)
            valid_until (str): Password expiration date
            
        Returns:
            PostgresUser: Created user object or None if failed
        """
        try:
            # Build the CREATE USER SQL statement
            query = f"CREATE USER {username}"
            options = []
            
            if superuser:
                options.append("SUPERUSER")
            else:
                options.append("NOSUPERUSER")
                
            if createdb:
                options.append("CREATEDB")
            else:
                options.append("NOCREATEDB")
                
            if createrole:
                options.append("CREATEROLE")
            else:
                options.append("NOCREATEROLE")
                
            if inherit:
                options.append("INHERIT")
            else:
                options.append("NOINHERIT")
                
            if login:
                options.append("LOGIN")
            else:
                options.append("NOLOGIN")
                
            if connection_limit != -1:
                options.append(f"CONNECTION LIMIT {connection_limit}")
                
            if password:
                options.append(f"PASSWORD '{password}'")
                
            if valid_until:
                options.append(f"VALID UNTIL '{valid_until}'")
                
            if options:
                query += " WITH " + " ".join(options)
                
            # Execute the query
            DatabaseConnection.execute_query(query, fetch=False)
            
            # Return the new user object
            return cls(
                username=username,
                superuser=superuser,
                createdb=createdb,
                createrole=createrole,
                inherit=inherit,
                login=login,
                connection_limit=connection_limit,
                password=password,
                valid_until=valid_until
            )
        except Exception as e:
            print(f"Error creating PostgreSQL user: {e}")
            return None
    
    @classmethod
    def get_all(cls):
        """
        Get all PostgreSQL users
        
        Returns:
            list: List of PostgresUser objects
        """
        query = """
        SELECT 
            usename, 
            usesuper, 
            usecreatedb, 
            rolcreaterole, 
            useinhherit, 
            uselogin, 
            useconnlimit, 
            valuntil
        FROM pg_catalog.pg_user
        ORDER BY usename;
        """
        results = DatabaseConnection.execute_query(query)
        
        users = []
        for user_data in results:
            user = cls(
                username=user_data[0],
                superuser=user_data[1],
                createdb=user_data[2],
                createrole=user_data[3],
                inherit=user_data[4],
                login=user_data[5],
                connection_limit=user_data[6],
                valid_until=user_data[7]
            )
            
            # Get user's groups
            user.groups = cls.get_user_groups(user.username)
            users.append(user)
            
        return users
    
    @classmethod
    def get_by_username(cls, username):
        """
        Get a PostgreSQL user by username
        
        Args:
            username (str): Username
            
        Returns:
            PostgresUser: User object or None if not found
        """
        query = """
        SELECT 
            usename, 
            usesuper, 
            usecreatedb, 
            usecreaterole, 
            useinherit, 
            uselogin, 
            useconnlimit, 
            valuntil
        FROM pg_catalog.pg_user
        WHERE usename = %s;
        """
        result = DatabaseConnection.execute_query(query, (username,))
        
        if result and len(result) > 0:
            user_data = result[0]
            user = cls(
                username=user_data[0],
                superuser=user_data[1],
                createdb=user_data[2],
                createrole=user_data[3],
                inherit=user_data[4],
                login=user_data[5],
                connection_limit=user_data[6],
                valid_until=user_data[7]
            )
            
            # Get user's groups
            user.groups = cls.get_user_groups(user.username)
            return user
        return None
    
    @staticmethod
    def get_user_groups(username):
        """
        Get all groups a user belongs to
        
        Args:
            username (str): Username
            
        Returns:
            list: List of group names
        """
        query = """
        SELECT g.groname
        FROM pg_group g
        JOIN pg_user u ON u.usesysid = ANY(g.grolist)
        WHERE u.usename = %s;
        """
        results = DatabaseConnection.execute_query(query, (username,))
        
        groups = []
        for group_data in results:
            groups.append(group_data[0])
        return groups
    
    def update(self, password=None, superuser=None, createdb=None, createrole=None, 
               inherit=None, login=None, connection_limit=None, valid_until=None):
        """
        Update PostgreSQL user
        
        Args:
            password (str, optional): New password
            superuser (bool, optional): Whether the user is a superuser
            createdb (bool, optional): Whether the user can create databases
            createrole (bool, optional): Whether the user can create roles
            inherit (bool, optional): Whether the user inherits privileges
            login (bool, optional): Whether the user can login
            connection_limit (int, optional): Connection limit (-1 for unlimited)
            valid_until (str, optional): Password expiration date
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Build the ALTER USER SQL statement
            query = f"ALTER USER {self.username}"
            options = []
            
            if superuser is not None:
                options.append("SUPERUSER" if superuser else "NOSUPERUSER")
                self.superuser = superuser
                
            if createdb is not None:
                options.append("CREATEDB" if createdb else "NOCREATEDB")
                self.createdb = createdb
                
            if createrole is not None:
                options.append("CREATEROLE" if createrole else "NOCREATEROLE")
                self.createrole = createrole
                
            if inherit is not None:
                options.append("INHERIT" if inherit else "NOINHERIT")
                self.inherit = inherit
                
            if login is not None:
                options.append("LOGIN" if login else "NOLOGIN")
                self.login = login
                
            if connection_limit is not None:
                options.append(f"CONNECTION LIMIT {connection_limit}")
                self.connection_limit = connection_limit
                
            if password:
                options.append(f"PASSWORD '{password}'")
                self.password = password
                
            if valid_until is not None:
                if valid_until:
                    options.append(f"VALID UNTIL '{valid_until}'")
                else:
                    options.append("VALID UNTIL 'infinity'")
                self.valid_until = valid_until
                
            if options:
                query += " WITH " + " ".join(options)
                
            # Execute the query
            DatabaseConnection.execute_query(query, fetch=False)
            return True
        except Exception as e:
            print(f"Error updating PostgreSQL user: {e}")
            return False
    
    def delete(self):
        """
        Delete a PostgreSQL user
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            query = f"DROP USER {self.username};"
            DatabaseConnection.execute_query(query, fetch=False)
            return True
        except Exception as e:
            print(f"Error deleting PostgreSQL user: {e}")
            return False
    
    def add_to_group(self, group_name):
        """
        Add user to a group
        
        Args:
            group_name (str): Group name
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            query = f"ALTER GROUP {group_name} ADD USER {self.username};"
            DatabaseConnection.execute_query(query, fetch=False)
            
            # Update the groups list
            if group_name not in self.groups:
                self.groups.append(group_name)
                
            return True
        except Exception as e:
            print(f"Error adding user to group: {e}")
            return False
    
    def remove_from_group(self, group_name):
        """
        Remove user from a group
        
        Args:
            group_name (str): Group name
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            query = f"ALTER GROUP {group_name} DROP USER {self.username};"
            DatabaseConnection.execute_query(query, fetch=False)
            
            # Update the groups list
            if group_name in self.groups:
                self.groups.remove(group_name)
                
            return True
        except Exception as e:
            print(f"Error removing user from group: {e}")
            return False
