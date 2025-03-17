from fasthtml.common import *
from monsterui.all import *
import json
from redshift.role import RedshiftRole
from helpers.session_helper import *
from fasthtml.common import CheckboxX as fhCheckboxX
from components.common import *

# ===== Role list table =====

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
                    Button(UkIcon('trash-2'), cls=ButtonT.destructive, 
                           hx_delete=f'/role/{role.role_name}',
                           hx_confirm=f'Are you sure you want to delete role {role.role_name}?',
                           hx_target=f'#role-row-{role.role_name}',
                           hx_swap='outerHTML') if role.role_id >= 200_000 else '-',
                    id=f'role-row-{role.role_name}',
                    cls='Actions'
                )
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
    role_nested_roles_frm = Div(
                DivHStacked(H4('Nested Roles', cls='mb-4'), Loading((LoadingT.bars, LoadingT.lg, 'mx-4'), htmx_indicator=True)),
                Form(
                    Hidden(id='role_name', value=role.role_name),
                    Hidden(id='nested_role_list_id', value='nested-role-list'),
                    ListAddRemove(*SelectOptions([r.role_name for r in all_roles if r.role_name != role.role_name]), 
                                  items=role.nested_roles, placeholder='Select Role', 
                                  id='nested-role-select', ls_id='nested-role-list', 
                                  add_hx_post='/role/add-nested-role', remove_hx_post='/role/remove-nested-role'),
                    Button('Save Nested Roles', id='btn-save-nested-roles', cls=ButtonT.primary),
                    Loading((LoadingT.bars, LoadingT.lg, 'mx-4'), htmx_indicator=True),
                    cls='space-y-6', hx_post='/role/save-nested-roles', hx_swap='none',
                    hx_disabled_elt='#btn-save-nested-roles'
                )
            )
    return fill_form(role_nested_roles_frm, role)

# === Role Privileges ===
def mk_role_privileges(role: RedshiftRole, schemas: list):
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
    
    # Create schema tabs
    schema_tabs = []
    schema_contents = []
    
    for i, schema in enumerate(schemas):
        schema_tabs.append(Li(A(schema, href=f'#{schema}', id=f'tab-{schema}'), 
                              cls='uk-active' if i == 0 else ''))
        
        # Create privilege tables for this schema
        schema_privileges = privileges_by_schema.get(schema, {})
        
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
        tables_tbl = None
        if tables_rows:
            tables_tbl = Div(
                H5('Tables'),
                Table(
                    Thead(Tr(Th('Table Name'), Th('SELECT'), Th('INSERT'), Th('UPDATE'), Th('DELETE'))),
                    Tbody(*tables_rows),
                    cls=(TableT.striped, TableT.sm)
                ),
                cls='mb-6'
            )
        
        views_tbl = None
        if views_rows:
            views_tbl = Div(
                H5('Views'),
                Table(
                    Thead(Tr(Th('View Name'), Th('SELECT'))),
                    Tbody(*views_rows),
                    cls=(TableT.striped, TableT.sm)
                ),
                cls='mb-6'
            )
        
        funcs_tbl = None
        if funcs_rows:
            funcs_tbl = Div(
                H5('Functions & Procedures'),
                Table(
                    Thead(Tr(Th('Type'), Th('Name'), Th('EXECUTE'))),
                    Tbody(*funcs_rows),
                    cls=(TableT.striped, TableT.sm)
                ),
                cls='mb-6'
            )
        
        # Create schema content
        schema_content = Li(
            Div(
                tables_tbl if tables_tbl else Div(P('No tables in this schema')),
                views_tbl if views_tbl else Div(P('No views in this schema')),
                funcs_tbl if funcs_tbl else Div(P('No functions or procedures in this schema')),
                Button('Save Privileges', id=f'btn-save-privs-{schema}', cls=ButtonT.primary),
                Loading((LoadingT.bars, LoadingT.lg, 'mx-4'), htmx_indicator=True),
                cls='space-y-4',
                id=schema
            ),
            cls='uk-active' if i == 0 else ''
        )
        
        schema_contents.append(schema_content)
    
    role_privileges_frm = Div(
        H4('Privileges', cls='mb-4'),
        Form(
            Hidden(id='role_name', value=role.role_name),
            TabContainer(*schema_tabs, uk_switcher='connect: #schema-content; animation: uk-animation-fade'),
            Ul(*schema_contents, id='schema-content', cls='uk-switcher'),
            cls='space-y-6',
            hx_post='/role/save-privileges',
            hx_swap='none'
        )
    )
    
    return role_privileges_frm

# ===== Main Role Form =====
def mk_role_form(role: RedshiftRole, all_roles: list, schemas: list):
    rfrm = Card(
                CardHeader(
                    DivFullySpaced(
                        DivLAligned(
                            H3(f'{role.role_name}', cls=TextT.primary),
                            P(Output(f'ID: {role.role_id}')),
                        ),
                        LinkButton('All Roles', icon='arrow-left', href='/roles', cls=ButtonT.default),
                    )
                ),
                CardBody(
                    Div(mk_role_nested_roles(role, all_roles), id='role-nested-roles'),
                    DividerSplit(cls='my-4'),
                    Div(mk_role_privileges(role, schemas), id='role-privileges')
                )
        )

    return rfrm
