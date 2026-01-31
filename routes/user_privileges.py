"""
User privilege management routes.
Routes for managing schema-level and object-level privileges for users.
"""
from fasthtml.common import RedirectResponse, Div, P, Tr, Td
from fasthtml.common import CheckboxX as fhCheckboxX
from redshift.user import RedshiftUser
from routes.helpers import get_rs, get_user, set_user, add_toast


def register_routes(app):
    """Register all user privilege management routes."""

    @app.rt('/user/load-table/{schema_name}')
    def post(session, schema_name: str, frm_data: dict):
        """Load table privileges form row."""
        try:
            # Get table name from form data
            table_name = frm_data.get('new-table-' + schema_name)
            table_name = table_name[1] if isinstance(table_name, list) else table_name
            if not table_name:
                return None

            # Check if the table already exists in the UI
            existing_table_id = f'table-row-{schema_name}-{table_name}'
            if frm_data.get(existing_table_id) == 'exists':
                # Table already exists in the UI, return a message
                return Div(
                    P(f"Table '{table_name}' is already in the list.", cls="uk-text-warning"),
                    cls="uk-margin-small"
                )

            # Create privilege checkboxes for the table
            return Tr(
                Td(table_name),
                Td(fhCheckboxX(id=f'priv-{schema_name}-{table_name}-SELECT', cls='uk-checkbox')),
                Td(fhCheckboxX(id=f'priv-{schema_name}-{table_name}-INSERT', cls='uk-checkbox')),
                Td(fhCheckboxX(id=f'priv-{schema_name}-{table_name}-UPDATE', cls='uk-checkbox')),
                Td(fhCheckboxX(id=f'priv-{schema_name}-{table_name}-DELETE', cls='uk-checkbox')),
                id=existing_table_id
            )
        except Exception as e:
            add_toast(session, f'Error loading table: {str(e)}', 'error', True)
            return None

    @app.rt('/user/load-view/{schema_name}')
    def post(session, schema_name: str, frm_data: dict):
        """Load view privileges form row."""
        try:
            # Get view name from form data
            view_name = frm_data.get('new-view-' + schema_name)
            view_name = view_name[1] if isinstance(view_name, list) else view_name
            if not view_name:
                return None

            # Check if the view already exists in the UI
            existing_view_id = f'view-row-{schema_name}-{view_name}'
            if frm_data.get(existing_view_id) == 'exists':
                # View already exists in the UI, return a message
                return Div(
                    P(f"View '{view_name}' is already in the list.", cls="uk-text-warning"),
                    cls="uk-margin-small"
                )

            # Create privilege checkboxes for the view
            return Tr(
                Td(view_name),
                Td(fhCheckboxX(id=f'priv-{schema_name}-{view_name}-SELECT', cls='uk-checkbox')),
                id=f'view-row-{schema_name}-{view_name}'
            )
        except Exception as e:
            add_toast(session, f'Error loading view: {str(e)}', 'error', True)
            return None

    @app.rt('/user/load-function/{schema_name}')
    def post(session, schema_name: str, frm_data: dict):
        """Load function/procedure privileges form row."""
        try:
            # Get function, procedure name from form data
            func = frm_data.get('new-func-' + schema_name)
            func = func[1] if isinstance(func, list) else func
            if not func:
                return None

            # Parse function type and name
            func_parts = func.split(':')
            if len(func_parts) != 2:
                return Div(
                    P(f"Invalid function format: {func}", cls="uk-text-danger"),
                    cls="uk-margin-small"
                )

            func_type = func_parts[0]
            func_name = func_parts[1]

            # Check if the function already exists in the UI
            existing_func_id = f'func-row-{schema_name}-{func_name}'
            if frm_data.get(existing_func_id) == 'exists':
                # Function already exists in the UI, return a message
                return Div(
                    P(f"{func_type} '{func_name}' is already in the list.", cls="uk-text-warning"),
                    cls="uk-margin-small"
                )

            # Create privilege checkboxes for the function
            return Tr(
                Td(func_type),
                Td(func_name),
                Td(fhCheckboxX(id=f'priv-{schema_name}-{func_name}-EXECUTE', cls='uk-checkbox')),
                id=existing_func_id
            )
        except Exception as e:
            add_toast(session, f'Error loading function: {str(e)}', 'error', True)
            return None

    @app.rt('/user/schema-content/{user_id}/{schema_name}')
    def get(session, user_id: int, schema_name: str):
        """Get schema content with user privileges."""
        try:
            rs = get_rs(session)
            user = RedshiftUser.get_user(user_id, rs)
            schema_relations = session.get('schema_relations', {})

            if user and schema_name in schema_relations:
                # Note: This would need a component function to render properly
                # For now, returning placeholder
                return Div(P(f"Schema content for {schema_name}"))
            else:
                return Div(P("Error: Schema not found or user not available"), cls='text-red-500')
        except Exception as e:
            return Div(P(f"Error loading schema content: {str(e)}"), cls='text-red-500')

    @app.rt('/user/save-privileges')
    def post(session, frm_data: dict):
        """Save user privilege changes."""
        try:
            user = get_user(session)
            rs = get_rs(session)

            # Get current privileges from the database
            current_user = RedshiftUser.get_user(user.user_id, rs)
            current_privileges = current_user.privileges if current_user else []

            # Get schema relations from session or fetch if not available
            schema_relations = session.get('schema_relations', {})
            if not schema_relations:
                # Fetch all schemas
                schemas = rs.get_all_schemas()

                # Fetch all relations for all schemas
                for schema in schemas:
                    schema_relations[schema] = {
                        'tables': rs.get_schema_tables(schema),
                        'views': rs.get_schema_views(schema),
                        'functions': rs.get_schema_functions(schema),
                        'procedures': rs.get_schema_procedures(schema)
                    }
                # Store in session for future use
                session['schema_relations'] = schema_relations

            # Process form data to extract selected privileges
            selected_privileges = []
            for key, value in frm_data.items():
                if key.startswith('priv-') and (isinstance(value, list) and '1' in value):
                    # Format: priv-{schema}-{object}-{privilege}
                    parts = key.split('-')
                    if len(parts) == 4:
                        schema_name = parts[1]
                        object_name = parts[2]
                        privilege_type = parts[3]

                        # Determine object type based on database metadata
                        object_type = rs.determine_object_type(schema_name, object_name, privilege_type, schema_relations)

                        selected_privileges.append({
                            'schema_name': schema_name,
                            'object_name': object_name,
                            'object_type': object_type,
                            'privilege_type': privilege_type
                        })

            # Compare current privileges with selected privileges
            privileges_to_grant = []
            privileges_to_revoke = []

            # Find privileges to grant (selected but not in current)
            for selected in selected_privileges:
                found = False
                for current in current_privileges:
                    if (selected['schema_name'] == current['schema_name'] and
                        selected['object_name'] == current['object_name'] and
                        selected['privilege_type'] == current['privilege_type']):
                        found = True
                        break
                if not found:
                    privileges_to_grant.append(selected)

            # Find privileges to revoke (in current but not selected)
            for current in current_privileges:
                found = False
                for selected in selected_privileges:
                    if (current['schema_name'] == selected['schema_name'] and
                        current['object_name'] == selected['object_name'] and
                        current['privilege_type'] == selected['privilege_type']):
                        found = True
                        break
                if not found:
                    privileges_to_revoke.append(current)

            # Apply changes
            success = True
            revoked_count = 0
            granted_count = 0

            # Revoke privileges
            for privilege in privileges_to_revoke:
                if user.revoke_privilege(
                    privilege['schema_name'],
                    privilege['object_name'],
                    privilege['object_type'],
                    privilege['privilege_type'],
                    rs
                ):
                    revoked_count += 1
                else:
                    success = False

            # Grant privileges
            for privilege in privileges_to_grant:
                if user.grant_privilege(
                    privilege['schema_name'],
                    privilege['object_name'],
                    privilege['object_type'],
                    privilege['privilege_type'],
                    rs
                ):
                    granted_count += 1
                else:
                    success = False

            # Refresh user privileges
            updated_user = RedshiftUser.get_user(user.user_id, rs)
            if updated_user:
                set_user(session, updated_user)

            # Show appropriate message
            if success:
                if granted_count > 0 and revoked_count > 0:
                    add_toast(session, f'Privileges updated successfully! Granted: {granted_count}, Revoked: {revoked_count}', 'success', True)
                elif granted_count > 0:
                    add_toast(session, f'Privileges granted successfully! Count: {granted_count}', 'success', True)
                elif revoked_count > 0:
                    add_toast(session, f'Privileges revoked successfully! Count: {revoked_count}', 'success', True)
                else:
                    add_toast(session, 'No privilege changes were needed.', 'info', True)
            else:
                if granted_count > 0 or revoked_count > 0:
                    add_toast(session, f'Some privileges updated successfully, but errors occurred. Granted: {granted_count}, Revoked: {revoked_count}', 'warning', True)
                else:
                    add_toast(session, 'Error updating privileges!', 'error', True)

        except Exception as e:
            add_toast(session, f'Error saving privileges: {str(e)}', 'error', True)

        return None
