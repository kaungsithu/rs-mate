"""User service for business logic operations."""
from redshift.user import RedshiftUser
from redshift.database import Redshift


class UserService:
    """Service for user management operations."""

    def __init__(self, rs: Redshift):
        """Initialize user service with Redshift connection."""
        self.rs = rs

    def get_all_users(self) -> list:
        """Get all users."""
        return RedshiftUser.get_all(self.rs)

    def get_user(self, user_id: int) -> RedshiftUser:
        """Get user by ID."""
        return RedshiftUser.get_user(user_id, self.rs)

    def create_user(self, user: RedshiftUser) -> RedshiftUser:
        """Create a new user."""
        return RedshiftUser.create_user(user, rs=self.rs)

    def update_user(self, user: RedshiftUser) -> bool:
        """Update user properties."""
        return user.update(self.rs)

    def delete_user(self, user_id: int) -> bool:
        """Delete user by ID."""
        user = self.get_user(user_id)
        if user:
            return user.delete(self.rs)
        return False

    def add_user_to_group(self, user: RedshiftUser, group_name: str) -> RedshiftUser:
        """Add user to a group."""
        user.groups = set(user.groups) | {group_name}
        return user

    def remove_user_from_group(self, user: RedshiftUser, group_name: str) -> RedshiftUser:
        """Remove user from a group."""
        user.groups = set(user.groups) - {group_name}
        return user

    def save_user_groups(self, user: RedshiftUser) -> bool:
        """Save user group memberships."""
        return user.save_groups(self.rs)

    def add_user_to_role(self, user: RedshiftUser, role_name: str) -> RedshiftUser:
        """Add user to a role."""
        user.roles = set(user.roles) | {role_name}
        return user

    def remove_user_from_role(self, user: RedshiftUser, role_name: str) -> RedshiftUser:
        """Remove user from a role."""
        user.roles = set(user.roles) - {role_name}
        return user

    def save_user_roles(self, user: RedshiftUser) -> bool:
        """Save user role memberships."""
        return user.save_roles(self.rs)

    def compute_privilege_changes(self, user: RedshiftUser, selected_privileges: list) -> tuple:
        """Compute which privileges need to be granted and revoked.

        Args:
            user: User object with current privileges
            selected_privileges: List of privileges user should have

        Returns:
            Tuple of (privileges_to_grant, privileges_to_revoke)
        """
        current_privileges = user.privileges if user else []
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

    def apply_privilege_changes(self, user: RedshiftUser, privileges_to_grant: list,
                               privileges_to_revoke: list) -> tuple:
        """Apply privilege changes to user.

        Args:
            user: User object
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
            if user.revoke_privilege(
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
            if user.grant_privilege(
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
