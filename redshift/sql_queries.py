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
                        usename                         AS user_name, 
                        usesysid                        AS user_id,
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
            
GET_ALL_ROLES = """
                    SELECT role_name FROM svv_roles;
                """

# Role queries
GET_ROLE_INFO = """
                    SELECT role_name FROM svv_roles WHERE role_name = %s;
                """

GET_ALL_ROLE_USERS = """
                    SELECT role_name, user_name 
                    FROM svv_user_grants;
                """

GET_ROLE_USERS = """
                    SELECT user_name 
                    FROM svv_user_grants 
                    WHERE role_name = %s;
                """

GET_ALL_ROLE_NESTED_ROLES = """
                    SELECT role_name, granted_role_name 
                    FROM svv_role_grants;
                """

GET_ROLE_NESTED_ROLES = """
                    SELECT granted_role_name 
                    FROM svv_role_grants 
                    WHERE role_name = %s;
                """

GET_ROLE_PRIVILEGES = """
                    SELECT 
                        namespace_name, 
                        relation_name, 
                        relation_type, 
                        privilege_type, 
                        admin_option 
                    FROM svv_relation_privileges 
                    WHERE identity_name = %s AND identity_type = 'role';
                """

GET_ALL_SCHEMAS = """
                    SELECT schema_name 
                    FROM information_schema.schemata 
                    WHERE schema_name NOT LIKE 'pg_%' 
                    AND schema_name NOT LIKE 'information_schema';
                """

GET_SCHEMA_TABLES = """
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = %s 
                    AND table_type = 'BASE TABLE';
                """

GET_SCHEMA_VIEWS = """
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = %s 
                    AND table_type = 'VIEW';
                """

GET_SCHEMA_FUNCTIONS = """
                    SELECT routine_name 
                    FROM information_schema.routines 
                    WHERE routine_schema = %s 
                    AND routine_type = 'FUNCTION';
                """

GET_SCHEMA_PROCEDURES = """
                    SELECT routine_name 
                    FROM information_schema.routines 
                    WHERE routine_schema = %s 
                    AND routine_type = 'PROCEDURE';
                """

# ===== Privileges =====

GET_USER_PRIVILEGES = """
                    SELECT 
                        COALESCE(s.namespace_name, d.schema_name, r.namespace_name) AS schema_name,
                        r.relation_name                                             AS rel_name,
                        s.privilege_type                                            AS schema_priv,
                        d.privilege_type                                            AS default_priv,
                        r.privilege_type                                            AS rel_priv,
                        d.owner_id                                                  AS dpriv_owner_id,
                        d.owner_name                                                AS dpriv_owner_name,
                        COALESCE(s.identity_id, d.grantee_id, r.identity_id)        AS id,
                        COALESCE(s.identity_name, d.grantee_name, r.identity_name)  AS id_name,
                        COALESCE(s.identity_type, d.grantee_type, r.identity_type)  AS id_type,
                        s.admin_option                                              AS schema_admin,
                        d.admin_option                                              AS dpriv_admin,
                        r.admin_option                                              AS rel_admin
                    FROM svv_schema_privileges s
                    FULL OUTER JOIN svv_default_privileges d 
                        ON  d.grantee_id    = s.identity_id
                        AND d.schema_name   = s.namespace_name
                    FULL OUTER JOIN svv_relation_privileges r 
                        ON  r.identity_id   = s.identity_id
                        AND r.namespace_name = s.namespace_name
                    WHERE  s.identity_id    = %s
                        OR d.grantee_id     = %s
                        OR r.identity_id    = %s;
                    """
