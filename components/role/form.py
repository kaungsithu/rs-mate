"""Role form components."""
from fasthtml.common import *
from monsterui.all import *
from redshift.role import RedshiftRole
from helpers.session_helper import *
from components.common import *

__all__ = ['mk_role_nested_roles', 'mk_role_form']


def mk_role_nested_roles(role: RedshiftRole, all_roles: list):
    """Create role nested roles form."""
    role_nested_roles_frm = Form(
                DivFullySpaced(
                    H4('Nested Roles'),
                    Loading((LoadingT.bars, LoadingT.lg, 'mx-4'), htmx_indicator=True),
                    DivRAligned(
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
                    cls='space-y-4',
                ),
                id='role-nested-roles-form',
                hx_post='/role/save-nested-roles', hx_swap='none',
                hx_disabled_elt='#btn-save-nested-roles'
            )
    return fill_form(role_nested_roles_frm, role)


def mk_role_form(role: RedshiftRole, all_roles: list, schemas: list, schema_relations=None):
    """Create main role form combining nested roles and privileges."""
    from components.role.privileges import mk_role_privileges

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
