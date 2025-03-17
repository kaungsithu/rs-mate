from fasthtml.common import *
from fasthtml.common import CheckboxX as fhCheckboxX
from app import app, rt
from redshift.role import RedshiftRole
from redshift import sql_queries as sql
from helpers.session_helper import *
from components import *

# ===== Role Privileges =====
@rt('/role/get-schema-tables/{schema_name}')
def get(session, schema_name: str):
    rs = get_rs(session)
    
    # Get tables for the schema
    tables_result = rs.execute_query(sql.GET_SCHEMA_TABLES, (schema_name,))
    tables = [row[0] for row in tables_result] if tables_result else []
    
    # Return options for select
    options = SelectOptions(tables)
    return ''.join([str(option) for option in options])

@rt('/role/get-schema-views/{schema_name}')
def get(session, schema_name: str):
    rs = get_rs(session)
    
    # Get views for the schema
    views_result = rs.execute_query(sql.GET_SCHEMA_VIEWS, (schema_name,))
    views = [row[0] for row in views_result] if views_result else []
    
    # Return options for select
    options = SelectOptions(views)
    return ''.join([str(option) for option in options])

@rt('/role/get-schema-functions/{schema_name}')
def get(session, schema_name: str, frm_data: dict):
    rs = get_rs(session)
    func_type = frm_data.get('new-func-type-' + schema_name)
    
    if func_type == 'FUNCTION':
        # Get functions for the schema
        funcs_result = rs.execute_query(sql.GET_SCHEMA_FUNCTIONS, (schema_name,))
        funcs = [row[0] for row in funcs_result] if funcs_result else []
    else:
        # Get procedures for the schema
        funcs_result = rs.execute_query(sql.GET_SCHEMA_PROCEDURES, (schema_name,))
        funcs = [row[0] for row in funcs_result] if funcs_result else []
    
    # Return options for select
    options = SelectOptions(funcs)
    return ''.join([str(option) for option in options])


@rt('/role/load-table/{schema_name}')
def post(session, schema_name: str, frm_data: dict):
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

@rt('/role/load-view/{schema_name}')
def post(session, schema_name: str, frm_data: dict):
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
                Td(fhCheckboxX(id=f'priv-{schema_name}-{view_name}-INSERT', cls='uk-checkbox')),
                Td(fhCheckboxX(id=f'priv-{schema_name}-{view_name}-UPDATE', cls='uk-checkbox')),
                Td(fhCheckboxX(id=f'priv-{schema_name}-{view_name}-DELETE', cls='uk-checkbox')),
                id=existing_view_id
            )

@rt('/role/load-function/{schema_name}')
def get(session, schema_name: str, frm_data: dict):
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

@rt('/role/save-privileges')
def post(session, frm_data: dict):
    role = get_role(session)
    rs = get_rs(session)
    
    # Get current privileges from the database
    current_role = RedshiftRole.get_role(role.role_name, rs)
    current_privileges = current_role.privileges if current_role else []
    
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
                # Note: We're not comparing object_type here because the database might 
                # report a slightly different type name than what we determine
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
                # Note: We're not comparing object_type here because the database might 
                # report a slightly different type name than what we determine
                found = True
                break
        if not found:
            # Use the object_type from the database for revoking
            privileges_to_revoke.append(current)
    
    # Apply changes
    success = True
    revoked_count = 0
    granted_count = 0
    
    # Revoke privileges
    for privilege in privileges_to_revoke:
        if role.revoke_privilege(
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
        if role.grant_privilege(
            privilege['schema_name'],
            privilege['object_name'],
            privilege['object_type'],
            privilege['privilege_type'],
            rs
        ):
            granted_count += 1
        else:
            success = False
    
    # Refresh role privileges
    updated_role = RedshiftRole.get_role(role.role_name, rs)
    if updated_role:
        set_role(session, updated_role)
    
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
    
    return None
