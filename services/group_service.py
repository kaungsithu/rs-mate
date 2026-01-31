"""Group service for business logic operations."""
from redshift.group import RedshiftGroup
from redshift.database import Redshift


class GroupService:
    """Service for group management operations."""

    def __init__(self, rs: Redshift):
        """Initialize group service with Redshift connection."""
        self.rs = rs

    def get_all_groups(self) -> list:
        """Get all groups."""
        return RedshiftGroup.get_all(self.rs)

    def get_group(self, group_name: str) -> RedshiftGroup:
        """Get group by name."""
        return RedshiftGroup.get_group(group_name, self.rs)

    def create_group(self, group_name: str) -> RedshiftGroup:
        """Create a new group."""
        return RedshiftGroup.create_group(group_name, self.rs)

    def delete_group(self, group_name: str) -> bool:
        """Delete group by name."""
        group = self.get_group(group_name)
        if group:
            return group.delete(self.rs)
        return False

    def add_user_to_group(self, group: RedshiftGroup, user_name: str) -> RedshiftGroup:
        """Add user to a group."""
        group.users = set(group.users) | {user_name}
        return group

    def remove_user_from_group(self, group: RedshiftGroup, user_name: str) -> RedshiftGroup:
        """Remove user from a group."""
        group.users = set(group.users) - {user_name}
        return group

    def save_group_users(self, group: RedshiftGroup) -> bool:
        """Save group user memberships."""
        return group.update_users(group.users, self.rs)
