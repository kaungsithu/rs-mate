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
                        usename                 AS user_name, 
                        usesysid                AS user_id,
                        usecreatedb             AS can_create_db, 
                        usesuper                AS super_user, 
                        usecatupd               AS can_update_catalog,
                        valuntil                AS password_expiry,
                        useconfig               AS session_defaults,
                        useconnlimit            AS connection_limit
                    FROM pg_user_info
                    ORDER BY usename;
                """

# Dynamic queries with placeholders
GET_USER_GROUPS = """
                    SELECT 
                        groname AS group_name
                    FROM pg_group
                    WHERE %s = ANY(grolist)
                """