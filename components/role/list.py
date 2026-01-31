"""Role list and table components."""
from fasthtml.common import *
from monsterui.all import *
import json
from redshift.role import RedshiftRole
from helpers.session_helper import *
from components.common import *

__all__ = ['mk_delete_role_modal', 'mk_role_link', 'mk_role_table']


def mk_delete_role_modal(role_name):
    """Create a delete confirmation modal for a role."""
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
    """Create a link to role detail page, or muted text if system role."""
    if role.role_id >= 200_000:
        return A(role.role_name, href=f'/role/{role.role_name}', cls='text-blue-500')
    else:
        return A(role.role_name, href='#', cls=TextT.muted)


def mk_role_table(roles: list=None):
    """Create role table with filtering and create modal."""
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
