"""User list and table components."""
from fasthtml.common import *
from monsterui.all import *
import json
from redshift.user import RedshiftUser
from helpers import *
from components.common import *

__all__ = ['mk_delete_user_modal', 'mk_user_link', 'mk_user_table']


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
    """Create a link to user detail page, or muted text if system user."""
    if user.user_id > 100:
        return A(user.user_name, href=f'/user/{user.user_id}', cls='text-blue-500')
    else:
        return A(user.user_name, href='#', cls=TextT.muted)


def mk_user_table(users: RedshiftUser=None):
    """Create user table with filtering and create modal."""
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
                Grid(
                    CheckboxX(id='super_user', label='Super User', cls='uk-checkbox'),
                    CheckboxX(id='can_create_db', label='Create DB', cls='uk-checkbox'),
                    cols=3
                ),
                DividerSplit(cls='my-4'),
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
