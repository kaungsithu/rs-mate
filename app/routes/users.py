from fasthtml.common import *
from app import app, rt
from redshift.user import RedshiftUser
from helpers.session_helper import *
from components import *
from starlette.responses import RedirectResponse

@rt('/users')
def get(session):
    users = RedshiftUser.get_all(get_rs(session))
    return MainLayout(mk_user_table(users))

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

# Get user groups for each user
@rt('/user-groups/{user_id}')
def get(session, user_id: int):
    groups = RedshiftUser.get_user_groups(user_id, get_rs(session))
    return BadgeList(groups) if groups else '-'

# Get user roles for each user
@rt('/user-roles/{user_id}')
def get(session, user_id: int):
    roles = RedshiftUser.get_user_roles(user_id, get_rs(session))
    return BadgeList(roles) if roles else '-'
