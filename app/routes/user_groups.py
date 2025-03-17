from fasthtml.common import *
from app import app, rt
from redshift.user import RedshiftUser
from helpers.session_helper import *
from components import *

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

@rt('/user/remove-group')
def post(session, frm_data: dict):
    user = get_user(session)
    user.groups = set(user.groups) - set(frm_data.keys())
    set_user(session, user)
    ls_id = frm_data['group_list_id']
    return RemovableList(user.groups, id=ls_id, 
                         hx_post='/user/remove-group', hx_target=f'#{ls_id}')

@rt('/user/save-groups')
def post(session, user: RedshiftUser):
    user = get_user(session)
    if user.save_groups(get_rs(session)):
        add_toast(session, 'User groups saved successfully!', 'success', True)
    else:
        add_toast(session, 'Error saving user groups!', 'error', True)
    return None
