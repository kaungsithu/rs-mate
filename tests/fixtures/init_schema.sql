-- Redshift Emulator Schema for Local Testing
-- This file creates system catalog views and tables that mimic Redshift's structure

-- Create custom data types and functions that Redshift uses
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create pg_user_info view (mimics Redshift's pg_user_info system view)
CREATE TABLE _pg_users (
    usesysid INTEGER PRIMARY KEY,
    usename TEXT NOT NULL UNIQUE,
    usesuper BOOLEAN NOT NULL DEFAULT FALSE,
    usecreatedb BOOLEAN NOT NULL DEFAULT FALSE,
    usecanlogin BOOLEAN NOT NULL DEFAULT TRUE,
    usecreaterole BOOLEAN NOT NULL DEFAULT FALSE,
    valuntil TIMESTAMP WITHOUT TIME ZONE,
    useconfig TEXT[]
);

CREATE VIEW pg_user_info AS
    SELECT usesysid, usename, usesuper, usecreatedb, usecanlogin, usecreaterole, valuntil, useconfig
    FROM _pg_users
    ORDER BY usesysid;

-- Create svv_roles view (mimics Redshift's role system view)
CREATE TABLE _svv_roles (
    role_id INTEGER PRIMARY KEY,
    role_name TEXT NOT NULL UNIQUE,
    super BOOLEAN NOT NULL DEFAULT FALSE,
    create_db BOOLEAN NOT NULL DEFAULT FALSE,
    create_user BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE VIEW svv_roles AS
    SELECT role_id, role_name, super, create_db, create_user
    FROM _svv_roles
    ORDER BY role_id;

-- Create pg_group view (mimics Redshift's group system)
CREATE TABLE _pg_groups (
    grosysid INTEGER PRIMARY KEY,
    groname TEXT NOT NULL UNIQUE,
    grolist INTEGER[] DEFAULT ARRAY[]::INTEGER[]
);

CREATE VIEW pg_group AS
    SELECT grosysid, groname, grolist
    FROM _pg_groups
    ORDER BY grosysid;

-- Create role_grants table (tracks role membership)
CREATE TABLE _role_grants (
    role_id INTEGER NOT NULL,
    member_id INTEGER NOT NULL,
    PRIMARY KEY (role_id, member_id),
    FOREIGN KEY (role_id) REFERENCES _svv_roles(role_id) ON DELETE CASCADE,
    FOREIGN KEY (member_id) REFERENCES _pg_users(usesysid) ON DELETE CASCADE
);

-- Create user_group_membership table
CREATE TABLE _user_group_membership (
    user_id INTEGER NOT NULL,
    group_id INTEGER NOT NULL,
    PRIMARY KEY (user_id, group_id),
    FOREIGN KEY (user_id) REFERENCES _pg_users(usesysid) ON DELETE CASCADE,
    FOREIGN KEY (group_id) REFERENCES _pg_groups(grosysid) ON DELETE CASCADE
);

-- Create svv_role_grants view
CREATE VIEW svv_role_grants AS
    SELECT rg.role_id, rg.member_id, u.usename as member_name, r.role_name
    FROM _role_grants rg
    JOIN _pg_users u ON u.usesysid = rg.member_id
    JOIN _svv_roles r ON r.role_id = rg.role_id;

-- Create svv_user_grants view (users granted to roles)
CREATE VIEW svv_user_grants AS
    SELECT rg.role_id, rg.member_id as user_id, u.usename, r.role_name
    FROM _role_grants rg
    JOIN _pg_users u ON u.usesysid = rg.member_id
    JOIN _svv_roles r ON r.role_id = rg.role_id;

-- Create schemas and schema information
CREATE TABLE _schema_info (
    schema_id INTEGER PRIMARY KEY,
    schema_name TEXT NOT NULL UNIQUE,
    schema_owner INTEGER NOT NULL REFERENCES _pg_users(usesysid)
);

-- Create relation types table (tables, views, functions, procedures)
CREATE TABLE _relation_types (
    relid INTEGER PRIMARY KEY,
    relname TEXT NOT NULL,
    relnamespace INTEGER NOT NULL REFERENCES _schema_info(schema_id),
    relkind CHAR(1) NOT NULL,  -- r=table, v=view, f=foreign table, c=composite, m=materialized view, p=partitioned
    relowner INTEGER NOT NULL REFERENCES _pg_users(usesysid)
);

-- Create privilege information table
CREATE TABLE _svv_relation_privileges (
    schema_id INTEGER NOT NULL,
    schema_name TEXT NOT NULL,
    table_id INTEGER NOT NULL,
    table_name TEXT NOT NULL,
    grantee TEXT NOT NULL,
    privilege_type TEXT NOT NULL,
    is_grantable BOOLEAN NOT NULL DEFAULT FALSE,
    PRIMARY KEY (schema_id, table_id, grantee, privilege_type)
);

CREATE VIEW svv_relation_privileges AS
    SELECT schema_id, schema_name, table_id, table_name, grantee, privilege_type, is_grantable
    FROM _svv_relation_privileges;

-- Create user grants view (role/user privilege grants)
CREATE TABLE _user_grants (
    privilege_type TEXT NOT NULL,
    principal_id INTEGER NOT NULL,
    principal_name TEXT NOT NULL,
    object_type TEXT NOT NULL,
    object_id INTEGER NOT NULL,
    object_name TEXT NOT NULL,
    schema_id INTEGER,
    schema_name TEXT,
    PRIMARY KEY (principal_id, object_id, privilege_type)
);

CREATE VIEW svv_user_grants_view AS
    SELECT privilege_type, principal_id, principal_name, object_type, object_id, object_name, schema_id, schema_name
    FROM _user_grants;

-- Ensure system user (ID 1) exists
INSERT INTO _pg_users (usesysid, usename, usesuper, usecreatedb, usecanlogin, usecreaterole)
VALUES (1, 'admin', true, true, true, true)
ON CONFLICT DO NOTHING;

-- Create default schemas
INSERT INTO _schema_info (schema_id, schema_name, schema_owner)
VALUES
    (1, 'public', 1),
    (2, 'pg_internal', 1),
    (3, 'pg_catalog', 1),
    (4, 'information_schema', 1)
ON CONFLICT DO NOTHING;
