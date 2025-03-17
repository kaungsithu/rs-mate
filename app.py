from fasthtml.common import *
from fasthtml.common import CheckboxX as fhCheckboxX
from requests import session
from redshift.database import Redshift
from redshift.user import RedshiftUser
from redshift.role import RedshiftRole
from redshift import sql_queries as sql
from helpers.session_helper import *
from monsterui.all import *
import json
from components import *

# listjs
listjs = Script(src='https://cdnjs.cloudflare.com/ajax/libs/list.js/2.3.1/list.min.js')
hdrs = (Theme.violet.headers(mode='light'), listjs)
app, rt = fast_app(hdrs=hdrs, debug=True, live=True)
setup_toasts(app)

# Helper function to store role in session
def set_role(session, role: RedshiftRole):
    sess_store_obj(session, 'rsrole', role)

# Helper function to get role from session
def get_role(session) -> RedshiftRole:
    return sess_get_obj(session, 'rsrole')

# Home, DB info form
@rt('/')
def get(session):
    session.clear()
    return MainLayout(mk_db_frm(), nav_btns=False)

# Connect to Redshift, show Nav, User Table
@rt('/')
def post(session, rs: Redshift):
    session.clear()
    if not (rs.host and rs.port and rs.name and rs.user and rs.pwd):
        add_toast(session, 'All connection fields are required!', 'error', True)
        return RedirectResponse('/', status_code=303)

    if not rs.test_conn():
        add_toast(session, 'There was a problem connecting to Redshift!', 'error', True)
        return RedirectResponse('/', status_code=303)

    set_rs(session, rs)
    session['active_btn'] = 'users'

    return RedirectResponse('/users', status_code=303)
    # return Div(
    #     mk_nav_bar(session),
    #     Div(mk_user_table(session), id='content-area'),
    # )


@rt('/user-groups/{user_id}')
def get(session, user_id: int):
    groups = RedshiftUser.get_user_groups(user_id, get_rs(session))
    return BadgeList(groups) if groups else '-'

# Get user roles for each user
@rt('/user-roles/{user_id}')
def get(session, user_id: int):
    roles = RedshiftUser.get_user_roles(user_id, get_rs(session))
    return BadgeList(roles) if roles else '-'



@rt('/users')
def get(session):
    users = RedshiftUser.get_all(get_rs(session))
    return MainLayout(mk_user_table(users))


# ===== User Groups =====
@rt('/user/add-group')
def post(session, frm_data: dict):
    user = get_user(session)
    # TODO: group_select returning a list with two values. 1st always 1st option, 2nd is selected val.
    group_name = frm_data['ugroup-select'][1] if frm_data['ugroup-select'] else None
    if group_name: user.groups = set(user.groups) | set([group_name])
    set_user(session, user)
    ls_id = frm_data['group_list_id']
    return RemovableList(user.groups, id=ls_id, 
                         hx_post='/user/remove-group', hx_target=f'#{ls_id}')
    # return mk_user_groups(session, user)

@rt('/user/remove-group')
def post(session, frm_data: dict):
    user = get_user(session)
    user.groups = set(user.groups) - set(frm_data.keys())
    set_user(session, user)
    ls_id = frm_data['group_list_id']
    return RemovableList(user.groups, id=ls_id, 
                         hx_post='/user/remove-group', hx_target=f'#{ls_id}')
    # return mk_user_groups(session, user)

@rt('/user/save-groups')
def post(session, user: RedshiftUser):
    user = get_user(session)
    if user.save_groups(get_rs(session)):
        add_toast(session, 'User groups saved successfully!', 'success', True)
    else:
        add_toast(session, 'Error saving user groups!', 'error', True)
    return None

# ===== User Roles =====
@rt('/user/add-role')
def post(session, frm_data: dict):
    user = get_user(session)
    # TODO: role_select returning a list with two values. 1st always 1st option, 2nd is selected val.
    role_name = frm_data['urole-select'][1] if frm_data['urole-select'] else None
    if role_name: user.roles = set(user.roles) | set([role_name])
    set_user(session, user)
    ls_id = frm_data['role_list_id']
    return RemovableList(user.roles, id=ls_id, 
                         hx_post='/user/remove-role', hx_target=f'#{ls_id}')

@rt('/user/remove-role')
def post(session, frm_data: dict):
    user = get_user(session)
    user.roles = set(user.roles) - set(frm_data.keys())
    set_user(session, user)
    ls_id = frm_data['role_list_id']
    return RemovableList(user.roles, id=ls_id, 
                         hx_post='/user/remove-role', hx_target=f'#{ls_id}')

@rt('/user/save-roles')
def post(session, user: RedshiftUser):
    user = get_user(session)
    if user.save_roles(get_rs(session)):
        set_user(session, user)
        add_toast(session, 'User roles saved successfully!', 'success', True)
    else:
        add_toast(session, 'Error saving user roles!', 'error', True)
    return None

# Show user details
@rt('/user/{user_id}')
def get(session, user_id: int):
    try:
        rs = get_rs(session)
        user = RedshiftUser.get_user(user_id, rs)
        all_groups = RedshiftUser.get_all_groups(rs)
        all_roles = RedshiftUser.get_all_roles(rs)
        if user:
            set_user(session, user)
            return MainLayout(mk_user_form(user, all_groups, all_roles), active_btn='users')
        else:
            add_toast(session, f'User with ID: {user_id} not found', 'error', True)
            return RedirectResponse('/users')
    except Exception as e:
        add_toast(session, f'Error retrieving user with ID: {user_id}', 'error', True)
        return RedirectResponse('/users')

@rt('/user/create')
def post(session, user: RedshiftUser):
    # Create the user in Redshift
    rs = get_rs(session)
    try:
        nu = RedshiftUser.create_user(user, rs=rs) # new user
        
        if nu:
            add_toast(session, f'User {user.user_name} created successfully!', 'success', True)
            # Redirect to the user detail page for further configuration
            return RedirectResponse(url=f'/user/{nu.user_id}', status_code=303)
        else:
            add_toast(session, f'Error creating or unable to verify creating user {user.user_name}!', 'error', True)
            return RedirectResponse(url='/users', status_code=303)
    except Exception as e:
        add_toast(session, f'Error creating user: {str(e)}', 'error', True)
        return RedirectResponse(url='/users', status_code=303)

@rt('/user/save-props')
def post(session, user: RedshiftUser):
    if user.update(get_rs(session)):
        add_toast(session, f'User: {user.user_name} saved successfully!', 'success', True)
    else:
        add_toast(session, f'Error saving user: {user.user_name}!', 'error', True)
    return mk_user_props(session, user)

# ===== Roles =====
@rt('/roles')
def get(session):
    roles = RedshiftRole.get_all(get_rs(session))
    return MainLayout(mk_role_table(roles), active_btn='roles')

# Get role users for each role
@rt('/role-users/{role_name}')
def get(session, role_name: str):
    users = RedshiftRole.get_role_users(role_name, get_rs(session))
    return BadgeList(users) if users else '-'

# Get nested roles for each role
@rt('/role-nested-roles/{role_name}')
def get(session, role_name: str):
    nested_roles = RedshiftRole.get_role_nested_roles(role_name, get_rs(session))
    return BadgeList(nested_roles) if nested_roles else '-'

# Show role details
@rt('/role/{role_name}')
def get(session, role_name: str):
    try:
        rs = get_rs(session)
        role = RedshiftRole.get_role(role_name, rs)
        all_roles = RedshiftRole.get_all(rs)
        
        # Get all schemas
        schemas = rs.get_all_schemas()
        session['schemas'] = schemas
        
        # Fetch all relations for all schemas
        schema_relations = {}
        for schema in schemas:
            schema_relations[schema] = {
                'tables': [],
                'views': [],
                'functions': [],
                'procedures': []
            }
            
            # Get tables for the schema
            schema_relations[schema]['tables'] = rs.get_schema_tables(schema)
            
            # Get views for the schema
            schema_relations[schema]['views'] = rs.get_schema_views(schema)
            
            # Get functions for the schema
            schema_relations[schema]['functions'] = rs.get_schema_functions(schema)

            # Get procedures for the schema
            schema_relations[schema]['procedures'] = rs.get_schema_procedures(schema)
        
        if role:
            set_role(session, role)
            # Store schema relations in session
            session['schema_relations'] = schema_relations
            return MainLayout(mk_role_form(role, all_roles, schemas, schema_relations), active_btn='roles')
        else:
            add_toast(session, f'Role with name: {role_name} not found', 'error', True)
            return RedirectResponse('/roles')
    except Exception as e:
        add_toast(session, f'Error retrieving role with name: {role_name}: {str(e)}', 'error', True)
        return RedirectResponse('/roles')

# Delete role
@rt('/role/{role_name}')
def delete(session, role_name: str):
    try:
        rs = get_rs(session)
        role = RedshiftRole.get_role(role_name, rs)
        
        if not role:
            add_toast(session, f'Role with name: {role_name} not found', 'error', True)
            return None
            
        # Check if role has users
        if role.users:
            add_toast(session, f'Cannot delete role {role_name} because it is granted to users', 'error', True)
            return None
            
        # Delete role
        if role.delete(rs):
            add_toast(session, f'Role {role_name} deleted successfully', 'success', True)
            return None
        else:
            add_toast(session, f'Error deleting role {role_name}', 'error', True)
            return None
    except Exception as e:
        add_toast(session, f'Error deleting role {role_name}: {str(e)}', 'error', True)
        return None

# Create role
@rt('/role/create')
def post(session, frm_data: dict):
    role_name = frm_data.get('role_name')
    
    if not role_name:
        add_toast(session, 'Role name is required!', 'error', True)
        return RedirectResponse('/roles', status_code=303)
    
    # Create the role in Redshift
    rs = get_rs(session)
    try:
        role = RedshiftRole.create_role(role_name, rs)
        
        if role:
            add_toast(session, f'Role {role_name} created successfully!', 'success', True)
            # Redirect to the role detail page for further configuration
            return RedirectResponse(url=f'/role/{role.role_name}', status_code=303)
        else:
            add_toast(session, f'Error creating role {role_name}!', 'error', True)
            return RedirectResponse(url='/roles', status_code=303)
    except Exception as e:
        add_toast(session, f'Error creating role: {str(e)}', 'error', True)
        return RedirectResponse(url='/roles', status_code=303)

# ===== Role Nested Roles =====
@rt('/role/add-nested-role')
def post(session, frm_data: dict):
    role = get_role(session)
    # TODO: nested-role-select returning a list with two values. 1st always 1st option, 2nd is selected val.
    nested_role_name = frm_data['nested-role-select'][1] if frm_data['nested-role-select'] else None
    if nested_role_name: role.nested_roles = set(role.nested_roles) | set([nested_role_name])
    set_role(session, role)
    ls_id = frm_data['nested_role_list_id']
    return RemovableList(role.nested_roles, id=ls_id, 
                         hx_post='/role/remove-nested-role', hx_target=f'#{ls_id}')

@rt('/role/remove-nested-role')
def post(session, frm_data: dict):
    role = get_role(session)
    role.nested_roles = set(role.nested_roles) - set(frm_data.keys())
    set_role(session, role)
    ls_id = frm_data['nested_role_list_id']
    return RemovableList(role.nested_roles, id=ls_id, 
                         hx_post='/role/remove-nested-role', hx_target=f'#{ls_id}')

@rt('/role/save-nested-roles')
def post(session, role: RedshiftRole):
    role = get_role(session)
    if role.update_nested_roles(role.nested_roles, get_rs(session)):
        add_toast(session, 'Nested roles saved successfully!', 'success', True)
    else:
        add_toast(session, 'Error saving nested roles!', 'error', True)
    return None

# ===== Role Privileges =====
@rt('/role/get-schema-tables/{schema_name}')
def get(session, schema_name: str):
    rs = get_rs(session)
    
    # Get tables for the schema
    tables_result = rs.execute_query(sql.GET_SCHEMA_TABLES, (schema_name,))
    tables = [row[0] for row in tables_result] if tables_result else []
    
    # Return options for select
    options = SelectOptions(tables)
    return ''.join([str(option) for option in options])

@rt('/role/get-schema-views/{schema_name}')
def get(session, schema_name: str):
    rs = get_rs(session)
    
    # Get views for the schema
    views_result = rs.execute_query(sql.GET_SCHEMA_VIEWS, (schema_name,))
    views = [row[0] for row in views_result] if views_result else []
    
    # Return options for select
    options = SelectOptions(views)
    return ''.join([str(option) for option in options])

@rt('/role/get-schema-functions/{schema_name}')
def get(session, schema_name: str, frm_data: dict):
    rs = get_rs(session)
    func_type = frm_data.get('new-func-type-' + schema_name)
    
    if func_type == 'FUNCTION':
        # Get functions for the schema
        funcs_result = rs.execute_query(sql.GET_SCHEMA_FUNCTIONS, (schema_name,))
        funcs = [row[0] for row in funcs_result] if funcs_result else []
    else:
        # Get procedures for the schema
        funcs_result = rs.execute_query(sql.GET_SCHEMA_PROCEDURES, (schema_name,))
        funcs = [row[0] for row in funcs_result] if funcs_result else []
    
    # Return options for select
    options = SelectOptions(funcs)
    return ''.join([str(option) for option in options])


@rt('/role/load-table/{schema_name}')
def post(schema_name: str, frm_data: dict):
    # Get table name from form data
    table_name = frm_data.get('new-table-' + schema_name)
    table_name = table_name[1] if isinstance(table_name, list) else table_name
    if not table_name:
        return None
    
    # Create privilege checkboxes for the table
    # TODO: Table added even if the table is existing. To check if the table exists before adding.
    return Tr(
                Td(table_name),
                Td(fhCheckboxX(id=f'priv-{schema_name}-{table_name}-SELECT', cls='uk-checkbox')),
                Td(fhCheckboxX(id=f'priv-{schema_name}-{table_name}-INSERT', cls='uk-checkbox')),
                Td(fhCheckboxX(id=f'priv-{schema_name}-{table_name}-UPDATE', cls='uk-checkbox')),
                Td(fhCheckboxX(id=f'priv-{schema_name}-{table_name}-DELETE', cls='uk-checkbox')),
            )

@rt('/role/load-view/{schema_name}')
def post(schema_name: str, frm_data: dict):
    # Get view name from form data
    view_name = frm_data.get('new-view-' + schema_name)
    view_name = view_name[1] if isinstance(view_name, list) else view_name
    if not view_name:
        return None
    
    # Create privilege checkboxes for the view
    # TODO: View added even if the table is existing. To check if the table exists before adding.
    return Tr(
                Td(view_name),
                Td(fhCheckboxX(id=f'priv-{schema_name}-{view_name}-SELECT', cls='uk-checkbox')),
                Td(fhCheckboxX(id=f'priv-{schema_name}-{view_name}-INSERT', cls='uk-checkbox')),
                Td(fhCheckboxX(id=f'priv-{schema_name}-{view_name}-UPDATE', cls='uk-checkbox')),
                Td(fhCheckboxX(id=f'priv-{schema_name}-{view_name}-DELETE', cls='uk-checkbox')),
            )

@rt('/role/load-function/{schema_name}')
def get(schema_name: str, frm_data: dict):
    # Get function, procedure name from form data
    func = frm_data.get('new-func-' + schema_name)
    func = func[1] if isinstance(func, list) else func
    if not func:
        return None
    
    # Create privilege checkboxes for the function
    # TODO: Function added even if the function is existing. To check if the function exists before adding.
    func_type = func.split(':')[0]
    func_name = func.split(':')[1]
    return Tr(
                Td(func_type),
                Td(func_name),
                Td(fhCheckboxX(id=f'priv-{schema_name}-{func_name}-EXECUTE', cls='uk-checkbox')),
            )

@rt('/role/save-privileges')
def post(session, frm_data: dict):
    role = get_role(session)
    rs = get_rs(session)
    
    # Process form data to extract privileges
    privileges = []
    for key, value in frm_data.items():
        if key.startswith('priv-') and (isinstance(value, list) and '1' in value):
            # Format: priv-{schema}-{object}-{privilege}
            parts = key.split('-')
            if len(parts) == 4:
                schema_name = parts[1]
                object_name = parts[2]
                privilege_type = parts[3]
                
                # Determine object type based on privilege
                if privilege_type == 'EXECUTE':
                    # Check if it's a function or procedure
                    # This is a simplification - in a real implementation, you'd need to check the actual type
                    object_type = frm_data.get(f'new-func-type-{schema_name}', 'FUNCTION')
                else:
                    # For SELECT, INSERT, UPDATE, DELETE - could be TABLE or VIEW
                    # For simplicity, assume it's a TABLE if it has INSERT, UPDATE, or DELETE privileges
                    if privilege_type in ['INSERT', 'UPDATE', 'DELETE']:
                        object_type = 'TABLE'
                    else:
                        # For SELECT only, check if it's in the views list
                        views = rs.get_schema_views(schema_name)
                        object_type = 'VIEW' if object_name in views else 'TABLE'
                
                privileges.append({
                    'schema_name': schema_name,
                    'object_name': object_name,
                    'object_type': object_type,
                    'privilege_type': privilege_type
                })
    
    # Grant privileges
    success = True
    for privilege in privileges:
        if not role.grant_privilege(
            privilege['schema_name'],
            privilege['object_name'],
            privilege['object_type'],
            privilege['privilege_type'],
            rs
        ):
            success = False
    
    if success:
        # Refresh role privileges
        updated_role = RedshiftRole.get_role(role.role_name, rs)
        if updated_role:
            set_role(session, updated_role)
        add_toast(session, 'Privileges saved successfully!', 'success', True)
    else:
        add_toast(session, 'Error saving some privileges!', 'warning', True)
    
    return None

# ===== Role Schema Content =====
@rt('/role/schema-nav/{schema_name}')
def get(session, schema_name: str):
    schemas = session.get('schemas', get_rs(session).get_all_schemas())
    return mk_schema_nav(schemas, schema_name)

@rt('/role/schema-content/{role_name}/{schema_name}')
def get(session, role_name: str, schema_name: str):
    try:
        rs = get_rs(session)
        role = RedshiftRole.get_role(role_name, rs)
        schema_relations = session.get('schema_relations', {})
        
        if role and schema_name in schema_relations:
            schemas = session.get('schemas', get_rs(session).get_all_schemas())
            return get_schema_content(role, schema_name, schema_relations), mk_schema_nav(role_name, schemas, schema_name)
        else:
            return Div(P("Error: Schema not found or role not available"), cls='text-red-500')
    except Exception as e:
        return Div(P(f"Error loading schema content: {str(e)}"), cls='text-red-500')

# ===== End Routes =====

if __name__ == '__main__':
    try:
        serve()
    except KeyboardInterrupt:
        pass
    finally:
        sys.exit(0)
