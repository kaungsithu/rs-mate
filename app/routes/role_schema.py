from fasthtml.common import *
from app import app, rt
from redshift.role import RedshiftRole
from helpers.session_helper import *
from components import *

# ===== Role Schema Content =====
@rt('/role/schema-nav/{schema_name}')
def get(session, schema_name: str):
    schemas = session.get('schemas', get_rs(session).get_all_schemas())
    return mk_schema_nav(schemas, schema_name)

@rt('/role/schema-content/{role_name}/{schema_name}')
def get(session, role_name: str, schema_name: str):
    try:
        rs = get_rs(session)
        role = RedshiftRole.get_role(role_name, rs)
        schema_relations = session.get('schema_relations', {})
        
        if role and schema_name in schema_relations:
            schemas = session.get('schemas', get_rs(session).get_all_schemas())
            return get_schema_content(role, schema_name, schema_relations), mk_schema_nav(role_name, schemas, schema_name)
        else:
            return Div(P("Error: Schema not found or role not available"), cls='text-red-500')
    except Exception as e:
        return Div(P(f"Error loading schema content: {str(e)}"), cls='text-red-500')
