"""User form and properties components."""
from fasthtml.common import *
from monsterui.all import *
from redshift.user import RedshiftUser
from helpers import *
from fasthtml.common import CheckboxX as fhCheckboxX
from components.common import *

__all__ = ['mk_user_props', 'mk_user_groups', 'mk_user_roles', 'mk_user_form']


def mk_user_props(user: RedshiftUser):
    """Create user properties form."""
    user_props_frm = Div(
                H4('User Properties', cls='mb-4'),
                Form(
                    Hidden(id='user_id', value=user.user_id), Hidden(id='user_name', value=user.user_name),
                    Hidden(id='can_update_catalog', value=user.can_update_catalog),
                    FormLabel(f'Last DDL Time: {user.last_ddl_time}'),
                    Grid(
                        fhCheckboxX(id='super_user', label='Super User', cls='uk-checkbox'),
                        fhCheckboxX(id='can_create_db', label='Create DB', cls='uk-checkbox'),
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


def mk_user_groups(user: RedshiftUser, all_groups: list):
    """Create user groups form."""
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


def mk_user_roles(user: RedshiftUser, all_roles: list):
    """Create user roles form."""
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


def mk_user_form(user: RedshiftUser, all_groups: list, all_roles: list, schemas: list=None, schema_relations=None):
    """Create main user form combining properties, groups, roles, and privileges."""
    from components.user.privileges import mk_user_privileges

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

                    (Div(mk_user_privileges(user, schemas, schema_relations), id='user-privileges')
                     if schemas else '')
                )
        )

    return ufrm
