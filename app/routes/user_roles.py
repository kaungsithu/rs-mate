from fasthtml.common import *
from app import app, rt
from redshift.user import RedshiftUser
from helpers.session_helper import *
from components import *

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
