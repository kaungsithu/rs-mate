"""
User management routes.
Routes for listing, viewing, creating, and editing Redshift users.
"""
from fasthtml.common import RedirectResponse
from redshift.user import RedshiftUser
from components.common import MainLayout
from components.user import mk_user_table, mk_user_form, mk_user_props
from components.common import BadgeList, RemovableList
from routes.helpers import get_rs, set_rs, set_user, get_user, add_toast


def register_routes(app):
    """Register all user management routes."""

    @app.rt('/users')
    def get(session):
        """List all users."""
        users = RedshiftUser.get_all(get_rs(session))
        return MainLayout(mk_user_table(users))

    @app.rt('/user/{user_id}')
    def get(session, user_id: int):
        """View user detail with all information."""
        try:
            rs = get_rs(session)
            user = RedshiftUser.get_user(user_id, rs)
            all_groups = RedshiftUser.get_all_groups(rs)
            all_roles = RedshiftUser.get_all_roles(rs)

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

            if user:
                set_user(session, user)
                # Store schema relations in session
                session['schema_relations'] = schema_relations
                return MainLayout(mk_user_form(user, all_groups, all_roles, schemas, schema_relations), active_btn='users')
            else:
                add_toast(session, f'User with ID: {user_id} not found', 'error', True)
                return RedirectResponse('/users')
        except Exception as e:
            add_toast(session, f'Error retrieving user with ID: {user_id}', 'error', True)
            return RedirectResponse('/users')

    @app.rt('/user-groups/{user_id}')
    def get(session, user_id: int):
        """Get user groups as badge list."""
        groups = RedshiftUser.get_user_groups(user_id, get_rs(session))
        return BadgeList(groups) if groups else '-'

    @app.rt('/user-roles/{user_id}')
    def get(session, user_id: int):
        """Get user roles as badge list."""
        roles = RedshiftUser.get_user_roles(user_id, get_rs(session))
        return BadgeList(roles) if roles else '-'

    @app.rt('/user/create')
    def post(session, user: RedshiftUser):
        """Create a new user."""
        rs = get_rs(session)
        try:
            nu = RedshiftUser.create_user(user, rs=rs)  # new user

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

    @app.rt('/user/save-props')
    def post(session, user: RedshiftUser):
        """Save user properties."""
        try:
            if user.update(get_rs(session)):
                add_toast(session, f'User: {user.user_name} saved successfully!', 'success', True)
            else:
                add_toast(session, f'Error saving user: {user.user_name}!', 'error', True)
            return mk_user_props(user)
        except Exception as e:
            add_toast(session, f'Error saving user properties: {str(e)}', 'error', True)
            return mk_user_props(user)

    @app.rt('/user/add-group')
    def post(session, frm_data: dict):
        """Add user to a group."""
        try:
            user = get_user(session)
            # group_select returning a list with two values: [option_placeholder, selected_value]
            group_name = frm_data.get('ugroup-select', [None, None])[1] if frm_data.get('ugroup-select') else None
            if group_name:
                user.groups = set(user.groups) | {group_name}
                set_user(session, user)
            ls_id = frm_data.get('group_list_id')
            return RemovableList(user.groups, id=ls_id,
                               hx_post='/user/remove-group', hx_target=f'#{ls_id}')
        except Exception as e:
            add_toast(session, f'Error adding user to group: {str(e)}', 'error', True)
            return None

    @app.rt('/user/remove-group')
    def post(session, frm_data: dict):
        """Remove user from a group."""
        try:
            user = get_user(session)
            user.groups = set(user.groups) - set(frm_data.keys())
            set_user(session, user)
            ls_id = frm_data.get('group_list_id')
            return RemovableList(user.groups, id=ls_id,
                               hx_post='/user/remove-group', hx_target=f'#{ls_id}')
        except Exception as e:
            add_toast(session, f'Error removing user from group: {str(e)}', 'error', True)
            return None

    @app.rt('/user/save-groups')
    def post(session, user: RedshiftUser):
        """Save user group memberships to database."""
        try:
            user = get_user(session)
            if user.save_groups(get_rs(session)):
                add_toast(session, 'User groups saved successfully!', 'success', True)
            else:
                add_toast(session, 'Error saving user groups!', 'error', True)
        except Exception as e:
            add_toast(session, f'Error saving user groups: {str(e)}', 'error', True)
        return None

    @app.rt('/user/add-role')
    def post(session, frm_data: dict):
        """Add user to a role."""
        try:
            user = get_user(session)
            # role_select returning a list with two values: [option_placeholder, selected_value]
            role_name = frm_data.get('urole-select', [None, None])[1] if frm_data.get('urole-select') else None
            if role_name:
                user.roles = set(user.roles) | {role_name}
                set_user(session, user)
            ls_id = frm_data.get('role_list_id')
            return RemovableList(user.roles, id=ls_id,
                               hx_post='/user/remove-role', hx_target=f'#{ls_id}')
        except Exception as e:
            add_toast(session, f'Error adding user to role: {str(e)}', 'error', True)
            return None

    @app.rt('/user/remove-role')
    def post(session, frm_data: dict):
        """Remove user from a role."""
        try:
            user = get_user(session)
            user.roles = set(user.roles) - set(frm_data.keys())
            set_user(session, user)
            ls_id = frm_data.get('role_list_id')
            return RemovableList(user.roles, id=ls_id,
                               hx_post='/user/remove-role', hx_target=f'#{ls_id}')
        except Exception as e:
            add_toast(session, f'Error removing user from role: {str(e)}', 'error', True)
            return None

    @app.rt('/user/save-roles')
    def post(session, user: RedshiftUser):
        """Save user role memberships to database."""
        try:
            user = get_user(session)
            if user.save_roles(get_rs(session)):
                set_user(session, user)
                add_toast(session, 'User roles saved successfully!', 'success', True)
            else:
                add_toast(session, 'Error saving user roles!', 'error', True)
        except Exception as e:
            add_toast(session, f'Error saving user roles: {str(e)}', 'error', True)
        return None

    @app.rt('/user/{user_id}')
    def delete(session, user_id: int):
        """Delete a user."""
        try:
            rs = get_rs(session)
            user = RedshiftUser.get_user(user_id, rs)

            if not user:
                add_toast(session, f'User with ID: {user_id} not found', 'error', True)
                return None

            # Delete user
            if user.delete(rs):
                add_toast(session, f'User {user.user_name} deleted successfully', 'success', True)
                return None
            else:
                add_toast(session, f'Error deleting user {user.user_name}', 'error', True)
                return None
        except Exception as e:
            add_toast(session, f'Error deleting user with ID {user_id}: {str(e)}', 'error', True)
            return None
