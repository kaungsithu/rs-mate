"""Role service for business logic operations."""
from redshift.role import RedshiftRole
from redshift.database import Redshift


class RoleService:
    """Service for role management operations."""

    def __init__(self, rs: Redshift):
        """Initialize role service with Redshift connection."""
        self.rs = rs

    def get_all_roles(self) -> list:
        """Get all roles."""
        return RedshiftRole.get_all(self.rs)

    def get_role(self, role_name: str) -> RedshiftRole:
        """Get role by name."""
        return RedshiftRole.get_role(role_name, self.rs)

    def create_role(self, role_name: str) -> RedshiftRole:
        """Create a new role."""
        return RedshiftRole.create_role(role_name, self.rs)

    def delete_role(self, role_name: str) -> bool:
        """Delete role by name."""
        role = self.get_role(role_name)
        if role:
            return role.delete(self.rs)
        return False

    def add_nested_role(self, role: RedshiftRole, nested_role_name: str) -> RedshiftRole:
        """Add a nested role to a role."""
        role.nested_roles = set(role.nested_roles) | {nested_role_name}
        return role

    def remove_nested_role(self, role: RedshiftRole, nested_role_name: str) -> RedshiftRole:
        """Remove a nested role from a role."""
        role.nested_roles = set(role.nested_roles) - {nested_role_name}
        return role

    def save_nested_roles(self, role: RedshiftRole) -> bool:
        """Save role nested role memberships."""
        return role.update_nested_roles(role.nested_roles, self.rs)

    def compute_privilege_changes(self, role: RedshiftRole, selected_privileges: list) -> tuple:
        """Compute which privileges need to be granted and revoked.

        Args:
            role: Role object with current privileges
            selected_privileges: List of privileges role should have

        Returns:
            Tuple of (privileges_to_grant, privileges_to_revoke)
        """
        current_privileges = role.privileges if role else []
        privileges_to_grant = []
        privileges_to_revoke = []

        # Find privileges to grant (selected but not in current)
        for selected in selected_privileges:
            found = False
            for current in current_privileges:
                if (selected['schema_name'] == current['schema_name'] and
                    selected['object_name'] == current['object_name'] and
                    selected['privilege_type'] == current['privilege_type']):
                    found = True
                    break
            if not found:
                privileges_to_grant.append(selected)

        # Find privileges to revoke (in current but not selected)
        for current in current_privileges:
            found = False
            for selected in selected_privileges:
                if (current['schema_name'] == selected['schema_name'] and
                    current['object_name'] == selected['object_name'] and
                    current['privilege_type'] == selected['privilege_type']):
                    found = True
                    break
            if not found:
                privileges_to_revoke.append(current)

        return privileges_to_grant, privileges_to_revoke

    def apply_privilege_changes(self, role: RedshiftRole, privileges_to_grant: list,
                               privileges_to_revoke: list) -> tuple:
        """Apply privilege changes to role.

        Args:
            role: Role object
            privileges_to_grant: List of privileges to grant
            privileges_to_revoke: List of privileges to revoke

        Returns:
            Tuple of (success: bool, granted_count: int, revoked_count: int)
        """
        success = True
        granted_count = 0
        revoked_count = 0

        # Revoke privileges
        for privilege in privileges_to_revoke:
            if role.revoke_privilege(
                privilege['schema_name'],
                privilege['object_name'],
                privilege['object_type'],
                privilege['privilege_type'],
                self.rs
            ):
                revoked_count += 1
            else:
                success = False

        # Grant privileges
        for privilege in privileges_to_grant:
            if role.grant_privilege(
                privilege['schema_name'],
                privilege['object_name'],
                privilege['object_type'],
                privilege['privilege_type'],
                self.rs
            ):
                granted_count += 1
            else:
                success = False

        return success, granted_count, revoked_count
