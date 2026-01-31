import redshift.sql_queries as sql
from redshift.database import Redshift
from redshift.sanitize import validate_identifier
from dataclasses import dataclass, field
from typing import Optional, List, Set

@dataclass
class RedshiftRole:
    role_name: str
    role_id: Optional[int] = None
    owner_id: Optional[int] = None
    owner_name: Optional[str] = None
    nested_roles: Set[str] = field(default_factory=set)
    users: Set[str] = field(default_factory=set)
    privileges: List[dict] = field(default_factory=list)
    
    def __post_init__(self):
        # Convert lists to sets for easier manipulation
        if isinstance(self.nested_roles, list):
            self.nested_roles = set(self.nested_roles)
        if isinstance(self.users, list):
            self.users = set(self.users)
    
    @classmethod
    def get_all(cls, rs: Redshift) -> list:
        """
        Get all Redshift roles
        
        Returns:
            list: List of RedshiftRole objects
        """
        try:
            results = rs.execute_query(sql.GET_ALL_ROLES)
            roles = []
            
            if results:
                for row in results:
                    role_id = row[0]
                    role_name = row[1]
                    role_owner = row[2] if len(row) > 2 else None
                    
                    # Create role object with the available information
                    role = cls(
                        role_name=role_name,
                        role_id=role_id,
                        owner_name=role_owner
                    )
                    roles.append(role)
                
                # Users and nested roles are lazily loaded when needed
                
            return roles
        except Exception as e:
            print(f"Error getting all roles: {e}")
            return []
    
    @classmethod
    def get_role(cls, role_name: str, rs: Redshift) -> 'RedshiftRole':
        """
        Get a specific role by name
        
        Args:
            role_name: The name of the role to retrieve
            rs: Redshift connection
            
        Returns:
            RedshiftRole object or None if not found
        """
        try:
            # Check if role exists
            results = rs.execute_query(sql.GET_ROLE_INFO, (role_name,))
            if not results:
                return None
                
            # Create role object
            role = cls(role_name=role_name)
            
            # Get users for this role
            role.users = set(cls.get_role_users(role_name, rs))
            
            # Get nested roles for this role
            role.nested_roles = set(cls.get_role_nested_roles(role_name, rs))
            
            # Get privileges for this role
            role.privileges = cls.get_role_privileges(role_name, rs)
            
            return role
        except Exception as e:
            print(f"Error getting role {role_name}: {e}")
            return None
    
    @staticmethod
    def get_all_role_users(rs: Redshift) -> dict:
        """
        Get all users for all roles
        
        Returns:
            dict: Dictionary mapping role names to sets of usernames
        """
        try:
            results = rs.execute_query(sql.GET_ALL_ROLE_USERS)
            role_users = {}
            
            if results:
                for row in results:
                    role_name, user_name = row
                    if role_name not in role_users:
                        role_users[role_name] = set()
                    role_users[role_name].add(user_name)
                    
            return role_users
        except Exception as e:
            print(f"Error getting role users: {e}")
            return {}
    
    @staticmethod
    def get_role_users(role_name: str, rs: Redshift) -> list:
        """
        Get all users for a specific role
        
        Args:
            role_name: The name of the role
            rs: Redshift connection
            
        Returns:
            list: List of usernames
        """
        try:
            results = rs.execute_query(sql.GET_ROLE_USERS, (role_name,))
            return [row[0] for row in results] if results else []
        except Exception as e:
            print(f"Error getting users for role {role_name}: {e}")
            return []
    
    @staticmethod
    def get_all_role_nested_roles(rs: Redshift) -> dict:
        """
        Get all nested roles for all roles
        
        Returns:
            dict: Dictionary mapping role names to sets of nested role names
        """
        try:
            results = rs.execute_query(sql.GET_ALL_ROLE_NESTED_ROLES)
            role_nested_roles = {}
            
            if results:
                for row in results:
                    role_name, nested_role_name = row
                    if role_name not in role_nested_roles:
                        role_nested_roles[role_name] = set()
                    role_nested_roles[role_name].add(nested_role_name)
                    
            return role_nested_roles
        except Exception as e:
            print(f"Error getting nested roles: {e}")
            return {}
    
    @staticmethod
    def get_role_nested_roles(role_name: str, rs: Redshift) -> list:
        """
        Get all nested roles for a specific role
        
        Args:
            role_name: The name of the role
            rs: Redshift connection
            
        Returns:
            list: List of nested role names
        """
        try:
            results = rs.execute_query(sql.GET_ROLE_NESTED_ROLES, (role_name,))
            return [row[0] for row in results] if results else []
        except Exception as e:
            print(f"Error getting nested roles for role {role_name}: {e}")
            return []
    
    @staticmethod
    def get_role_privileges(role_name: str, rs: Redshift) -> list:
        """
        Get all privileges for a specific role (uses batch query for better performance)

        Args:
            role_name: The name of the role
            rs: Redshift connection

        Returns:
            list: List of privilege dictionaries
        """
        try:
            results = rs.execute_query(sql.GET_ROLE_PRIVILEGES_BATCH, (rs.name, role_name, rs.name, role_name,))
            privileges = []

            if results:
                for row in results:
                    privilege = {
                        'schema_name': row[0],
                        'object_name': row[1],
                        'object_type': row[2],
                        'privilege_type': row[3],
                        'is_grantable': row[4]
                    }
                    privileges.append(privilege)

            return privileges
        except Exception as e:
            print(f"Error getting privileges for role {role_name}: {e}")
            return []

    @staticmethod
    def get_schema_relations_batch(rs: Redshift, schema_list: List[str] = None) -> dict:
        """
        Get all relations (tables, views, functions, procedures) for all schemas in one batch query.

        Args:
            rs: Redshift connection
            schema_list: Optional list of schemas to filter by. If None, gets all schemas.

        Returns:
            dict: Dictionary with schema names as keys and dict of relations as values
                 {
                     'schema_name': {
                         'tables': ['table1', 'table2'],
                         'views': ['view1'],
                         'functions': ['func1'],
                         'procedures': ['proc1']
                     }
                 }
        """
        try:
            results = rs.execute_query(sql.GET_ALL_SCHEMAS_WITH_RELATIONS,
                                      (rs.name, rs.name, rs.name, rs.name, rs.name, rs.name))
            schema_relations = {}

            if results:
                for schema_name, relation_name, relation_type in results:
                    # Skip if schema_list is provided and schema is not in it
                    if schema_list and schema_name not in schema_list:
                        continue

                    if schema_name not in schema_relations:
                        schema_relations[schema_name] = {
                            'tables': [],
                            'views': [],
                            'functions': [],
                            'procedures': []
                        }

                    # Only add non-None relation names
                    if relation_name is not None:
                        if relation_type == 'TABLE':
                            schema_relations[schema_name]['tables'].append(relation_name)
                        elif relation_type == 'VIEW':
                            schema_relations[schema_name]['views'].append(relation_name)
                        elif relation_type == 'FUNCTION':
                            schema_relations[schema_name]['functions'].append(relation_name)
                        elif relation_type == 'PROCEDURE':
                            schema_relations[schema_name]['procedures'].append(relation_name)

            return schema_relations
        except Exception as e:
            print(f"Error getting schema relations batch: {e}")
            return {}
    
    @classmethod
    def create_role(cls, role_name: str, rs: Redshift) -> 'RedshiftRole':
        """
        Create a new role in Redshift

        Args:
            role_name: The name of the new role
            rs: Redshift connection

        Returns:
            RedshiftRole object or None if creation failed
        """
        try:
            # Validate and sanitize role name
            role = validate_identifier(role_name)

            # Create role SQL
            create_sql = f"CREATE ROLE {role};"

            # Execute SQL
            success = rs.execute_cmd(create_sql)

            if success:
                return cls(role_name=role_name)
            return None
        except (ValueError, Exception) as e:
            print(f"Error creating role {role_name}: {e}")
            return None
    
    def delete(self, rs: Redshift) -> bool:
        """
        Delete this role from Redshift

        Args:
            rs: Redshift connection

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Check if role is granted to any users
            if self.users:
                return False

            # Validate and sanitize role name
            role = validate_identifier(self.role_name)

            # Delete role SQL
            delete_sql = f"DROP ROLE {role};"

            # Execute SQL
            return rs.execute_cmd(delete_sql)
        except (ValueError, Exception) as e:
            print(f"Error deleting role {self.role_name}: {e}")
            return False
    
    def add_nested_role(self, nested_role_name: str, rs: Redshift) -> bool:
        """
        Add a nested role to this role

        Args:
            nested_role_name: The name of the nested role to add
            rs: Redshift connection

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Validate and sanitize role names
            nested_role = validate_identifier(nested_role_name)
            current_role = validate_identifier(self.role_name)

            # Grant role SQL
            grant_sql = f"GRANT ROLE {nested_role} TO ROLE {current_role};"

            # Execute SQL
            success = rs.execute_cmd(grant_sql)

            if success:
                self.nested_roles.add(nested_role_name)

            return success
        except (ValueError, Exception) as e:
            print(f"Error adding nested role {nested_role_name} to {self.role_name}: {e}")
            return False
    
    def remove_nested_role(self, nested_role_name: str, rs: Redshift) -> bool:
        """
        Remove a nested role from this role

        Args:
            nested_role_name: The name of the nested role to remove
            rs: Redshift connection

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Validate and sanitize role names
            nested_role = validate_identifier(nested_role_name)
            current_role = validate_identifier(self.role_name)

            # Revoke role SQL
            revoke_sql = f"REVOKE ROLE {nested_role} FROM ROLE {current_role};"

            # Execute SQL
            success = rs.execute_cmd(revoke_sql)

            if success:
                self.nested_roles.discard(nested_role_name)

            return success
        except (ValueError, Exception) as e:
            print(f"Error removing nested role {nested_role_name} from {self.role_name}: {e}")
            return False
    
    def update_nested_roles(self, new_nested_roles: set, rs: Redshift) -> bool:
        """
        Update the nested roles for this role
        
        Args:
            new_nested_roles: Set of new nested role names
            rs: Redshift connection
            
        Returns:
            bool: True if all operations were successful, False otherwise
        """
        try:
            # Find roles to add and remove
            cur_roles = set(RedshiftRole.get_role_nested_roles(self.role_name, rs))
            roles_to_add = new_nested_roles - cur_roles
            roles_to_remove = cur_roles - new_nested_roles
            
            # Remove roles
            for role_name in roles_to_remove:
                if not self.remove_nested_role(role_name, rs):
                    return False
                    
            # Add roles
            for role_name in roles_to_add:
                if not self.add_nested_role(role_name, rs):
                    return False
                    
            return True
        except Exception as e:
            print(f"Error updating nested roles for {self.role_name}: {e}")
            return False
    
    def grant_privilege(self, schema_name: str, object_name: str, object_type: str,
                       privilege_type: str, rs: Redshift) -> bool:
        """
        Grant a privilege to this role

        Args:
            schema_name: The name of the schema
            object_name: The name of the object
            object_type: The type of the object (TABLE, VIEW, FUNCTION, PROCEDURE)
            privilege_type: The type of privilege (SELECT, INSERT, UPDATE, DELETE, EXECUTE)
            rs: Redshift connection

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Validate and sanitize identifiers
            schema = validate_identifier(schema_name)
            obj_name = validate_identifier(object_name)
            obj_type = validate_identifier(object_type)
            priv_type = validate_identifier(privilege_type)
            role = validate_identifier(self.role_name)

            # Grant privilege SQL
            if obj_type.upper() in ['TABLE', 'VIEW']:
                grant_sql = f"GRANT {priv_type} ON {schema}.{obj_name} TO ROLE {role};"
            elif obj_type.upper() in ['FUNCTION', 'PROCEDURE']:
                grant_sql = f"GRANT EXECUTE ON {obj_type} {schema}.{obj_name} TO ROLE {role};"
            else:
                # Schema level privilege
                grant_sql = f"GRANT {priv_type} ON SCHEMA {schema} TO ROLE {role};"

            # Execute SQL
            success = rs.execute_cmd(grant_sql)

            if success:
                # Add to privileges list
                self.privileges.append({
                    'schema_name': schema_name,
                    'object_name': object_name,
                    'object_type': object_type,
                    'privilege_type': privilege_type,
                    'is_grantable': False
                })

            return success
        except (ValueError, Exception) as e:
            print(f"Error granting privilege to {self.role_name}: {e}")
            return False
    
    def revoke_privilege(self, schema_name: str, object_name: str, object_type: str,
                        privilege_type: str, rs: Redshift) -> bool:
        """
        Revoke a privilege from this role

        Args:
            schema_name: The name of the schema
            object_name: The name of the object
            object_type: The type of the object (TABLE, VIEW, FUNCTION, PROCEDURE)
            privilege_type: The type of privilege (SELECT, INSERT, UPDATE, DELETE, EXECUTE)
            rs: Redshift connection

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Validate and sanitize identifiers
            schema = validate_identifier(schema_name)
            obj_name = validate_identifier(object_name)
            obj_type = validate_identifier(object_type)
            priv_type = validate_identifier(privilege_type)
            role = validate_identifier(self.role_name)

            # Revoke privilege SQL
            if obj_type.upper() in ['TABLE', 'VIEW']:
                revoke_sql = f"REVOKE {priv_type} ON {schema}.{obj_name} FROM ROLE {role};"
            elif obj_type.upper() in ['FUNCTION', 'PROCEDURE']:
                revoke_sql = f"REVOKE EXECUTE ON {obj_type} {schema}.{obj_name} FROM ROLE {role};"
            else:
                # Schema level privilege
                revoke_sql = f"REVOKE {priv_type} ON SCHEMA {schema} FROM ROLE {role};"

            # Execute SQL
            success = rs.execute_cmd(revoke_sql)

            if success:
                # Remove from privileges list
                self.privileges = [p for p in self.privileges if not (
                    p['schema_name'] == schema_name and
                    p['object_name'] == object_name and
                    p['object_type'] == object_type and
                    p['privilege_type'] == privilege_type
                )]

            return success
        except (ValueError, Exception) as e:
            print(f"Error revoking privilege from {self.role_name}: {e}")
            return False
