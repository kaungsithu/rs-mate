import sql_queries as sql
import redshift
from dataclasses import dataclass, field
from typing import Optional

# TODO: Not to bring in session here, but to take only what is needed.
@dataclass
class RedshiftUser:
    user_name:str 
    user_id:int 
    super_user:bool
    can_create_db:bool = False
    can_update_catalog:bool = False
    password_expiry:Optional[str] = None
    session_defaults:Optional[list] = None
    connection_limit:Optional[int] = None
    syslog_access:Optional[str] = None
    session_timeout:Optional[int] = None
    last_ddl_time:Optional[str] = None
    groups:list = field(default_factory=list)
    roles:list = field(default_factory=list)

    def update_fields(self, data:dict):
       for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value) 

    @classmethod
    def map_results(cls, results, column_names):
        return [cls(**dict(zip(column_names, row))) for row in results]

    @classmethod
    def get_all(cls, session):
        """
        get all redshift users
        
        returns:
            list: list of redshift user objects
        """
        print(session)
        try:
            results = redshift.execute_query(sql.GET_ALL_USERS, session)
            cols = ['user_id', 'user_name', 'super_user', 'can_create_db',
                         'can_update_catalog', 'password_expiry', 
                         'session_defaults', 'connection_limit']

            return cls.map_results(results, cols) if results else []
        except Exception as e: 
            print(e)
            return []

    @staticmethod
    def get_user_groups(user_id, session):
        """
        get all groups a user belongs to
        
        args:
            username (str): username
            
        returns:
            list: list of group names
        """
        query = sql.GET_USER_GROUPS
        results = redshift.execute_query(query, session, (user_id,))
        
        groups = []
        for group_data in results:
            groups.append(group_data[0])
        return groups

    @staticmethod
    def get_user_roles(user_id, session):
        """
        get all roles a user belongs to
        
        args:
            username (str): username
            
        returns:
            list: list of role names
        """
        query = sql.GET_USER_ROLES
        results = redshift.execute_query(query, session, (user_id,))
        
        roles = []
        for role_name in results:
            roles.append(role_name[0])
        return roles

    @staticmethod
    def get_all_user_roles(session):
        """
        get all roles
        
        args:
            username (str): username
            
        returns:
            dict: dictionary of user id and role names
        """
        query = sql.GET_ALL_USER_ROLES
        results = redshift.execute_query(query, session)
        
        user_roles = {}
        for user_role in results:
            if user_role[0] not in user_roles:
                user_roles[user_role[0]] = []
            user_roles[user_role[0]].append(user_role[1])
        return user_roles

    @staticmethod
    def get_svv_user_info(user_id, session):
        """
        get user information
        
        args:
            user_id (int): user id
            
        returns:
            dict: user information
        """
        query = sql.GET_SVV_USER_INFO
        results = redshift.execute_query(query, session, (user_id,))
        
        if results:
            return {
                'syslog_access': results[0][0],
                'session_timeout': results[0][1],
                'last_ddl_time': results[0][2]
            }
        return {'syslog_access': None, 'session_timeout': None, 'last_ddl_time': None}

    @staticmethod
    def get_user(user_id:int, session:any):
        """
        get user information
        
        args:
            user_id (int): user id
            
        returns:
            dict: user information
        """
        query = sql.GET_USER_INFO
        results = redshift.execute_query(query, session, (user_id,))

        if results:
            user = RedshiftUser(*results[0])
            user.update_fields(RedshiftUser.get_svv_user_info(user_id, session))
            user.groups = RedshiftUser.get_user_groups(user_id, session)
            user.roles = RedshiftUser.get_user_roles(user_id, session)
        
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

        # if ori_user.groups != upd_user.groups:
        #     original_groups_set = set(ori_user.groups)
        #     updated_groups_set = set(upd_user.groups)

        #     added_groups = updated_groups_set - original_groups_set
        #     removed_groups = original_groups_set - updated_groups_set

        #     for group in added_groups:
        #         changes.append(f"ADD GROUP {group}")
        #     for group in removed_groups:
        #         changes.append(f"REMOVE GROUP {group}")

        # if ori_user.roles != upd_user.roles:
        #     original_roles_set = set(ori_user.roles)
        #     updated_roles_set = set(upd_user.roles)

        #     added_roles = updated_roles_set - original_roles_set
        #     removed_roles = original_roles_set - updated_roles_set

        #     for role in added_roles:
        #         changes.append(f"ADD ROLE {role}")
        #     for role in removed_roles:
        #         changes.append(f"REMOVE ROLE {role}")

        if not changes:
            return ""  # No changes detected

        return alter_statement + " " + " ".join(changes) + ";"


    def update(self, ori_user, session):
        """
        update redshift user
        
        args:
            session (sqlalchemy session): database session
        
        returns:
            bool: true if successful, false otherwise
        """
        try:
            query:str = RedshiftUser.get_alt_user_sql(ori_user, self)
            result = redshift.execute_query(query, session, fetch=False)
            return True if result else False
        except Exception as e:
            print(f"error updating redshift user: {e}")
            return False

    @staticmethod
    def get_all_groups(session):
        try:
            results = redshift.execute_query(sql.GET_ALL_GROUPS, session)
            return [group[0] for group in results] if results else []
        except Exception as e:
            print(e)
            return []