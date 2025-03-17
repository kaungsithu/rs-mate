from fasthtml.common import *
from monsterui.all import *
import json
from redshift.user import RedshiftUser
from helpers import *
from fasthtml.common import CheckboxX as fhCheckboxX
from components.common import *

__all__ = [
    'mk_delete_user_modal', 'mk_user_link', 'mk_user_table', 'mk_user_props', 
    'mk_user_groups', 'mk_user_roles', 'mk_user_privileges',
    'mk_user_schema_content', 'get_user_schema_content', 'mk_user_schema_nav', 'mk_user_form'
]

# ===== User list table =====

def mk_delete_user_modal(user_id: int, user_name: str):
    """Create a delete confirmation modal for a user"""
    delete_btn_id = f'delete-btn-{user_id}'
    return Modal(
        ModalHeader(H3(f"Delete User: {user_name}")),
        ModalBody(
            P(f"Are you sure you want to delete user {user_name}?", cls=TextPresets.muted_lg),
            DivFullySpaced(
                Button("Cancel", cls=ButtonT.ghost, data_uk_toggle=f"target: #delete-user-modal-{user_id}"),
                DivLAligned(
                    Button("Delete", id=delete_btn_id, cls=ButtonT.destructive, 
                           hx_delete=f'/user/{user_id}',
                           hx_target=f'#user-row-{user_id}',
                           hx_swap='outerHTML',
                           hx_disabled_elt=f'#{delete_btn_id}',
                           data_uk_toggle=f"target: #delete-user-modal-{user_id}"),
                    Loading((LoadingT.bars, LoadingT.sm, 'ml-2'), htmx_indicator=True)
                )
            )
        ),
        id=f'delete-user-modal-{user_id}'
    )

def mk_user_link(user: RedshiftUser):
    if user.user_id > 100: 
        return A(user.user_name, href=f'/user/{user.user_id}', cls='text-blue-500')
    else:
        return A(user.user_name, href='#', cls=TextT.muted)

def mk_user_table(users: RedshiftUser=None):
    if not users:
        return Div(H3('No users retrieved from Redshift.'), cls='mt-10 text-red-400')

    rows = []
    for user in users:
        rows.append(
            Tr(
                Td(user.user_id, cls='ID'),
                Td(mk_user_link(user), cls='Username'),
                Td('✅' if user.super_user else '-'),
                Td(
                    Loading((LoadingT.dots, LoadingT.xs), htmx_indicator=True),
                    hx_get=f'/user-groups/{user.user_id}',
                    hx_trigger='revealed',
                    cls='Groups',
                ),
                Td(
                    Loading((LoadingT.dots, LoadingT.xs), htmx_indicator=True),
                    hx_get=f'/user-roles/{user.user_id}',
                    hx_trigger='revealed',
                    cls='Roles',
                ),
                Td(
                    (Button(UkIcon('trash-2'), cls=(ButtonT.destructive, ButtonT.xs), 
                           data_uk_toggle=f"target: #delete-user-modal-{user.user_id}") if user.user_id > 100 else '-'),
                    # Add delete confirmation modal if user can be deleted
                    (mk_delete_user_modal(user.user_id, user.user_name) if user.user_id > 100 else ''),
                    cls='Actions'
                ),
                id=f'user-row-{user.user_id}'
            )
        )

    tbl_headers = ['ID', 'Username', 'Super', 'Groups', 'Roles', 'Actions']
    tbl = Table(Thead(Tr(*map(Th, tbl_headers))), Tbody(*rows, cls='list'), 
                cls=(TableT.striped))
    card_header=(H4('Redshift Users'), Subtitle('Click on each username to manage user details'))
    ctrls = DivFullySpaced(
                Div(Input(cls='w-sm search', placeholder='Filter users...')),
                Button(UkIcon('plus'), 'Add User', 
                       cls=ButtonT.primary,
                       data_uk_toggle="target: #new-user-modal")
    )

    # Create new user modal
    new_user_modal = Modal(
        ModalHeader(H3("Create New User")),
        ModalBody(
            Form(
                Grid(
                    Hidden(id='user_id', value='-1'),
                    FormSectionDiv(
                        LabelInput('Username', id='user_name', required=True),
                        HelpText('Redshift username (required)')
                    ),
                    FormSectionDiv(
                        LabelInput('Password', id='password', type='password', required=True),
                        HelpText('User password (required)')
                    ),
                ),
                # H4('Basic Properties', cls='mt-6 mb-4'),
                Grid(
                    fhCheckboxX(id='super_user', label='Super User', cls='uk-checkbox'),
                    fhCheckboxX(id='can_create_db', label='Create DB', cls='uk-checkbox'),
                    cols=3
                ),
                DividerSplit(cls='my-4'),
                # Alert(
                #     DivLAligned(
                #         UkIcon('info'),
                #         P('Creating a user will execute SQL commands in your Redshift cluster. You can configure additional properties after creation.')
                #     ),
                #     cls=AlertT.info
                # ),
                DivFullySpaced(
                    ModalCloseButton("Cancel", cls=ButtonT.default, data_uk_toggle="target: #new-user-modal"),
                    Button('Create User', id='btn-create-user', cls=ButtonT.primary, data_uk_toggle="target: #new-user-modal"),
                    Loading((LoadingT.bars, LoadingT.lg, 'mx-4'), htmx_indicator=True),
                ),
                cls='space-y-6',
                action='/user/create', method='post',
                hx_disabled_elt='#btn-create-user'
            )
        ),
        id='new-user-modal'
    )

    card = Card((ctrls, tbl), header=card_header, id='users-table', cls='w-full lg:w-4/5 mb-6')
    list_script = Script(f"new List('users-table', {{ valueNames: {json.dumps(tbl_headers)} }})")

    return card, list_script, new_user_modal
    # return DivVStacked(card, list_script, new_user_modal)

# ===== User Management =====

# === User Properties ===
def mk_user_props(user :RedshiftUser):
    user_props_frm = Div(
                H4('User Properties', cls='mb-4'),
                Form(
                    Hidden(id='user_id', value=user.user_id), Hidden(id='user_name', value=user.user_name),
                    Hidden(id='can_update_catalog', value=user.can_update_catalog),
                    FormLabel(f'Last DDL Time: {user.last_ddl_time}'),
                    Grid(
                        fhCheckboxX(id='super_user', label='Super User', cls='uk-checkbox'),
                        fhCheckboxX(id='can_create_db', label='Create DB', cls='uk-checkbox'),
                        # fhCheckboxX(id='can_update_catalog', label='Update Catalog', 
                        #             cls=('uk-checkbox', LabelT.secondary), disabled='', hidden=''),
                        cols=3 
                    ),
                    Grid(
                        FormSectionDiv(LabelInput('Connection Limit', type='number', id='connection_limit'),
                                        HelpText('0 for unlimited')),
                        FormSectionDiv(LabelInput('Session Timeout', type='number', 
                                                   min=60, max='1728000', id='session_timeout'),
                                       HelpText('Seconds - 60 to 1728000 (20 days)')), 
                        FormSectionDiv(LabelSelect(
                                Option('RESTRICTED', value='RESTRICTED', selected=(user.syslog_access == 'RESTRICTED')), 
                                Option('UNRESTRICTED', value='UNRESTRICTED', selected=(user.syslog_access == 'UNRESTRICTED')),
                                label='System Log Access', id='syslog_access'),
                                HelpText('UNRESTRICTED: View all logs, RESTRICTED: Only own logs')),
                        FormSectionDiv(LabelInput('Password Expiry', type='date', id='password_expiry'),
                                        HelpText('Password expires on 00:00 hours of selected date')),
                    ),
                    Button('Save User Properties', id='btn-props', cls=ButtonT.primary),
                    Loading((LoadingT.bars, LoadingT.lg, 'mx-4'), htmx_indicator=True),
                    cls='space-y-6',
                    hx_post='/user/save-props',
                    hx_target="#user-props",
                    hx_disabled_elt='#btn-props'
                )
            )
    return fill_form(user_props_frm, user)

# === User Groups ===
def mk_user_groups(user: RedshiftUser, all_groups: list):
    user_groups_frm = Div(
                DivHStacked(H4('Groups', cls='mb-4'), Loading((LoadingT.bars, LoadingT.lg, 'mx-4'), htmx_indicator=True)),
                Form(
                    Hidden(id='user_id', value=user.user_id), Hidden(id='user_name', value=user.user_name),
                    Hidden(id='super_user', value=user.super_user),
                    Hidden(id='group_list_id', value='ugroup-list'),
                    ListAddRemove(*SelectOptions(all_groups), items=user.groups, placeholder='Select Group', 
                                  id='ugroup-select', ls_id='ugroup-list', 
                                  add_hx_post='/user/add-group', remove_hx_post='/user/remove-group'),
                    Button('Save Groups', id='btn-save-groups', cls=ButtonT.primary),
                    Loading((LoadingT.bars, LoadingT.lg, 'mx-4'), htmx_indicator=True),
                    cls='space-y-6', hx_post='/user/save-groups', hx_swap='none', 
                    hx_disabled_elt='#btn-save-groups'
                )
            )
    return fill_form(user_groups_frm, user)

# === User Roles ===
def mk_user_roles(user: RedshiftUser, all_roles: list):
    user_roles_frm = Div(
                DivHStacked(H4('Roles', cls='mb-4'), Loading((LoadingT.bars, LoadingT.lg, 'mx-4'), htmx_indicator=True)),
                Form(
                    Hidden(id='user_id', value=user.user_id), Hidden(id='user_name', value=user.user_name),
                    Hidden(id='super_user', value=user.super_user),
                    Hidden(id='role_list_id', value='urole-list'),
                    ListAddRemove(*SelectOptions(all_roles), items=user.roles, placeholder='Select Role', 
                                  id='urole-select', ls_id='urole-list', 
                                  add_hx_post='/user/add-role', remove_hx_post='/user/remove-role'),
                    Button('Save Roles', id='btn-save-roles', cls=ButtonT.primary),
                    Loading((LoadingT.bars, LoadingT.lg, 'mx-4'), htmx_indicator=True),
                    cls='space-y-6', hx_post='/user/save-roles', hx_swap='none',
                    hx_disabled_elt='#btn-save-roles'
                )
            )
    return fill_form(user_roles_frm, user)

# === User Privileges ===
# Helper method to create schema content for a specific schema
def mk_user_schema_content(schema: str, schema_privileges: dict, schema_relations: dict):
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
        # Add hidden fields to track existing tables
        *[Hidden(id=f'table-row-{schema}-{table_name}', value='exists') for table_name in existing_tables],
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
                    Select(*SelectOptions(tables), id=f'new-table-{schema}', name=f'new-table-{schema}', 
                        placeholder='Select Table'),
                    Button('Load Table', id=f'btn-load-table-{schema}', cls=(ButtonT.secondary, ButtonT.sm)), 
                ),
                cls='space-x-2'
            ),
            id=f'new-table-privileges-{schema}', cls='mb-4',
            hx_post=f'/user/load-table/{schema}',
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
        # Add hidden fields to track existing views
        *[Hidden(id=f'view-row-{schema}-{view_name}', value='exists') for view_name in existing_views],
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
                    Select(*SelectOptions(views), id=f'new-view-{schema}', placeholder='Select View'),
                    Button('Load View', id=f'btn-load-view-{schema}', cls=(ButtonT.secondary, ButtonT.sm)),
                ),
                cls='space-x-2'
            ),
            id=f'new-view-privileges-{schema}', cls='mb-4',
            hx_post=f'/user/load-view/{schema}',
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
        # Add hidden fields to track existing functions
        *[Hidden(id=f'func-row-{schema}-{func_name}', value='exists') for func_name in existing_funcs],
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
            hx_post=f'/user/load-function/{schema}',
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
def get_user_schema_content(user: RedshiftUser, schema: str, schema_relations=None):
    # Group privileges by schema and object
    privileges_by_schema = {}
    for privilege in user.privileges:
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
    return mk_user_schema_content(schema, schema_privileges, schema_relations)

def mk_user_schema_nav(user_id: int, schemas: list, active_schema: str):
    # Create schema nav items
    return NavContainer(
        *[Li(
            A(s),
            hx_get=f'/user/schema-content/{user_id}/{s}',
            hx_target='#schema-content', 
            hx_swap='outerHTML',
            hx_trigger='click',
            hx_disabled_elt=f'input, button',
        ) for s in schemas],
        cls=(NavT.secondary, 'border-r'),
        id='schema-nav'
    )

def mk_user_privileges(user: RedshiftUser, schemas: list, schema_relations=None):
    # Group privileges by schema and object
    privileges_by_schema = {}
    for privilege in user.privileges:
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
    initial_schema_content = get_user_schema_content(user, initial_schema, schema_relations) if initial_schema else Div()
    
    user_privileges_frm = Form(
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
            Hidden(id='user_id', value=user.user_id),
            Hidden(id='user_name', value=user.user_name),
            Grid(
                mk_user_schema_nav(user.user_id, schemas, initial_schema),
                Div(
                    initial_schema_content,
                    id='schema-content-container',
                    cls='col-span-4'
                ),
                cls='space-x-4', cols=5 
            ),
            cls='space-y-6',
        ),
        id='user-privileges-form',
        hx_post='/user/save-privileges',
        hx_swap='none',
        hx_disabled_elt='#btn-save-privileges',
    )
    
    return user_privileges_frm

# ===== Main User Form =====
def mk_user_form(user: RedshiftUser, all_groups: list, all_roles: list, schemas: list=None, schema_relations=None):
    ufrm = Card(
                CardHeader(
                    DivFullySpaced(
                        DivLAligned(
                            H3(f'{user.user_name}', cls=TextT.primary), 
                            P(Output(f'ID: {user.user_id}')),
                        ),
                        LinkButton('All Users', icon='arrow-left', href='/users', cls=ButtonT.default),
                    )
                ),
                CardBody(
                    Div(mk_user_props(user), id='user-props'),
                    DividerSplit(cls='my-4'),

                    Div(mk_user_groups(user, all_groups), id='user-groups'),
                    DividerSplit(cls='my-4'),

                    Div(mk_user_roles(user, all_roles), id='user-roles'),
                    DividerSplit(cls='my-4'),
                    
                    # Add privileges section if schemas are provided
                    (Div(mk_user_privileges(user, schemas, schema_relations), id='user-privileges') 
                     if schemas else '')
                )
        )

    return ufrm
