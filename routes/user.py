"""
User management routes.
Routes for listing, viewing, creating, and editing Redshift users.
"""
from fasthtml.common import RedirectResponse
from redshift.user import RedshiftUser
from components.common import MainLayout
from components.user import mk_user_table, mk_user_form
from routes.helpers import get_rs, set_rs, set_user, add_toast


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

    # TODO: Extract remaining user routes:
    # - GET /user-groups/{user_id} - List user groups
    # - GET /user-roles/{user_id} - List user roles
    # - POST /user/add-group - Add user to group
    # - POST /user/remove-group - Remove user from group
    # - POST /user/save-groups - Save user groups
    # - POST /user/add-role - Add user to role
    # - POST /user/remove-role - Remove user from role
    # - POST /user/save-roles - Save user roles
    # - POST /user/save-props - Save user properties
