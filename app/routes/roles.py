from fasthtml.common import *
from app import app, rt
from redshift.role import RedshiftRole
from helpers.session_helper import *
from components import *
from starlette.responses import RedirectResponse

# ===== Roles =====
@rt('/roles')
def get(session):
    roles = RedshiftRole.get_all(get_rs(session))
    return MainLayout(mk_role_table(roles), active_btn='roles')

# Get role users for each role
@rt('/role-users/{role_name}')
def get(session, role_name: str):
    users = RedshiftRole.get_role_users(role_name, get_rs(session))
    return BadgeList(users) if users else '-'

# Get nested roles for each role
@rt('/role-nested-roles/{role_name}')
def get(session, role_name: str):
    nested_roles = RedshiftRole.get_role_nested_roles(role_name, get_rs(session))
    return BadgeList(nested_roles) if nested_roles else '-'

# Show role details
@rt('/role/{role_name}')
def get(session, role_name: str):
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

# Delete role
@rt('/role/{role_name}')
def delete(session, role_name: str):
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

# Create role
@rt('/role/create')
def post(session, frm_data: dict):
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
