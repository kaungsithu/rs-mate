from fasthtml.common import *
from redshift.database import Redshift
from redshift.user import RedshiftUser 
from helpers.session_helper import *
from monsterui.all import *
import json
from components import *

# listjs
listjs = Script(src='https://cdnjs.cloudflare.com/ajax/libs/list.js/2.3.1/list.min.js')
hdrs = (Theme.violet.headers(mode='light'), listjs)
app, rt = fast_app(hdrs=hdrs, debug=True, live=True)
setup_toasts(app)

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
def post(session, frm_data: dict):
    user_name = frm_data.get('user_name')
    password = frm_data.get('password')
    super_user = frm_data.get('super_user') == 'on'
    can_create_db = frm_data.get('can_create_db') == 'on'
    
    # Create the user in Redshift
    rs = get_rs(session)
    try:
        user = RedshiftUser.create_user(
            user_name=user_name,
            password=password,
            super_user=super_user,
            can_create_db=can_create_db,
            rs=rs
        )
        
        if user:
            add_toast(session, f'User {user_name} created successfully!', 'success', True)
            # Redirect to the user detail page for further configuration
            return RedirectResponse(url=f'/user/{user.user_id}', status_code=303)
        else:
            add_toast(session, f'Error creating user {user_name}!', 'error', True)
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

if __name__ == '__main__':
    try:
        serve()
    except KeyboardInterrupt:
        pass
    finally:
        sys.exit(0)
