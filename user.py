import datetime
import sql_queries as sql
import redshift
from dataclasses import dataclass, field
from typing import Optional


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
    groups:list = field(default_factory=list)
    roles:list = field(default_factory=list)
    
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
        try:
            return cls.map_results(
                        redshift.execute_query(sql.GET_ALL_USERS, session), 
                        ['user_id', 'user_name', 'super_user']
                    )
            
            #     # get user's groups
            #     user.groups = cls.get_user_groups(user.user_id, session)
            #     users.append(user)
            
            # user_roles = cls.get_all_user_roles(session)
            # for user in users:
            #     if user.user_id in user_roles:
            #         user.roles = user_roles[user.user_id]

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

# =================

    # @classmethod
    # def create(cls, username, password, superuser=false, createdb=false, createrole=false, 
    #            inherit=true, login=true, connection_limit=-1, valid_until=none):
    #     """
    #     create a new postgresql user
        
    #     args:
    #         username (str): username
    #         password (str): password
    #         superuser (bool): whether the user is a superuser
    #         createdb (bool): whether the user can create databases
    #         createrole (bool): whether the user can create roles
    #         inherit (bool): whether the user inherits privileges
    #         login (bool): whether the user can login
    #         connection_limit (int): connection limit (-1 for unlimited)
    #         valid_until (str): password expiration date
            
    #     returns:
    #         postgresuser: created user object or none if failed
    #     """
    #     try:
    #         # build the create user sql statement
    #         query = f"create user {username}"
    #         options = []
            
    #         if superuser:
    #             options.append("superuser")
    #         else:
    #             options.append("nosuperuser")
                
    #         if createdb:
    #             options.append("createdb")
    #         else:
    #             options.append("nocreatedb")
                
    #         if createrole:
    #             options.append("createrole")
    #         else:
    #             options.append("nocreaterole")
                
    #         if inherit:
    #             options.append("inherit")
    #         else:
    #             options.append("noinherit")
                
    #         if login:
    #             options.append("login")
    #         else:
    #             options.append("nologin")
                
    #         if connection_limit != -1:
    #             options.append(f"connection limit {connection_limit}")
                
    #         if password:
    #             options.append(f"password '{password}'")
                
    #         if valid_until:
    #             options.append(f"valid until '{valid_until}'")
                
    #         if options:
    #             query += " with " + " ".join(options)
                
    #         # execute the query
    #         databaseconnection.execute_query(query, fetch=false)
            
    #         # return the new user object
    #         return cls(
    #             username=username,
    #             superuser=superuser,
    #             createdb=createdb,
    #             createrole=createrole,
    #             inherit=inherit,
    #             login=login,
    #             connection_limit=connection_limit,
    #             password=password,
    #             valid_until=valid_until
    #         )
    #     except exception as e:
    #         print(f"error creating postgresql user: {e}")
    #         return none
    
    
    # @classmethod
    # def get_by_username(cls, username):
    #     """
    #     get a postgresql user by username
        
    #     args:
    #         username (str): username
            
    #     returns:
    #         postgresuser: user object or none if not found
    #     """
    #     query = """
    #     select 
    #         usename, 
    #         usesuper, 
    #         usecreatedb, 
    #         usecreaterole, 
    #         useinherit, 
    #         uselogin, 
    #         useconnlimit, 
    #         valuntil
    #     from pg_catalog.pg_user
    #     where usename = %s;
    #     """
    #     result = databaseconnection.execute_query(query, (username,))
        
    #     if result and len(result) > 0:
    #         user_data = result[0]
    #         user = cls(
    #             username=user_data[0],
    #             superuser=user_data[1],
    #             createdb=user_data[2],
    #             createrole=user_data[3],
    #             inherit=user_data[4],
    #             login=user_data[5],
    #             connection_limit=user_data[6],
    #             valid_until=user_data[7]
    #         )
            
    #         # get user's groups
    #         user.groups = cls.get_user_groups(user.username)
    #         return user
    #     return none
    
    
    # def update(self, password=none, superuser=none, createdb=none, createrole=none, 
    #            inherit=none, login=none, connection_limit=none, valid_until=none):
    #     """
    #     update postgresql user
        
    #     args:
    #         password (str, optional): new password
    #         superuser (bool, optional): whether the user is a superuser
    #         createdb (bool, optional): whether the user can create databases
    #         createrole (bool, optional): whether the user can create roles
    #         inherit (bool, optional): whether the user inherits privileges
    #         login (bool, optional): whether the user can login
    #         connection_limit (int, optional): connection limit (-1 for unlimited)
    #         valid_until (str, optional): password expiration date
            
    #     returns:
    #         bool: true if successful, false otherwise
    #     """
    #     try:
    #         # build the alter user sql statement
    #         query = f"alter user {self.username}"
    #         options = []
            
    #         if superuser is not none:
    #             options.append("superuser" if superuser else "nosuperuser")
    #             self.superuser = superuser
                
    #         if createdb is not none:
    #             options.append("createdb" if createdb else "nocreatedb")
    #             self.createdb = createdb
                
    #         if createrole is not none:
    #             options.append("createrole" if createrole else "nocreaterole")
    #             self.createrole = createrole
                
    #         if inherit is not none:
    #             options.append("inherit" if inherit else "noinherit")
    #             self.inherit = inherit
                
    #         if login is not none:
    #             options.append("login" if login else "nologin")
    #             self.login = login
                
    #         if connection_limit is not none:
    #             options.append(f"connection limit {connection_limit}")
    #             self.connection_limit = connection_limit
                
    #         if password:
    #             options.append(f"password '{password}'")
    #             self.password = password
                
    #         if valid_until is not none:
    #             if valid_until:
    #                 options.append(f"valid until '{valid_until}'")
    #             else:
    #                 options.append("valid until 'infinity'")
    #             self.valid_until = valid_until
                
    #         if options:
    #             query += " with " + " ".join(options)
                
    #         # execute the query
    #         databaseconnection.execute_query(query, fetch=false)
    #         return true
    #     except exception as e:
    #         print(f"error updating postgresql user: {e}")
    #         return false
    
    # def delete(self):
    #     """
    #     delete a postgresql user
        
    #     returns:
    #         bool: true if successful, false otherwise
    #     """
    #     try:
    #         query = f"drop user {self.username};"
    #         databaseconnection.execute_query(query, fetch=false)
    #         return true
    #     except exception as e:
    #         print(f"error deleting postgresql user: {e}")
    #         return false
    
    # def add_to_group(self, group_name):
    #     """
    #     add user to a group
        
    #     args:
    #         group_name (str): group name
            
    #     returns:
    #         bool: true if successful, false otherwise
    #     """
    #     try:
    #         query = f"alter group {group_name} add user {self.username};"
    #         databaseconnection.execute_query(query, fetch=false)
            
    #         # update the groups list
    #         if group_name not in self.groups:
    #             self.groups.append(group_name)
                
    #         return true
    #     except exception as e:
    #         print(f"error adding user to group: {e}")
    #         return false
    
    # def remove_from_group(self, group_name):
    #     """
    #     remove user from a group
        
    #     args:
    #         group_name (str): group name
            
    #     returns:
    #         bool: true if successful, false otherwise
    #     """
    #     try:
    #         query = f"alter group {group_name} drop user {self.username};"
    #         databaseconnection.execute_query(query, fetch=false)
            
    #         # update the groups list
    #         if group_name in self.groups:
    #             self.groups.remove(group_name)
                
    #         return true
    #     except exception as e:
    #         print(f"error removing user from group: {e}")
    #         return false
