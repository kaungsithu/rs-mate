# Static queries

"""_summary_
|     Column name | Data type | Description                                       |
| --------------- | --------- | ------------------------------------------------- |
| usename         | name      | The username.                                     |
| usesysid        | integer   | The user ID.                                      |
| usecreatedb     | boolean   | True if the user can create databases.            |
| usesuper        | boolean   | True if the user is a superuser.                  |
| usecatupd       | boolean   | True if the user can update system catalogs.      |
| passwd          | text      | The password.                                     |
| valuntil        | abstime   | The password's expiration date and time.          |
| useconfig       | text[]    | The session defaults for run-time variables.      |
| useconnlimit    | text      | The number of connections that the user can open. |
|                 |           |                                                   |
"""
GET_ALL_USERS = """
                    SELECT 
                        usesysid                        AS user_id,
                        usename                         AS user_name, 
                        usesuper                        AS super_user, 
                        usecreatedb                     AS can_create_db, 
                        usecatupd                       AS can_update_catalog,
                        valuntil::timestamp::varchar    AS password_expiry,
                        useconfig                       AS session_defaults,
                        useconnlimit                    AS connection_limit
                    FROM pg_user_info
                    ORDER BY usename;
                """


GET_ALL_USER_ROLES = """
                    SELECT 
                        user_id, role_name
                    FROM svv_user_grants;
                """

# Dynamic queries with placeholders
GET_USER_GROUPS = """
                    SELECT 
                        groname AS group_name
                    FROM pg_group
                    WHERE %s = ANY(grolist);
                """

GET_USER_ROLES = """
                    SELECT 
                        role_name
                    FROM svv_user_grants
                    WHERE user_id = %s;
                """

GET_SVV_USER_INFO = """ 
                        SELECT 
                            syslog_access,
                            session_timeout,
                            TO_CHAR(last_ddl_timestamp, 'yyyy-MM-dd HH:mm:ss') AS last_ddl_time
                        FROM SVV_USER_INFO
                        WHERE user_id = %s;
                    """

GET_USER_INFO = """
                    SELECT 
                        usesysid                        AS user_id,
                        usename                         AS user_name, 
                        usesuper                        AS super_user, 
                        usecreatedb                     AS can_create_db, 
                        usecatupd                       AS can_update_catalog,
                        valuntil::timestamp::varchar    AS password_expiry,
                        useconfig                       AS session_defaults,
                        useconnlimit                    AS connection_limit
                    FROM pg_user_info
                    WHERE usesysid = %s;
                """

GET_ALL_GROUPS = """ 
                    SELECT groname AS group_name FROM pg_group;
                """