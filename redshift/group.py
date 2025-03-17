import redshift.sql_queries as sql
from redshift.database import Redshift
from dataclasses import dataclass, field
from typing import Optional, List, Set

@dataclass
class RedshiftGroup:
    group_name: str
    users: Set[str] = field(default_factory=set)
    
    def __post_init__(self):
        # Convert lists to sets for easier manipulation
        if isinstance(self.users, list):
            self.users = set(self.users)
    
    @classmethod
    def get_all(cls, rs: Redshift) -> list:
        """
        Get all Redshift groups
        
        Returns:
            list: List of RedshiftGroup objects
        """
        try:
            results = rs.execute_query(sql.GET_ALL_GROUPS)
            groups = []
            
            if results:
                for row in results:
                    group_name = row[0]
                    
                    # Create group object with the available information
                    group = cls(
                        group_name=group_name
                    )
                    groups.append(group)
                
            return groups
        except Exception as e:
            print(f"Error getting all groups: {e}")
            return []
    
    @classmethod
    def get_group(cls, group_name: str, rs: Redshift) -> 'RedshiftGroup':
        """
        Get a specific group by name
        
        Args:
            group_name: The name of the group to retrieve
            rs: Redshift connection
            
        Returns:
            RedshiftGroup object or None if not found
        """
        try:
            # Check if group exists
            results = rs.execute_query(sql.GET_GROUP_INFO, (group_name,))
            if not results:
                return None
                
            # Create group object
            group = cls(group_name=group_name)
            
            # Get users for this group
            group.users = set(cls.get_group_users(group_name, rs))
            
            return group
        except Exception as e:
            print(f"Error getting group {group_name}: {e}")
            return None
    
    @staticmethod
    def get_group_users(group_name: str, rs: Redshift) -> list:
        """
        Get all users for a specific group
        
        Args:
            group_name: The name of the group
            rs: Redshift connection
            
        Returns:
            list: List of usernames
        """
        try:
            results = rs.execute_query(sql.GET_GROUP_USERS, (group_name,))
            return [row[0] for row in results] if results else []
        except Exception as e:
            print(f"Error getting users for group {group_name}: {e}")
            return []
    
    def add_user(self, user_name: str, rs: Redshift) -> bool:
        """
        Add a user to this group
        
        Args:
            user_name: The name of the user to add
            rs: Redshift connection
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Add user to group SQL
            add_sql = f"ALTER GROUP {self.group_name} ADD USER {user_name};"
            
            # Execute SQL
            success = rs.execute_cmd(add_sql)
            
            if success:
                self.users.add(user_name)
                
            return success
        except Exception as e:
            print(f"Error adding user {user_name} to group {self.group_name}: {e}")
            return False
    
    def remove_user(self, user_name: str, rs: Redshift) -> bool:
        """
        Remove a user from this group
        
        Args:
            user_name: The name of the user to remove
            rs: Redshift connection
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Remove user from group SQL
            remove_sql = f"ALTER GROUP {self.group_name} DROP USER {user_name};"
            
            # Execute SQL
            success = rs.execute_cmd(remove_sql)
            
            if success:
                self.users.discard(user_name)
                
            return success
        except Exception as e:
            print(f"Error removing user {user_name} from group {self.group_name}: {e}")
            return False
    
    def update_users(self, new_users: set, rs: Redshift) -> bool:
        """
        Update the users for this group
        
        Args:
            new_users: Set of new usernames
            rs: Redshift connection
            
        Returns:
            bool: True if all operations were successful, False otherwise
        """
        try:
            # Find users to add and remove
            cur_users = set(RedshiftGroup.get_group_users(self.group_name, rs))
            users_to_add = new_users - cur_users
            users_to_remove = cur_users - new_users
            
            # Remove users
            for user_name in users_to_remove:
                if not self.remove_user(user_name, rs):
                    return False
                    
            # Add users
            for user_name in users_to_add:
                if not self.add_user(user_name, rs):
                    return False
                    
            return True
        except Exception as e:
            print(f"Error updating users for group {self.group_name}: {e}")
            return False
    
    @classmethod
    def create_group(cls, group_name: str, rs: Redshift) -> 'RedshiftGroup':
        """
        Create a new group in Redshift
        
        Args:
            group_name: The name of the new group
            rs: Redshift connection
            
        Returns:
            RedshiftGroup object or None if creation failed
        """
        try:
            # Create group SQL
            create_sql = f"CREATE GROUP {group_name};"
            
            # Execute SQL
            success = rs.execute_cmd(create_sql)
            
            if success:
                return cls(group_name=group_name)
            return None
        except Exception as e:
            print(f"Error creating group {group_name}: {e}")
            return None
    
    def delete(self, rs: Redshift) -> bool:
        """
        Delete this group from Redshift
        
        Args:
            rs: Redshift connection
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Delete group SQL
            delete_sql = f"DROP GROUP {self.group_name};"
            
            # Execute SQL
            return rs.execute_cmd(delete_sql)
        except Exception as e:
            print(f"Error deleting group {self.group_name}: {e}")
            return False
