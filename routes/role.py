"""
Role management routes.
Routes for listing, viewing, creating, and editing Redshift roles.
"""
from fasthtml.common import RedirectResponse
from redshift.role import RedshiftRole
from components.common import MainLayout, BadgeList, RemovableList
from components.role import mk_role_table, mk_role_form
from routes.helpers import get_rs, get_role, set_role, add_toast


def register_routes(app):
    """Register all role management routes."""

    @app.rt('/roles')
    def get(session):
        """List all roles."""
        roles = RedshiftRole.get_all(get_rs(session))
        return MainLayout(mk_role_table(roles), active_btn='roles')

    @app.rt('/role-users/{role_name}')
    def get(session, role_name: str):
        """Get role users as badge list."""
        users = RedshiftRole.get_role_users(role_name, get_rs(session))
        return BadgeList(users) if users else '-'

    @app.rt('/role-nested-roles/{role_name}')
    def get(session, role_name: str):
        """Get nested roles as badge list."""
        nested_roles = RedshiftRole.get_role_nested_roles(role_name, get_rs(session))
        return BadgeList(nested_roles) if nested_roles else '-'

    @app.rt('/role/{role_name}')
    def get(session, role_name: str):
        """View role detail with all information."""
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

    @app.rt('/role/create')
    def post(session, frm_data: dict):
        """Create a new role."""
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

    @app.rt('/role/add-nested-role')
    def post(session, frm_data: dict):
        """Add a nested role."""
        try:
            role = get_role(session)
            # nested-role-select returning a list with two values: [option_placeholder, selected_value]
            nested_role_name = frm_data.get('nested-role-select', [None, None])[1] if frm_data.get('nested-role-select') else None
            if nested_role_name:
                role.nested_roles = set(role.nested_roles) | {nested_role_name}
            set_role(session, role)
            ls_id = frm_data.get('nested_role_list_id')
            return RemovableList(role.nested_roles, id=ls_id,
                               hx_post='/role/remove-nested-role', hx_target=f'#{ls_id}')
        except Exception as e:
            add_toast(session, f'Error adding nested role: {str(e)}', 'error', True)
            return None

    @app.rt('/role/remove-nested-role')
    def post(session, frm_data: dict):
        """Remove a nested role."""
        try:
            role = get_role(session)
            role.nested_roles = set(role.nested_roles) - set(frm_data.keys())
            set_role(session, role)
            ls_id = frm_data.get('nested_role_list_id')
            return RemovableList(role.nested_roles, id=ls_id,
                               hx_post='/role/remove-nested-role', hx_target=f'#{ls_id}')
        except Exception as e:
            add_toast(session, f'Error removing nested role: {str(e)}', 'error', True)
            return None

    @app.rt('/role/save-nested-roles')
    def post(session, role: RedshiftRole):
        """Save nested roles to database."""
        try:
            role = get_role(session)
            if role.update_nested_roles(role.nested_roles, get_rs(session)):
                add_toast(session, 'Nested roles saved successfully!', 'success', True)
            else:
                add_toast(session, 'Error saving nested roles!', 'error', True)
        except Exception as e:
            add_toast(session, f'Error saving nested roles: {str(e)}', 'error', True)
        return None

    @app.rt('/role/{role_name}')
    def delete(session, role_name: str):
        """Delete a role."""
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
