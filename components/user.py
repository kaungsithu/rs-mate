"""User management components (backward compatibility wrapper).

This module is maintained for backward compatibility.
New code should import from components.user submodules directly:
- from components.user.list import mk_user_table
- from components.user.form import mk_user_form, mk_user_props
- from components.user.privileges import mk_user_privileges
"""
# Re-export all user components for backward compatibility
from components.user import (
    mk_delete_user_modal, mk_user_link, mk_user_table,
    mk_user_props, mk_user_groups, mk_user_roles, mk_user_form,
    mk_user_schema_content, get_user_schema_content, mk_user_schema_nav, mk_user_privileges
)

__all__ = [
    'mk_delete_user_modal', 'mk_user_link', 'mk_user_table', 'mk_user_props',
    'mk_user_groups', 'mk_user_roles', 'mk_user_privileges',
    'mk_user_schema_content', 'get_user_schema_content', 'mk_user_schema_nav', 'mk_user_form'
]
