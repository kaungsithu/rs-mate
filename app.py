from fasthtml.common import *
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
    return LabelList(groups) if groups else '-'

# Get user roles for each user
@rt('/user-roles/{user_id}')
def get(session, user_id: int):
    roles = RedshiftUser.get_user_roles(user_id, get_rs(session))
    return LabelList(roles) if roles else '-'



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
    return LabelList(users) if users else '-'

# Get nested roles for each role
@rt('/role-nested-roles/{role_name}')
def get(session, role_name: str):
    nested_roles = RedshiftRole.get_role_nested_roles(role_name, get_rs(session))
    return LabelList(nested_roles) if nested_roles else '-'

# Show role details
@rt('/role/{role_name}')
def get(session, role_name: str):
    try:
        rs = get_rs(session)
        role = RedshiftRole.get_role(role_name, rs)
        all_roles = RedshiftRole.get_all(rs)
        
        # Get all schemas
        schemas_result = rs.execute_query(sql.GET_ALL_SCHEMAS)
        schemas = [row[0] for row in schemas_result] if schemas_result else []
        
        if role:
            set_role(session, role)
            return MainLayout(mk_role_form(role, all_roles, schemas), active_btn='roles')
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
@rt('/role/save-privileges')
def post(session, frm_data: dict):
    role = get_role(session)
    rs = get_rs(session)
    
    # Process form data to extract privileges
    privileges = []
    for key, value in frm_data.items():
        if key.startswith('priv-') and value == 'on':
            # Format: priv-{schema}-{object}-{privilege}
            parts = key.split('-')
            if len(parts) == 4:
                schema_name = parts[1]
                object_name = parts[2]
                privilege_type = parts[3]
                
                # Determine object type based on privilege
                if privilege_type == 'EXECUTE':
                    object_type = 'FUNCTION'  # Could be FUNCTION or PROCEDURE
                else:
                    object_type = 'TABLE'  # Could be TABLE or VIEW
                
                privileges.append({
                    'schema_name': schema_name,
                    'object_name': object_name,
                    'object_type': object_type,
                    'privilege_type': privilege_type
                })
    
    # TODO: Compare with existing privileges and update
    # This is a simplified implementation
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
        add_toast(session, 'Privileges saved successfully!', 'success', True)
    else:
        add_toast(session, 'Error saving some privileges!', 'warning', True)
    
    return None

if __name__ == '__main__':
    try:
        serve()
    except KeyboardInterrupt:
        pass
    finally:
        sys.exit(0)
