from app.database.connection import DatabaseConnection

class PostgresGroup:
    """
    PostgreSQL group model for handling database group operations
    """
    def __init__(self, name=None, gid=None, members=None):
        self.name = name
        self.gid = gid
        self.members = members or []
    
    @classmethod
    def create(cls, name, members=None):
        """
        Create a new PostgreSQL group
        
        Args:
            name (str): Group name
            members (list, optional): List of usernames to add to the group
            
        Returns:
            PostgresGroup: Created group object or None if failed
        """
        try:
            # Build the CREATE GROUP SQL statement
            query = f"CREATE GROUP {name}"
            
            if members and len(members) > 0:
                query += f" WITH USER {', '.join(members)}"
                
            # Execute the query
            DatabaseConnection.execute_query(query, fetch=False)
            
            # Get the group ID
            gid = cls.get_group_id(name)
            
            # Return the new group object
            return cls(
                name=name,
                gid=gid,
                members=members or []
            )
        except Exception as e:
            print(f"Error creating PostgreSQL group: {e}")
            return None
    
    @staticmethod
    def get_group_id(name):
        """
        Get a group's ID by name
        
        Args:
            name (str): Group name
            
        Returns:
            int: Group ID or None if not found
        """
        query = """
        SELECT grosysid
        FROM pg_group
        WHERE groname = %s;
        """
        result = DatabaseConnection.execute_query(query, (name,))
        
        if result and len(result) > 0:
            return result[0][0]
        return None
    
    @classmethod
    def get_all(cls):
        """
        Get all PostgreSQL groups
        
        Returns:
            list: List of PostgresGroup objects
        """
        query = """
        SELECT groname, grosysid
        FROM pg_group
        ORDER BY groname;
        """
        results = DatabaseConnection.execute_query(query)
        
        groups = []
        for group_data in results:
            group_name = group_data[0]
            group_id = group_data[1]
            
            # Get group members
            members = cls.get_group_members(group_name)
            
            groups.append(cls(
                name=group_name,
                gid=group_id,
                members=members
            ))
            
        return groups
    
    @classmethod
    def get_by_name(cls, name):
        """
        Get a PostgreSQL group by name
        
        Args:
            name (str): Group name
            
        Returns:
            PostgresGroup: Group object or None if not found
        """
        query = """
        SELECT groname, grosysid
        FROM pg_group
        WHERE groname = %s;
        """
        result = DatabaseConnection.execute_query(query, (name,))
        
        if result and len(result) > 0:
            group_data = result[0]
            group_name = group_data[0]
            group_id = group_data[1]
            
            # Get group members
            members = cls.get_group_members(group_name)
            
            return cls(
                name=group_name,
                gid=group_id,
                members=members
            )
        return None
    
    @staticmethod
    def get_group_members(group_name):
        """
        Get all members of a group
        
        Args:
            group_name (str): Group name
            
        Returns:
            list: List of usernames
        """
        query = """
        SELECT u.usename
        FROM pg_user u
        JOIN pg_group g ON u.usesysid = ANY(g.grolist)
        WHERE g.groname = %s;
        """
        results = DatabaseConnection.execute_query(query, (group_name,))
        
        members = []
        for member_data in results:
            members.append(member_data[0])
        return members
    
    def rename(self, new_name):
        """
        Rename a PostgreSQL group
        
        Args:
            new_name (str): New group name
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            query = f"ALTER GROUP {self.name} RENAME TO {new_name};"
            DatabaseConnection.execute_query(query, fetch=False)
            self.name = new_name
            return True
        except Exception as e:
            print(f"Error renaming PostgreSQL group: {e}")
            return False
    
    def delete(self):
        """
        Delete a PostgreSQL group
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            query = f"DROP GROUP {self.name};"
            DatabaseConnection.execute_query(query, fetch=False)
            return True
        except Exception as e:
            print(f"Error deleting PostgreSQL group: {e}")
            return False
    
    def add_user(self, username):
        """
        Add a user to the group
        
        Args:
            username (str): Username
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            query = f"ALTER GROUP {self.name} ADD USER {username};"
            DatabaseConnection.execute_query(query, fetch=False)
            
            # Update the members list
            if username not in self.members:
                self.members.append(username)
                
            return True
        except Exception as e:
            print(f"Error adding user to group: {e}")
            return False
    
    def remove_user(self, username):
        """
        Remove a user from the group
        
        Args:
            username (str): Username
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            query = f"ALTER GROUP {self.name} DROP USER {username};"
            DatabaseConnection.execute_query(query, fetch=False)
            
            # Update the members list
            if username in self.members:
                self.members.remove(username)
                
            return True
        except Exception as e:
            print(f"Error removing user from group: {e}")
            return False