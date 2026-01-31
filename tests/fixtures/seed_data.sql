-- Seed data for Redshift emulator
-- Inserts 20 users, 10 roles, 5 groups, 15 schemas, 200 tables, and privilege grants

-- Insert 20 users (IDs 101-120)
INSERT INTO _pg_users (usesysid, usename, usesuper, usecreatedb, usecanlogin, usecreaterole)
VALUES
    (101, 'user1', FALSE, FALSE, TRUE, FALSE),
    (102, 'user2', FALSE, FALSE, TRUE, FALSE),
    (103, 'user3', FALSE, FALSE, TRUE, FALSE),
    (104, 'user4', FALSE, FALSE, TRUE, FALSE),
    (105, 'user5', FALSE, FALSE, TRUE, FALSE),
    (106, 'user6', FALSE, FALSE, TRUE, FALSE),
    (107, 'user7', FALSE, FALSE, TRUE, FALSE),
    (108, 'user8', FALSE, FALSE, TRUE, FALSE),
    (109, 'user9', FALSE, FALSE, TRUE, FALSE),
    (110, 'user10', FALSE, FALSE, TRUE, FALSE),
    (111, 'user11', FALSE, FALSE, TRUE, FALSE),
    (112, 'user12', FALSE, FALSE, TRUE, FALSE),
    (113, 'user13', FALSE, FALSE, TRUE, FALSE),
    (114, 'user14', FALSE, FALSE, TRUE, FALSE),
    (115, 'user15', FALSE, FALSE, TRUE, FALSE),
    (116, 'user16', FALSE, FALSE, TRUE, FALSE),
    (117, 'user17', FALSE, FALSE, TRUE, FALSE),
    (118, 'user18', FALSE, FALSE, TRUE, FALSE),
    (119, 'user19', FALSE, FALSE, TRUE, FALSE),
    (120, 'user20', FALSE, FALSE, TRUE, FALSE);

-- Insert 10 roles (IDs 201-210)
INSERT INTO _svv_roles (role_id, role_name, super, create_db, create_user)
VALUES
    (201, 'analysts', FALSE, FALSE, FALSE),
    (202, 'engineers', FALSE, FALSE, FALSE),
    (203, 'data_admins', FALSE, FALSE, FALSE),
    (204, 'reporting', FALSE, FALSE, FALSE),
    (205, 'developers', FALSE, FALSE, FALSE),
    (206, 'readonly', FALSE, FALSE, FALSE),
    (207, 'power_users', FALSE, FALSE, FALSE),
    (208, 'etl_role', FALSE, FALSE, FALSE),
    (209, 'finance', FALSE, FALSE, FALSE),
    (210, 'operations', FALSE, FALSE, FALSE);

-- Insert 5 groups (IDs 301-305)
INSERT INTO _pg_groups (grosysid, groname, grolist)
VALUES
    (301, 'group_analytics', ARRAY[101, 102, 103, 104, 105]),
    (302, 'group_engineering', ARRAY[106, 107, 108, 109, 110]),
    (303, 'group_operations', ARRAY[111, 112, 113, 114]),
    (304, 'group_finance', ARRAY[115, 116, 117]),
    (305, 'group_executives', ARRAY[118, 119, 120]);

-- Insert role grants (users assigned to roles)
INSERT INTO _role_grants (role_id, member_id)
VALUES
    (201, 101), (201, 102), (201, 103), (201, 104), (201, 105),
    (202, 106), (202, 107), (202, 108), (202, 109), (202, 110),
    (203, 101), (203, 106), (203, 111),
    (204, 102), (204, 103), (204, 104), (204, 112),
    (205, 107), (205, 108), (205, 109), (205, 113),
    (206, 101), (206, 102), (206, 103), (206, 104), (206, 105), (206, 106),
    (207, 111), (207, 112), (207, 114), (207, 115),
    (208, 113), (208, 114),
    (209, 115), (209, 116), (209, 117),
    (210, 111), (210, 112), (210, 118), (210, 119);

-- Insert user-group memberships
INSERT INTO _user_group_membership (user_id, group_id)
VALUES
    (101, 301), (102, 301), (103, 301), (104, 301), (105, 301),
    (106, 302), (107, 302), (108, 302), (109, 302), (110, 302),
    (111, 303), (112, 303), (113, 303), (114, 303),
    (115, 304), (116, 304), (117, 304),
    (118, 305), (119, 305), (120, 305);

-- Insert additional schemas (IDs 5-19, plus the 4 default)
INSERT INTO _schema_info (schema_id, schema_name, schema_owner)
VALUES
    (5, 'sales', 1),
    (6, 'marketing', 1),
    (7, 'finance_data', 1),
    (8, 'operations', 1),
    (9, 'raw_data', 1),
    (10, 'staging', 1),
    (11, 'analytics', 1),
    (12, 'reporting', 1),
    (13, 'etl', 1),
    (14, 'logs', 1),
    (15, 'audit', 1),
    (16, 'temp', 1),
    (17, 'archive', 1),
    (18, 'backup', 1),
    (19, 'metadata', 1);

-- Insert 200 tables across schemas
-- Each schema gets a mix of tables (public, staging, reporting)
-- Schema 5 (sales): tables 1001-1019 (19 tables)
INSERT INTO _relation_types (relid, relname, relnamespace, relkind, relowner)
SELECT
    1000 + ROW_NUMBER() OVER () as relid,
    'table_' || LPAD(ROW_NUMBER() OVER ()::TEXT, 3, '0') as relname,
    5 as relnamespace,
    'r' as relkind,
    1 as relowner
FROM (SELECT * FROM generate_series(1, 19)) AS t;

-- Schema 6 (marketing): tables 1020-1039 (20 tables)
INSERT INTO _relation_types (relid, relname, relnamespace, relkind, relowner)
SELECT
    1019 + ROW_NUMBER() OVER () as relid,
    'table_' || LPAD((19 + ROW_NUMBER() OVER ())::TEXT, 3, '0') as relname,
    6 as relnamespace,
    'r' as relkind,
    1 as relowner
FROM (SELECT * FROM generate_series(1, 20)) AS t;

-- Schema 7 (finance_data): tables 1040-1064 (25 tables)
INSERT INTO _relation_types (relid, relname, relnamespace, relkind, relowner)
SELECT
    1039 + ROW_NUMBER() OVER () as relid,
    'table_' || LPAD((39 + ROW_NUMBER() OVER ())::TEXT, 3, '0') as relname,
    7 as relnamespace,
    'r' as relkind,
    1 as relowner
FROM (SELECT * FROM generate_series(1, 25)) AS t;

-- Schema 8 (operations): tables 1065-1089 (25 tables)
INSERT INTO _relation_types (relid, relname, relnamespace, relkind, relowner)
SELECT
    1064 + ROW_NUMBER() OVER () as relid,
    'table_' || LPAD((64 + ROW_NUMBER() OVER ())::TEXT, 3, '0') as relname,
    8 as relnamespace,
    'r' as relkind,
    1 as relowner
FROM (SELECT * FROM generate_series(1, 25)) AS t;

-- Schema 9 (raw_data): tables 1090-1124 (35 tables)
INSERT INTO _relation_types (relid, relname, relnamespace, relkind, relowner)
SELECT
    1089 + ROW_NUMBER() OVER () as relid,
    'table_' || LPAD((89 + ROW_NUMBER() OVER ())::TEXT, 3, '0') as relname,
    9 as relnamespace,
    'r' as relkind,
    1 as relowner
FROM (SELECT * FROM generate_series(1, 35)) AS t;

-- Schema 10 (staging): tables 1125-1154 (30 tables)
INSERT INTO _relation_types (relid, relname, relnamespace, relkind, relowner)
SELECT
    1124 + ROW_NUMBER() OVER () as relid,
    'table_' || LPAD((124 + ROW_NUMBER() OVER ())::TEXT, 3, '0') as relname,
    10 as relnamespace,
    'r' as relkind,
    1 as relowner
FROM (SELECT * FROM generate_series(1, 30)) AS t;

-- Schema 11 (analytics): tables 1155-1184 (30 tables)
INSERT INTO _relation_types (relid, relname, relnamespace, relkind, relowner)
SELECT
    1154 + ROW_NUMBER() OVER () as relid,
    'table_' || LPAD((154 + ROW_NUMBER() OVER ())::TEXT, 3, '0') as relname,
    11 as relnamespace,
    'r' as relkind,
    1 as relowner
FROM (SELECT * FROM generate_series(1, 30)) AS t;

-- Schema 12 (reporting): tables 1185-1199 (15 tables)
INSERT INTO _relation_types (relid, relname, relnamespace, relkind, relowner)
SELECT
    1184 + ROW_NUMBER() OVER () as relid,
    'table_' || LPAD((184 + ROW_NUMBER() OVER ())::TEXT, 3, '0') as relname,
    12 as relnamespace,
    'r' as relkind,
    1 as relowner
FROM (SELECT * FROM generate_series(1, 15)) AS t;

-- Schema 13 (etl): tables 1200-1214 (15 tables)
INSERT INTO _relation_types (relid, relname, relnamespace, relkind, relowner)
SELECT
    1199 + ROW_NUMBER() OVER () as relid,
    'table_' || LPAD((199 + ROW_NUMBER() OVER ())::TEXT, 3, '0') as relname,
    13 as relnamespace,
    'r' as relkind,
    1 as relowner
FROM (SELECT * FROM generate_series(1, 15)) AS t;

-- Schemas 14-19 get 5-6 tables each to total 200
-- Schema 14 (logs): 5 tables
INSERT INTO _relation_types (relid, relname, relnamespace, relkind, relowner)
SELECT
    1214 + ROW_NUMBER() OVER () as relid,
    'table_' || LPAD((214 + ROW_NUMBER() OVER ())::TEXT, 3, '0') as relname,
    14 as relnamespace,
    'r' as relkind,
    1 as relowner
FROM (SELECT * FROM generate_series(1, 5)) AS t;

-- Schema 15 (audit): 6 tables
INSERT INTO _relation_types (relid, relname, relnamespace, relkind, relowner)
SELECT
    1219 + ROW_NUMBER() OVER () as relid,
    'table_' || LPAD((219 + ROW_NUMBER() OVER ())::TEXT, 3, '0') as relname,
    15 as relnamespace,
    'r' as relkind,
    1 as relowner
FROM (SELECT * FROM generate_series(1, 6)) AS t;

-- Schema 16 (temp): 5 tables
INSERT INTO _relation_types (relid, relname, relnamespace, relkind, relowner)
SELECT
    1225 + ROW_NUMBER() OVER () as relid,
    'table_' || LPAD((225 + ROW_NUMBER() OVER ())::TEXT, 3, '0') as relname,
    16 as relnamespace,
    'r' as relkind,
    1 as relowner
FROM (SELECT * FROM generate_series(1, 5)) AS t;

-- Schema 17 (archive): 5 tables
INSERT INTO _relation_types (relid, relname, relnamespace, relkind, relowner)
SELECT
    1230 + ROW_NUMBER() OVER () as relid,
    'table_' || LPAD((230 + ROW_NUMBER() OVER ())::TEXT, 3, '0') as relname,
    17 as relnamespace,
    'r' as relkind,
    1 as relowner
FROM (SELECT * FROM generate_series(1, 5)) AS t;

-- Schema 18 (backup): 5 tables
INSERT INTO _relation_types (relid, relname, relnamespace, relkind, relowner)
SELECT
    1235 + ROW_NUMBER() OVER () as relid,
    'table_' || LPAD((235 + ROW_NUMBER() OVER ())::TEXT, 3, '0') as relname,
    18 as relnamespace,
    'r' as relkind,
    1 as relowner
FROM (SELECT * FROM generate_series(1, 5)) AS t;

-- Schema 19 (metadata): 6 tables
INSERT INTO _relation_types (relid, relname, relnamespace, relkind, relowner)
SELECT
    1240 + ROW_NUMBER() OVER () as relid,
    'table_' || LPAD((240 + ROW_NUMBER() OVER ())::TEXT, 3, '0') as relname,
    19 as relnamespace,
    'r' as relkind,
    1 as relowner
FROM (SELECT * FROM generate_series(1, 6)) AS t;

-- Insert privilege grants for tables
-- Each user gets SELECT privilege on some tables, some get INSERT/UPDATE/DELETE
INSERT INTO _svv_relation_privileges (schema_id, schema_name, table_id, table_name, grantee, privilege_type, is_grantable)
SELECT
    si.schema_id,
    si.schema_name,
    rt.relid,
    rt.relname,
    u.usename,
    priv_type.priv,
    FALSE
FROM _schema_info si
JOIN _relation_types rt ON rt.relnamespace = si.schema_id
JOIN _pg_users u ON u.usesysid IN (101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115)
CROSS JOIN (VALUES ('SELECT'), ('INSERT'), ('UPDATE'), ('DELETE')) AS priv_type(priv)
WHERE (u.usesysid + rt.relid) % 3 = 0 OR priv_type.priv = 'SELECT'
LIMIT 200;
