"""Role management components (backward compatibility wrapper).

This module is maintained for backward compatibility.
New code should import from components.role submodules directly:
- from components.role.list import mk_role_table
- from components.role.form import mk_role_form, mk_role_nested_roles
- from components.role.privileges import mk_role_privileges
"""
# Re-export all role components for backward compatibility
from components.role import (
    mk_delete_role_modal, mk_role_link, mk_role_table, mk_role_nested_roles,
    mk_schema_content, get_schema_content, mk_schema_nav, mk_role_privileges, mk_role_form
)

__all__ = [
    'mk_delete_role_modal', 'mk_role_link', 'mk_role_table', 'mk_role_nested_roles',
    'mk_schema_content', 'get_schema_content', 'mk_schema_nav', 'mk_role_privileges', 'mk_role_form'
]
