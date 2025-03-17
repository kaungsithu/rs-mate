from fasthtml.common import *
from app import app, rt
from redshift.role import RedshiftRole
from helpers.session_helper import *
from components import *

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
