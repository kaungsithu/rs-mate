import redshift.sql_queries as sql
from redshift.database import Redshift
from dataclasses import dataclass, field
from typing import Optional

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
    groups: list = field(default_factory=list)
    roles: list = field(default_factory=list)

    def update_fields(self, data: dict):
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

    # @staticmethod
    # def get_all_user_roles(session):
    #     'Get all roles in Redshift'
    #     query = sql.GET_ALL_USER_ROLES
    #     results = redshift.execute_query(query, session)
        
    #     user_roles = {}
    #     for user_role in results:
    #         if user_role[0] not in user_roles:
    #             user_roles[user_role[0]] = []
    #         user_roles[user_role[0]].append(user_role[1])
    #     return user_roles

    @staticmethod
    def get_svv_user_info(user_id: int, rs: Redshift) -> dict:
        'Get additional user information. Set to user object and return additional as dict.'
        results = rs.execute_query(sql.GET_SVV_USER_INFO, (user_id,))
        cols = ['syslog_access', 'session_timeout', 'last_ddl_time']
        
        if results:
            return dict(zip(cols, results[0]))
        else:
            return dict(zip(cols, (None)*3))

    @classmethod
    def get_user(cls, user_id: int, rs: Redshift) -> 'RedshiftUser':
        'Get complete user information'
        results = rs.execute_query(sql.GET_USER_INFO, (user_id,))

        if results:
            user = cls(*results[0])
            user.update_fields(RedshiftUser.get_svv_user_info(user_id, rs))
            user.groups = RedshiftUser.get_user_groups(user_id, rs)
            user.roles = RedshiftUser.get_user_roles(user_id, rs)
        
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

        alter_statement = f"ALTER USER {upd_user.user_name}"
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
                changes.append(f"VALID UNTIL '{upd_user.password_expiry.strip()}'")

        if ori_user.connection_limit != upd_user.connection_limit:
            if upd_user.connection_limit is None or upd_user.connection_limit == 0:
                changes.append('CONNECTION LIMIT UNLIMITED')
            else:
                changes.append(f"CONNECTION LIMIT {upd_user.connection_limit}")

        if ori_user.syslog_access != upd_user.syslog_access:
            if upd_user.syslog_access is None:
                changes.append('SYSLOG ACCESS RESTRICTED')
            else:
                changes.append(f'SYSLOG ACCESS {upd_user.syslog_access}')

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

            for group in added_groups:
                changes.append(f'ALTER GROUP {group} ADD USER {user_name};')
            for group in removed_groups:
                changes.append(f'ALTER GROUP {group} DROP USER {user_name};')

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
            return [role[0] for role in results] if results else []
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

            for role in added_roles:
                changes.append(f'GRANT ROLE {role} TO {user_name};')
            for role in removed_roles:
                changes.append(f'REVOKE ROLE {role} FROM {user_name};')

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