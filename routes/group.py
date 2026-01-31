"""
Group management routes.
Routes for listing, viewing, creating, and editing Redshift groups.
"""
from fasthtml.common import RedirectResponse
from redshift.group import RedshiftGroup
from redshift.user import RedshiftUser
from components.common import MainLayout, BadgeList, RemovableList
from components.group import mk_group_table, mk_group_form
from routes.helpers import get_rs, get_group, set_group, add_toast


def register_routes(app):
    """Register all group management routes."""

    @app.rt('/groups')
    def get(session):
        """List all groups."""
        groups = RedshiftGroup.get_all(get_rs(session))
        return MainLayout(mk_group_table(groups), active_btn='groups')

    @app.rt('/group-users/{group_name}')
    def get(session, group_name: str):
        """Get group users as badge list."""
        users = RedshiftGroup.get_group_users(group_name, get_rs(session))
        return BadgeList(users) if users else '-'

    @app.rt('/group/{group_name}')
    def get(session, group_name: str):
        """View group detail with all information."""
        try:
            rs = get_rs(session)
            group = RedshiftGroup.get_group(group_name, rs)
            all_users = RedshiftUser.get_all(rs)

            if group:
                set_group(session, group)
                return MainLayout(mk_group_form(group, all_users), active_btn='groups')
            else:
                add_toast(session, f'Group with name: {group_name} not found', 'error', True)
                return RedirectResponse('/groups')
        except Exception as e:
            add_toast(session, f'Error retrieving group with name: {group_name}: {str(e)}', 'error', True)
            return RedirectResponse('/groups')

    @app.rt('/group/create')
    def post(session, frm_data: dict):
        """Create a new group."""
        group_name = frm_data.get('group_name')

        if not group_name:
            add_toast(session, 'Group name is required!', 'error', True)
            return RedirectResponse('/groups', status_code=303)

        # Create the group in Redshift
        rs = get_rs(session)
        try:
            group = RedshiftGroup.create_group(group_name, rs)

            if group:
                add_toast(session, f'Group {group_name} created successfully!', 'success', True)
                # Redirect to the group detail page for further configuration
                return RedirectResponse(url=f'/group/{group.group_name}', status_code=303)
            else:
                add_toast(session, f'Error creating group {group_name}!', 'error', True)
                return RedirectResponse(url='/groups', status_code=303)
        except Exception as e:
            add_toast(session, f'Error creating group: {str(e)}', 'error', True)
            return RedirectResponse(url='/groups', status_code=303)

    @app.rt('/group/add-user')
    def post(session, frm_data: dict):
        """Add user to a group."""
        try:
            group = get_group(session)
            # user-select returning a list with two values: [option_placeholder, selected_value]
            user_name = frm_data.get('user-select', [None, None])[1] if frm_data.get('user-select') else None
            if user_name:
                group.users = set(group.users) | {user_name}
            set_group(session, group)
            ls_id = frm_data.get('user_list_id')
            return RemovableList(group.users, id=ls_id,
                               hx_post='/group/remove-user', hx_target=f'#{ls_id}')
        except Exception as e:
            add_toast(session, f'Error adding user to group: {str(e)}', 'error', True)
            return None

    @app.rt('/group/remove-user')
    def post(session, frm_data: dict):
        """Remove user from a group."""
        try:
            group = get_group(session)
            group.users = set(group.users) - set(frm_data.keys())
            set_group(session, group)
            ls_id = frm_data.get('user_list_id')
            return RemovableList(group.users, id=ls_id,
                               hx_post='/group/remove-user', hx_target=f'#{ls_id}')
        except Exception as e:
            add_toast(session, f'Error removing user from group: {str(e)}', 'error', True)
            return None

    @app.rt('/group/save-users')
    def post(session, group: RedshiftGroup):
        """Save group membership to database."""
        try:
            group = get_group(session)
            if group.update_users(group.users, get_rs(session)):
                add_toast(session, 'Group users saved successfully!', 'success', True)
            else:
                add_toast(session, 'Error saving group users!', 'error', True)
        except Exception as e:
            add_toast(session, f'Error saving group users: {str(e)}', 'error', True)
        return None

    @app.rt('/group/{group_name}')
    def delete(session, group_name: str):
        """Delete a group."""
        try:
            rs = get_rs(session)
            group = RedshiftGroup.get_group(group_name, rs)

            if not group:
                add_toast(session, f'Group with name: {group_name} not found', 'error', True)
                return None

            # Delete group
            if group.delete(rs):
                add_toast(session, f'Group {group_name} deleted successfully', 'success', True)
                return None
            else:
                add_toast(session, f'Error deleting group {group_name}', 'error', True)
                return None
        except Exception as e:
            add_toast(session, f'Error deleting group {group_name}: {str(e)}', 'error', True)
            return None
