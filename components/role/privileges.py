"""Role privilege management components."""
from fasthtml.common import *
from monsterui.all import *
from redshift.role import RedshiftRole
from helpers.session_helper import *
from fasthtml.common import CheckboxX as fhCheckboxX
from components.common import *

__all__ = ['mk_schema_content', 'get_schema_content', 'mk_schema_nav', 'mk_role_privileges']


def mk_schema_content(schema: str, schema_privileges: dict, schema_relations: dict):
    """Create schema content with privilege checkboxes for tables, views, functions."""
    # Tables
    tables_rows = []
    existing_tables = []
    for key, privs in schema_privileges.items():
        if key.startswith('TABLE:'):
            obj_type, obj_name = key.split(':', 1)
            existing_tables.append(obj_name)
            tables_rows.append(
                Tr(
                    Td(obj_name),
                    Td(fhCheckboxX(id=f'priv-{schema}-{obj_name}-SELECT',
                                  checked='SELECT' in privs,
                                  cls='uk-checkbox')),
                    Td(fhCheckboxX(id=f'priv-{schema}-{obj_name}-INSERT',
                                  checked='INSERT' in privs,
                                  cls='uk-checkbox')),
                    Td(fhCheckboxX(id=f'priv-{schema}-{obj_name}-UPDATE',
                                  checked='UPDATE' in privs,
                                  cls='uk-checkbox')),
                    Td(fhCheckboxX(id=f'priv-{schema}-{obj_name}-DELETE',
                                  checked='DELETE' in privs,
                                  cls='uk-checkbox')),
                    id=f'table-row-{schema}-{obj_name}'
                )
            )

    # Views
    views_rows = []
    existing_views = []
    for key, privs in schema_privileges.items():
        if key.startswith('VIEW:'):
            obj_type, obj_name = key.split(':', 1)
            existing_views.append(obj_name)
            views_rows.append(
                Tr(
                    Td(obj_name),
                    Td(fhCheckboxX(id=f'priv-{schema}-{obj_name}-SELECT',
                                  checked='SELECT' in privs,
                                  cls='uk-checkbox')),
                    id=f'view-row-{schema}-{obj_name}'
                )
            )

    # Functions and Procedures
    funcs_rows = []
    existing_funcs = []
    for key, privs in schema_privileges.items():
        if key.startswith('FUNCTION:') or key.startswith('PROCEDURE:'):
            obj_type, obj_name = key.split(':', 1)
            existing_funcs.append(obj_name)
            funcs_rows.append(
                Tr(
                    Td(obj_type),
                    Td(obj_name),
                    Td(fhCheckboxX(id=f'priv-{schema}-{obj_name}-EXECUTE',
                                  checked='EXECUTE' in privs,
                                  cls='uk-checkbox')),
                    id=f'func-row-{schema}-{obj_name}'
                )
            )

    # Create tables
    tables_tbl = Div(
        Table(
            Thead(Tr(Th('Table Name'), Th('SELECT'), Th('INSERT'), Th('UPDATE'), Th('DELETE'))),
            Tbody(*tables_rows, id=f'tables-tbody-{schema}'),
            cls=(TableT.striped, TableT.sm)
        ),
        *[Hidden(id=f'table-row-{schema}-{table_name}', value='exists') for table_name in existing_tables],
        cls='mb-6'
    )

    tables = schema_relations[schema]['tables']
    add_table_section = (Div(
        Form(
            DivFullySpaced(
                H5('Tables'),
                DivRAligned(
                    Select(*SelectOptions(tables), id=f'new-table-{schema}', name=f'new-table-{schema}',
                        placeholder='Select Table'),
                    Button('Load Table', id=f'btn-load-table-{schema}', cls=(ButtonT.secondary, ButtonT.sm)),
                ),
                cls='space-x-2'
            ),
            id=f'new-table-privileges-{schema}', cls='mb-4',
            hx_post=f'/role/load-table/{schema}',
            hx_target=f'#tables-tbody-{schema}',
            hx_swap='afterbegin'
        ),
        cls='mb-6'
    ))

    views_tbl = Div(
        Table(
            Thead(Tr(Th('View Name'), Th('SELECT'))),
            Tbody(*views_rows, id=f'views-tbody-{schema}'),
            cls=(TableT.striped, TableT.sm)
        ),
        *[Hidden(id=f'view-row-{schema}-{view_name}', value='exists') for view_name in existing_views],
        cls='mb-6'
    )

    views = schema_relations[schema]['views']
    add_view_section = Div(
        Form(
            DivFullySpaced(
                H5('Views'),
                DivRAligned(
                    Select(*SelectOptions(views), id=f'new-view-{schema}', placeholder='Select View'),
                    Button('Load View', id=f'btn-load-view-{schema}', cls=(ButtonT.secondary, ButtonT.sm)),
                ),
                cls='space-x-2'
            ),
            id=f'new-view-privileges-{schema}', cls='mb-4',
            hx_post=f'/role/load-view/{schema}',
            hx_target=f'#views-tbody-{schema}',
            hx_swap='afterbegin'
        ),
        cls='mb-6'
    )

    funcs_tbl = Div(
        Table(
            Thead(Tr(Th('Type'), Th('Name'), Th('EXECUTE'))),
            Tbody(*funcs_rows, id=f'functions-tbody-{schema}'),
            cls=(TableT.striped, TableT.sm)
        ),
        *[Hidden(id=f'func-row-{schema}-{func_name}', value='exists') for func_name in existing_funcs],
        cls='mb-6'
    )

    funcs = schema_relations[schema]['functions']
    funcs_vals = [f'FUNCTION:{f}' for f in funcs]
    procs = schema_relations[schema]['procedures']
    procs_vals = [f'PROCEDURE:{p}' for p in procs]
    funcs_procs = funcs + procs
    funcs_procs_vals = funcs_vals + procs_vals

    add_func_section = Div(
        Form(
            DivFullySpaced(
                H5('Functions & Procedures'),
                DivRAligned(
                    Select(
                        *SelectOptions(funcs_procs, funcs_procs_vals),
                        id=f'new-func-{schema}',
                        placeholder='Select Function/Procedure'
                    ),
                    Button('Load Function', id=f'btn-load-func-{schema}', cls=(ButtonT.secondary, ButtonT.sm)),
                ),
                cls='space-x-2'
            ),
            Div(id=f'new-func-privileges-{schema}'),
            cls='mb-4',
            hx_post=f'/role/load-function/{schema}',
            hx_target=f'#functions-tbody-{schema}',
            hx_swap='afterbegin'
        ),
        cls='mb-6'
    )

    return Div(
        DivCentered(H4(f'{schema.upper()}', cls=TextT.primary)),
        add_table_section, tables_tbl,
        DividerSplit(),
        add_view_section, views_tbl,
        DividerSplit(),
        add_func_section, funcs_tbl,
        cls='space-y-4',
        id='schema-content'
    )


def get_schema_content(role: RedshiftRole, schema: str, schema_relations=None):
    """Get schema content for role with their current privileges."""
    # Group privileges by schema and object
    privileges_by_schema = {}
    for privilege in role.privileges:
        schema_name = privilege['schema_name']
        object_name = privilege['object_name']
        object_type = privilege['object_type']
        privilege_type = privilege['privilege_type']

        if schema_name not in privileges_by_schema:
            privileges_by_schema[schema_name] = {}

        key = f"{object_type}:{object_name}"
        if key not in privileges_by_schema[schema_name]:
            privileges_by_schema[schema_name][key] = []

        privileges_by_schema[schema_name][key].append(privilege_type)

    # Get privileges for this schema
    schema_privileges = privileges_by_schema.get(schema, {})

    # Create and return schema content
    return mk_schema_content(schema, schema_privileges, schema_relations)


def mk_schema_nav(role_name: str, schemas: list, active_schema: str):
    """Create schema navigation."""
    return NavContainer(
        *[Li(
            A(s),
            hx_get=f'/role/schema-content/{role_name}/{s}',
            hx_target='#schema-content',
            hx_swap='outerHTML',
            hx_trigger='click',
            hx_disabled_elt=f'input, button',
        ) for s in schemas],
        cls=(NavT.secondary, 'border-r'),
        id='schema-nav'
    )


def mk_role_privileges(role: RedshiftRole, schemas: list, schema_relations=None):
    """Create role privileges form."""
    # Group privileges by schema and object
    privileges_by_schema = {}
    for privilege in role.privileges:
        schema_name = privilege['schema_name']
        object_name = privilege['object_name']
        object_type = privilege['object_type']
        privilege_type = privilege['privilege_type']

        if schema_name not in privileges_by_schema:
            privileges_by_schema[schema_name] = {}

        key = f"{object_type}:{object_name}"
        if key not in privileges_by_schema[schema_name]:
            privileges_by_schema[schema_name][key] = []

        privileges_by_schema[schema_name][key].append(privilege_type)

    # Create initial schema content for the first schema
    initial_schema = schemas[0] if schemas else None
    initial_schema_content = get_schema_content(role, initial_schema, schema_relations) if initial_schema else Div()

    role_privileges_frm = Form(
        DivFullySpaced(
            H4('Privileges'),
            Loading((LoadingT.bars, LoadingT.lg), htmx_indicator=True),
            DivRAligned(
                Button('Save Privileges', id='btn-save-privileges', cls=ButtonT.primary),
                cls='space-x-2'
            ),
            cls='space-y-2'
        ),
        Div(
            Hidden(id='role_name', value=role.role_name),
            Grid(
                mk_schema_nav(role.role_name, schemas, initial_schema),
                Div(
                    initial_schema_content,
                    id='schema-content-container',
                    cls='col-span-4'
                ),
                cls='space-x-4', cols=5
            ),
            cls='space-y-6',
        ),
        id='role-privileges-form',
        hx_post='/role/save-privileges',
        hx_swap='none',
        hx_disabled_elt='#btn-save-privileges',
    )

    return role_privileges_frm
