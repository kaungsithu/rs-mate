from fasthtml.common import *
from monsterui.all import *
import json
from redshift.group import RedshiftGroup
from helpers.session_helper import *
from components.common import *

__all__ = [
    'mk_delete_group_modal', 'mk_group_link', 'mk_group_table', 'mk_group_users', 'mk_group_form'
]

# ===== Group list table =====

def mk_delete_group_modal(group_name):
    """Create a delete confirmation modal for a group"""
    delete_btn_id = f'delete-btn-{group_name}'
    return Modal(
        ModalHeader(H3(f"Delete Group: {group_name}")),
        ModalBody(
            P(f"Are you sure you want to delete group {group_name}?", cls=TextPresets.muted_lg),
            DivFullySpaced(
                Button("Cancel", cls=ButtonT.ghost, data_uk_toggle=f"target: #delete-group-modal-{group_name}"),
                DivLAligned(
                    Button("Delete", id=delete_btn_id, cls=ButtonT.destructive, 
                           hx_delete=f'/group/{group_name}',
                           hx_target=f'#group-row-{group_name}',
                           hx_swap='outerHTML',
                           hx_disabled_elt=f'#{delete_btn_id}',
                           data_uk_toggle=f"target: #delete-group-modal-{group_name}"),
                    Loading((LoadingT.bars, LoadingT.sm, 'ml-2'), htmx_indicator=True)
                )
            )
        ),
        id=f'delete-group-modal-{group_name}'
    )

def mk_group_link(group: RedshiftGroup):
    return A(group.group_name, href=f'/group/{group.group_name}', cls='text-blue-500')

def mk_group_table(groups: list=None):
    if not groups:
        return Div(H3('No groups retrieved from Redshift.'), cls='mt-10 text-red-400')

    rows = []
    for group in groups:
        rows.append(
            Tr(
                Td(mk_group_link(group), cls='GroupName'),
                Td(
                    Loading((LoadingT.dots, LoadingT.xs), htmx_indicator=True),
                    hx_get=f'/group-users/{group.group_name}',
                    hx_trigger='revealed',
                    cls='Users',
                ),
                Td(
                    Button(UkIcon('trash-2'), cls=(ButtonT.destructive, ButtonT.xs), 
                           data_uk_toggle=f"target: #delete-group-modal-{group.group_name}"),
                    mk_delete_group_modal(group.group_name),
                    cls='Actions'
                ),
                id=f'group-row-{group.group_name}'
            )
        )

    tbl_headers = ['Group Name', 'Users', 'Actions']
    tbl = Table(Thead(Tr(*map(Th, tbl_headers))), Tbody(*rows, cls='list'), cls=(TableT.striped))
    card_header=(H4('Redshift Groups'), Subtitle('Click on each group name to manage group details'))
    ctrls = DivFullySpaced(
                Div(Input(cls='w-sm search', placeholder='Filter groups...')),
                Button(UkIcon('plus'), 'Add Group', 
                       cls=ButtonT.primary,
                       data_uk_toggle="target: #new-group-modal")
    )

    # Create new group modal
    new_group_modal = Modal(
        ModalHeader(H3("Create New Group")),
        ModalBody(
            Form(
                FormSectionDiv(
                    LabelInput('Group Name', id='group_name', required=True),
                    HelpText('Redshift group name (required)')
                ),
                DividerSplit(cls='my-4'),
                DivFullySpaced(
                    Button("Cancel", cls=ButtonT.default, data_uk_toggle="target: #new-group-modal"),
                    Button('Create Group', id='btn-create-group', cls=ButtonT.primary, data_uk_toggle="target: #new-group-modal"),
                    Loading((LoadingT.bars, LoadingT.lg, 'mx-4'), htmx_indicator=True),
                ),
                cls='space-y-6',
                action='/group/create', method='post',
                hx_disabled_elt='#btn-create-group'
            )
        ),
        id='new-group-modal'
    )

    card = Card(ctrls, tbl, header=card_header, id='groups-table', cls='w-full lg:w-4/5 mb-6')
    list_script = Script(f"new List('groups-table', {{ valueNames: {json.dumps(tbl_headers)} }})")

    return DivVStacked(card, list_script, new_group_modal, cls='w-full lg:w-4/5')

# ===== Group Management =====

# === Group Users ===
def mk_group_users(group: RedshiftGroup, all_users: list):
    group_users_frm = Form(
                DivFullySpaced(
                    H4('Users'), 
                    Loading((LoadingT.bars, LoadingT.lg, 'mx-4'), htmx_indicator=True),
                    DivRAligned(
                        Button('Save Users', id='btn-save-users', cls=ButtonT.primary),
                        cls='space-x-2'
                    ),
                    cls='space-y-2'
                ),
                Div(
                    Hidden(id='group_name', value=group.group_name),
                    Hidden(id='user_list_id', value='user-list'),
                    ListAddRemove(*SelectOptions([u.user_name for u in all_users]), 
                                  items=group.users, placeholder='Select User', 
                                  id='user-select', ls_id='user-list', 
                                  add_hx_post='/group/add-user', remove_hx_post='/group/remove-user'),
                    cls='space-y-4', 
                ),
                id='group-users-form',
                hx_post='/group/save-users', hx_swap='none',
                hx_disabled_elt='#btn-save-users'
            )
    return fill_form(group_users_frm, group)

# ===== Main Group Form =====
def mk_group_form(group: RedshiftGroup, all_users: list):
    gfrm = Card(
                CardHeader(
                    DivFullySpaced(
                        DivLAligned(
                            H3(f'{group.group_name}', cls=TextT.primary),
                        ),
                        LinkButton('All Groups', icon='arrow-left', href='/groups', cls=ButtonT.default),
                    )
                ),
                CardBody(
                    Div(mk_group_users(group, all_users), id='group-users'),
                ),
                cls='w-full lg:w-4/5 mb-6'
        )

    return gfrm
