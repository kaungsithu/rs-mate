from fasthtml.common import *
from monsterui.all import *
import json
from redshift.role import RedshiftRole
from helpers.session_helper import *
from fasthtml.common import CheckboxX as fhCheckboxX
from components.common import *

# ===== Role list table =====

def mk_delete_role_modal(role_name):
    """Create a delete confirmation modal for a role"""
    delete_btn_id = f'delete-btn-{role_name}'
    return Modal(
        ModalHeader(H3(f"Delete Role: {role_name}")),
        ModalBody(
            P(f"Are you sure you want to delete role {role_name}?", cls=TextPresets.muted_lg),
            DivFullySpaced(
                Button("Cancel", cls=ButtonT.ghost, data_uk_toggle=f"target: #delete-role-modal-{role_name}"),
                DivLAligned(
                    Button("Delete", id=delete_btn_id, cls=ButtonT.destructive, 
                           hx_delete=f'/role/{role_name}',
                           hx_target=f'#role-row-{role_name}',
                           hx_swap='outerHTML',
                           hx_disabled_elt=f'#{delete_btn_id}',
                           data_uk_toggle=f"target: #delete-role-modal-{role_name}"),
                    Loading((LoadingT.bars, LoadingT.sm, 'ml-2'), htmx_indicator=True)
                )
            )
        ),
        id=f'delete-role-modal-{role_name}'
    )

def mk_role_link(role: RedshiftRole):
    if role.role_id >= 200_000: 
        return A(role.role_name, href=f'/role/{role.role_name}', cls='text-blue-500')
    else:
        return A(role.role_name, href='#', cls=TextT.muted)

def mk_role_table(roles: list=None):
    if not roles:
        return Div(H3('No roles retrieved from Redshift.'), cls='mt-10 text-red-400')

    rows = []
    for role in roles:
        rows.append(
            Tr(
                Td(role.role_id, cls='ID'),
                Td(mk_role_link(role), cls='RoleName'),
                Td(role.owner_name if role.owner_name else '-', cls='Owner'),
                Td(
                    Loading((LoadingT.dots, LoadingT.xs), htmx_indicator=True),
                    hx_get=f'/role-users/{role.role_name}',
                    hx_trigger='revealed',
                    cls='Users',
                ),
                Td(
                    Loading((LoadingT.dots, LoadingT.xs), htmx_indicator=True),
                    hx_get=f'/role-nested-roles/{role.role_name}',
                    hx_trigger='revealed',
                    cls='NestedRoles',
                ),
                Td(
                    (Button(UkIcon('trash-2'), cls=(ButtonT.destructive, ButtonT.xs), 
                           data_uk_toggle=f"target: #delete-role-modal-{role.role_name}") if role.role_id >= 200_000 else '-'),
                    # Add delete confirmation modal if role can be deleted
                    (mk_delete_role_modal(role.role_name) if role.role_id >= 200_000 else ''),
                    cls='Actions'
                ),
                id=f'role-row-{role.role_name}'
            )
        )

    tbl_headers = ['ID', 'Role Name', 'Owner', 'Users', 'Nested Roles', 'Actions']
    tbl = Table(Thead(Tr(*map(Th, tbl_headers))), Tbody(*rows, cls='list'), cls=(TableT.striped))
    card_header=(H4('Redshift Roles'), Subtitle('Click on each role name to manage role details'))
    ctrls = DivFullySpaced(
                Div(Input(cls='w-sm search', placeholder='Filter roles...')),
                Button(UkIcon('plus'), 'Add Role', 
                       cls=ButtonT.primary,
                       data_uk_toggle="target: #new-role-modal")
    )

    # Create new role modal
    new_role_modal = Modal(
        ModalHeader(H3("Create New Role")),
        ModalBody(
            Form(
                FormSectionDiv(
                    LabelInput('Role Name', id='role_name', required=True),
                    HelpText('Redshift role name (required)')
                ),
                DividerSplit(cls='my-4'),
            DivFullySpaced(
                Button("Cancel", cls=ButtonT.default, data_uk_toggle="target: #new-role-modal"),
                Button('Create Role', id='btn-create-role', cls=ButtonT.primary, data_uk_toggle="target: #new-role-modal"),
                Loading((LoadingT.bars, LoadingT.lg, 'mx-4'), htmx_indicator=True),
            ),
            cls='space-y-6',
            action='/role/create', method='post',
            hx_disabled_elt='#btn-create-role'
            )
        ),
        id='new-role-modal'
    )

    card = Card(ctrls, tbl, header=card_header, id='roles-table', cls='w-full lg:w-4/5 mb-6')
    list_script = Script(f"new List('roles-table', {{ valueNames: {json.dumps(tbl_headers)} }})")

    return DivVStacked(card, list_script, new_role_modal, cls='w-full lg:w-4/5')

# ===== Role Management =====

# === Role Nested Roles ===
def mk_role_nested_roles(role: RedshiftRole, all_roles: list):
    role_nested_roles_frm = Form(
                DivFullySpaced(
                    H4('Nested Roles'), 
                    DivRAligned(
                        Loading((LoadingT.bars, LoadingT.lg, 'mx-4'), htmx_indicator=True),
                        Button('Save Nested Roles', id='btn-save-nested-roles', cls=ButtonT.primary),
                        cls='space-x-2'
                    ),
                    cls='space-y-2'
                ),
                Div(
                    Hidden(id='role_name', value=role.role_name),
                    Hidden(id='nested_role_list_id', value='nested-role-list'),
                    ListAddRemove(*SelectOptions([r.role_name for r in all_roles if r.role_name != role.role_name]), 
                                  items=role.nested_roles, placeholder='Select Role', 
                                  id='nested-role-select', ls_id='nested-role-list', 
                                  add_hx_post='/role/add-nested-role', remove_hx_post='/role/remove-nested-role'),
                    Loading((LoadingT.bars, LoadingT.lg, 'mx-4'), htmx_indicator=True),
                    cls='space-y-4', 
                ),
                id='role-nested-roles-form',
                hx_post='/role/save-nested-roles', hx_swap='none',
                hx_disabled_elt='#btn-save-nested-roles'
            )
    return fill_form(role_nested_roles_frm, role)

# === Role Privileges ===
# Helper method to create schema content for a specific schema
def mk_schema_content(schema: str, schema_privileges: dict, schema_relations: dict):
    # Tables
    tables_rows = []
    for key, privs in schema_privileges.items():
        if key.startswith('TABLE:'):
            obj_type, obj_name = key.split(':', 1)
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
                )
            )
    
    # Views
    views_rows = []
    for key, privs in schema_privileges.items():
        if key.startswith('VIEW:'):
            obj_type, obj_name = key.split(':', 1)
            views_rows.append(
                Tr(
                    Td(obj_name),
                    Td(fhCheckboxX(id=f'priv-{schema}-{obj_name}-SELECT', 
                                  checked='SELECT' in privs, 
                                  cls='uk-checkbox')),
                )
            )
    
    # Functions and Procedures
    funcs_rows = []
    for key, privs in schema_privileges.items():
        if key.startswith('FUNCTION:') or key.startswith('PROCEDURE:'):
            obj_type, obj_name = key.split(':', 1)
            funcs_rows.append(
                Tr(
                    Td(obj_type),
                    Td(obj_name),
                    Td(fhCheckboxX(id=f'priv-{schema}-{obj_name}-EXECUTE', 
                                  checked='EXECUTE' in privs, 
                                  cls='uk-checkbox')),
                )
            )
    
    # Create tables
    tables_tbl = Div(
        Table(
            Thead(Tr(Th('Table Name'), Th('SELECT'), Th('INSERT'), Th('UPDATE'), Th('DELETE'))),
            Tbody(*tables_rows, id=f'tables-tbody-{schema}'),
            cls=(TableT.striped, TableT.sm)
        ),
        cls='mb-6'
    )
        
    # Add new table relation section
    # Use pre-loaded tables
    tables = schema_relations[schema]['tables']
    add_table_section = (Div(
        Form(
            DivFullySpaced(
                H5('Tables'),
                DivRAligned(
                    Loading((LoadingT.dots, LoadingT.xs), htmx_indicator=True),
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
        cls='mb-6'
    )
        
    # Add new view relation section
    # Use pre-loaded views
    views = schema_relations[schema]['views']
    add_view_section = Div(
        Form(
            DivFullySpaced(
                H5('Views'),
                DivRAligned(
                    Loading((LoadingT.dots, LoadingT.xs), htmx_indicator=True),
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
        cls='mb-6'
    )
        
    # Add new function/procedure relation section
    # Use pre-loaded functions and procedures
    # TODO: Both functions and procedures are combined, to make better UX.
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
                    Loading((LoadingT.dots, LoadingT.xs), htmx_indicator=True),
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
                
    # Create schema content
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

# Method to return schema content for HTMX
def get_schema_content(role: RedshiftRole, schema: str, schema_relations=None):
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

def mk_schema_nav(role_name:str, schemas: list, active_schema: str):
    # Create schema nav items
    # TODO: Active class not properly set.
    return NavContainer(
        *[Li(
            A(s),
            hx_get=f'/role/schema-content/{role_name}/{s}',
            hx_target='#schema-content', 
            hx_swap='outerHTML',
            hx_trigger='click',
            hx_disabled_elt=f'input, button',
            # cls=f"{'uk-active' if s == active_schema else ''}"
        ) for s in schemas],
        cls=(NavT.secondary, 'border-r'),
        id='schema-nav'
    )

def mk_role_privileges(role: RedshiftRole, schemas: list, schema_relations=None):
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
                Loading((LoadingT.bars, LoadingT.lg), htmx_indicator=True),
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
                    # cls='w-3/4'
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

# ===== Main Role Form =====
def mk_role_form(role: RedshiftRole, all_roles: list, schemas: list, schema_relations=None):
    rfrm = Card(
                CardHeader(
                    DivFullySpaced(
                        DivLAligned(
                            H3(f'{role.role_name}', cls=TextT.primary),
                        ),
                        LinkButton('All Roles', icon='arrow-left', href='/roles', cls=ButtonT.default),
                    )
                ),
                CardBody(
                    Div(mk_role_nested_roles(role, all_roles), id='role-nested-roles'),
                    DividerSplit(cls='my-4'),
                    Div(mk_role_privileges(role, schemas, schema_relations), id='role-privileges')
                ),
                cls='w-full lg:w-4/5 mb-6'
        )

    return rfrm
