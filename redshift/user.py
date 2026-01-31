import redshift.sql_queries as sql
from redshift.database import Redshift
from redshift.sanitize import validate_identifier, escape_literal
from dataclasses import dataclass, field
from typing import Optional, List

# TODO: Groups and roles update might be overwriting each other values.
@dataclass
class RedshiftUser:
    user_name: str 
    user_id: int 
    super_user: bool
    can_create_db: bool = False
    can_update_catalog: bool = False
    password_expiry: Optional[str] = None
    session_defaults: Optional[list] = None
    connection_limit: Optional[int] = None
    syslog_access: Optional[str] = None
    session_timeout: Optional[int] = None
    last_ddl_time: Optional[str] = None
    password: Optional[str] = None
    groups: list = field(default_factory=list)
    roles: list = field(default_factory=list)
    privileges: List[dict] = field(default_factory=list)

    def update_fields(self, data: dict):
        if data:
            for key, value in data.items():
                    if hasattr(self, key):
                        setattr(self, key, value) 

    @classmethod
    def map_results(cls, results, column_names) -> 'RedshiftUser':
        return [cls(**dict(zip(column_names, row))) for row in results]

    @classmethod
    def get_all(cls, rs: Redshift) -> list:
        """
        get all redshift users
        
        returns:
            list: list of redshift user objects
        """
        try:
            results = rs.execute_query(sql.GET_ALL_USERS)
            cols = ['user_id', 'user_name', 'super_user', 'can_create_db',
                         'can_update_catalog', 'password_expiry', 
                         'session_defaults', 'connection_limit']

            return cls.map_results(results, cols) if results else []
        except Exception as e: 
            print(e)
            return []

    @classmethod
    def create_user(cls, u: 'RedshiftUser', rs: Redshift) -> bool:
        """Create a new user in Redshift"""
        try:
            # Validate and sanitize inputs
            user_name = validate_identifier(u.user_name)
            password = escape_literal(u.password)

            # Build the CREATE USER SQL statement
            create_sql = f"CREATE USER {user_name} PASSWORD {password}"

            # Add user properties
            create_sql += f" {'' if u.super_user else 'NO'}CREATEUSER"
            create_sql += f" {'' if u.can_create_db else 'NO'}CREATEDB"

            if u.connection_limit and u.connection_limit > 0:
                create_sql += f" CONNECTION LIMIT {u.connection_limit}"

            if u.session_timeout and u.session_timeout > 0:
                create_sql += f" SESSION TIMEOUT {u.session_timeout}"

            if u.syslog_access:
                syslog = validate_identifier(u.syslog_access)
                create_sql += f" SYSLOG ACCESS {syslog}"

            if u.password_expiry:
                expiry = escape_literal(u.password_expiry)
                create_sql += f" VALID UNTIL {expiry}"

            create_sql += ";"

            # Execute the SQL command
            if rs.execute_cmd(create_sql):
                # Get the newly created user to get the user_id
                user = cls.get_user(-1, rs, user_name=u.user_name, all_info=False)
                return user if user else None

            return None
        except (ValueError, Exception) as e:
            print(f"Error creating Redshift user: {e}")
            return None

    @staticmethod
    def get_user_groups(user_id, rs: Redshift):
        'Get all groups a user belongs to.'
        results = rs.execute_query(sql.GET_USER_GROUPS, (user_id,))
        return [g[0] for g in results] if results else []


    @staticmethod
    def get_user_roles(user_id, rs: Redshift):
        'Get all roles a user belongs to'
        results = rs.execute_query(sql.GET_USER_ROLES, (user_id,))
        return [r[0] for r in results] if results else []

    @staticmethod
    def get_user_groups_and_roles_batch(user_id, rs: Redshift) -> tuple:
        """
        Get both groups and roles for a user in a single batch query.

        Args:
            user_id: The user ID
            rs: Redshift connection

        Returns:
            tuple: (groups_list, roles_list)
        """
        try:
            # The combined query uses the user_id parameter 4 times (twice for groups, twice for roles)
            results = rs.execute_query(sql.GET_USER_GROUPS_AND_ROLES, (user_id, user_id, user_id, user_id))
            groups = []
            roles = []

            if results:
                for row in results:
                    # row[0] = user_id, row[1] = type, row[2] = name
                    if row[1] == 'GROUP':
                        groups.append(row[2])
                    elif row[1] == 'ROLE':
                        roles.append(row[2])

            return groups, roles
        except Exception as e:
            print(f"Error getting user groups and roles: {e}")
            return [], []

    @staticmethod
    def get_user_privileges(user_name: str, rs: Redshift) -> list:
        """
        Get all privileges for a specific user (uses batch query for better performance)

        Args:
            user_name: The name of the user
            rs: Redshift connection

        Returns:
            list: List of privilege dictionaries
        """
        try:
            results = rs.execute_query(sql.GET_USER_PRIVILEGES_BATCH, (rs.name, user_name, rs.name, user_name,))
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
            print(f"Error getting privileges for user {user_name}: {e}")
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

    @staticmethod
    def get_svv_user_info(user_id: int, rs: Redshift) -> dict:
        'Get additional user information. Set to user object and return additional as dict.'
        results = rs.execute_query(sql.GET_SVV_USER_INFO, (user_id,))
        cols = ['syslog_access', 'session_timeout', 'last_ddl_time']
        return dict(zip(cols, results[0])) if results else None

    @classmethod
    def get_user(cls, user_id: int, rs: Redshift, user_name: str = None, all_info: bool = True) -> 'RedshiftUser':
        'Get complete user information (optimized with batch queries)'
        query = sql.GET_USER_INFO if user_name is None else sql.GET_USER_INFO_BY_NAME
        param = (user_name,) if user_name is not None else (user_id,)
        results = rs.execute_query(query, param)

        if results:
            user = cls(*results[0])
            if all_info:
                user.update_fields(RedshiftUser.get_svv_user_info(user_id, rs))
                # Use batch query to get both groups and roles in one call
                user.groups, user.roles = RedshiftUser.get_user_groups_and_roles_batch(user_id, rs)

                # Get privileges for this user (using batch query)
                user.privileges = cls.get_user_privileges(user.user_name, rs)

            return user
        return None

    @staticmethod
    def get_alt_user_sql(ori_user, upd_user) -> str:
        """
        Generates an ALTER USER statement based on the differences between original and updated RedshiftUser objects.

        ALTER USER username [ WITH ] option [, ... ]

        where option is

        CREATEDB | NOCREATEDB
        | CREATEUSER | NOCREATEUSER
        | SYSLOG ACCESS { RESTRICTED | UNRESTRICTED }
        | PASSWORD { 'password' | 'md5hash' | DISABLE }
        [ VALID UNTIL 'expiration_date' ]
        | RENAME TO new_name |
        | CONNECTION LIMIT { limit | UNLIMITED }
        | SESSION TIMEOUT limit | RESET SESSION TIMEOUT
        | SET parameter { TO | = } { value | DEFAULT }
        | RESET parameter
        | EXTERNALID external_id

        Args:
            ori_user: The original RedshiftUser object.
            upd_user: The updated RedshiftUser object.

        Returns:
            The ALTER USER SQL statement, or an empty string if no changes are detected.
        """

        if ori_user.user_id != upd_user.user_id:
            raise ValueError("User IDs must match.")

        user_name = validate_identifier(upd_user.user_name)
        alter_statement = f"ALTER USER {user_name}"
        changes = []

        if ori_user.super_user != upd_user.super_user:
            changes.append(f"{'CREATEUSER' if upd_user.super_user else 'NOCREATEUSER'}")

        if ori_user.can_create_db != upd_user.can_create_db:
            changes.append(f"{'CREATEDB' if upd_user.can_create_db else 'NOCREATEDB'}")

        # if ori_user.can_update_catalog != upd_user.can_update_catalog:
        #     changes.append(f"{'UPDATE CATALOG' if upd_user.can_update_catalog else 'NOUPDATECATALOG'}")

        if ori_user.password_expiry != upd_user.password_expiry:
            if upd_user.password_expiry is None or upd_user.password_expiry.strip() == '':
                changes.append("VALID UNTIL 'infinity'")
            else:
                expiry = escape_literal(upd_user.password_expiry.strip())
                changes.append(f"VALID UNTIL {expiry}")

        if ori_user.connection_limit != upd_user.connection_limit:
            if upd_user.connection_limit is None or upd_user.connection_limit == 0:
                changes.append('CONNECTION LIMIT UNLIMITED')
            else:
                changes.append(f"CONNECTION LIMIT {upd_user.connection_limit}")

        if ori_user.syslog_access != upd_user.syslog_access:
            if upd_user.syslog_access is None:
                changes.append('SYSLOG ACCESS RESTRICTED')
            else:
                syslog = validate_identifier(upd_user.syslog_access)
                changes.append(f'SYSLOG ACCESS {syslog}')

        if ori_user.session_timeout != upd_user.session_timeout:
            if upd_user.session_timeout is None or upd_user.session_timeout == 0:
                changes.append('RESET SESSION TIMEOUT')
            else:
                changes.append(f'SESSION TIMEOUT {upd_user.session_timeout}')

        if not changes:
            return ''  # No changes detected

        return alter_statement + ' ' + ' '.join(changes) + ';'


    def update(self, rs: Redshift) -> bool:
        'Update user info in Redshift'
        try:
            ori_user = RedshiftUser.get_user(self.user_id, rs)
            query = RedshiftUser.get_alt_user_sql(ori_user, self)
            return rs.execute_cmd(query)
        except Exception as e:
            print(f"Error updating redshift user: {e}")
            return False

# ===== User Groups ===== 

    @staticmethod
    def get_all_groups(rs: Redshift) -> list:
        'Get all available groups in Redshift'
        try:
            results = rs.execute_query(sql.GET_ALL_GROUPS)
            return [group[0] for group in results] if results else []
        except Exception as e:
            print(e)
            return []

    @staticmethod
    def get_save_groups_sqls(user_name: str, ori_groups: list, upd_groups: list) -> list:
        changes = []
        if ori_groups != upd_groups:
            ori_group_set = set(ori_groups)
            upd_group_set = set(upd_groups)

            added_groups = upd_group_set - ori_group_set
            removed_groups = ori_group_set - upd_group_set

            user = validate_identifier(user_name)
            for group in added_groups:
                group_name = validate_identifier(group)
                changes.append(f'ALTER GROUP {group_name} ADD USER {user};')
            for group in removed_groups:
                group_name = validate_identifier(group)
                changes.append(f'ALTER GROUP {group_name} DROP USER {user};')

            if not changes:
                return None  # No changes detected
            return changes
        
    def save_groups(self, rs: Redshift) -> bool:
        try:
            ori_groups = RedshiftUser.get_user_groups(self.user_id, rs)
            queries = RedshiftUser.get_save_groups_sqls(self.user_name, ori_groups, self.groups)
            return queries is None or all(map(rs.execute_cmd, queries))
        except Exception as e:
            print(f"error updating redshift user groups: {e}")
            return False

# ===== User Roles =====
    @staticmethod
    def get_all_roles(rs: Redshift) -> list:
        'Get all roles available in Redshift'
        try:
            results = rs.execute_query(sql.GET_ALL_ROLES, rs)
            return [role[1] for role in results] if results else []
        except Exception as e:
            print(e)
            return []

    @staticmethod
    def get_save_roles_sqls(user_name: str, ori_roles: list, upd_roles: list) -> list:
        changes = []
        if ori_roles != upd_roles:
            ori_role_set = set(ori_roles)
            upd_role_set = set(upd_roles)

            added_roles = upd_role_set - ori_role_set
            removed_roles = ori_role_set - upd_role_set

            user = validate_identifier(user_name)
            for role in added_roles:
                role_name = validate_identifier(role)
                changes.append(f'GRANT ROLE {role_name} TO {user};')
            for role in removed_roles:
                role_name = validate_identifier(role)
                changes.append(f'REVOKE ROLE {role_name} FROM {user};')

            if not changes:
                return None  # No changes detected
            return changes
        
    def save_roles(self, rs: Redshift) -> bool:
        try:
            ori_roles = RedshiftUser.get_user_roles(self.user_id, rs)
            queries = RedshiftUser.get_save_roles_sqls(self.user_name, ori_roles, self.roles)
            return queries is None or all(map(rs.execute_cmd, queries))
        except Exception as e:
            print(f"error updating redshift user roles: {e}")
            return False
            
    def delete(self, rs: Redshift) -> bool:
        """
        Delete this user from Redshift

        Args:
            rs: Redshift connection

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Validate and sanitize username
            user_name = validate_identifier(self.user_name)

            # Delete user SQL
            delete_sql = f"DROP USER {user_name};"

            # Execute SQL
            return rs.execute_cmd(delete_sql)
        except (ValueError, Exception) as e:
            print(f"Error deleting user {self.user_name}: {e}")
            return False

    # ===== User Privileges =====
    def grant_privilege(self, schema_name: str, object_name: str, object_type: str,
                       privilege_type: str, rs: Redshift) -> bool:
        """
        Grant a privilege to this user

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
            user = validate_identifier(self.user_name)

            # Grant privilege SQL
            if obj_type.upper() in ['TABLE', 'VIEW']:
                grant_sql = f"GRANT {priv_type} ON {schema}.{obj_name} TO {user};"
            elif obj_type.upper() in ['FUNCTION', 'PROCEDURE']:
                grant_sql = f"GRANT EXECUTE ON {obj_type} {schema}.{obj_name} TO {user};"
            else:
                # Schema level privilege
                grant_sql = f"GRANT {priv_type} ON SCHEMA {schema} TO {user};"

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
            print(f"Error granting privilege to {self.user_name}: {e}")
            return False
    
    def revoke_privilege(self, schema_name: str, object_name: str, object_type: str,
                        privilege_type: str, rs: Redshift) -> bool:
        """
        Revoke a privilege from this user

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
            user = validate_identifier(self.user_name)

            # Revoke privilege SQL
            if obj_type.upper() in ['TABLE', 'VIEW']:
                revoke_sql = f"REVOKE {priv_type} ON {schema}.{obj_name} FROM {user};"
            elif obj_type.upper() in ['FUNCTION', 'PROCEDURE']:
                revoke_sql = f"REVOKE EXECUTE ON {obj_type} {schema}.{obj_name} FROM {user};"
            else:
                # Schema level privilege
                revoke_sql = f"REVOKE {priv_type} ON SCHEMA {schema} FROM {user};"

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
            print(f"Error revoking privilege from {self.user_name}: {e}")
            return False
