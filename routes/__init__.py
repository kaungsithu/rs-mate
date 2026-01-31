"""
Route modules for RSMate application.
This package contains all HTTP route handlers organized by feature area.
"""
from routes import database, user, user_privileges, role, role_privileges, group


def register_all_routes(app):
    """Register all routes with the FastHTML application."""
    database.register_routes(app)
    user.register_routes(app)
    user_privileges.register_routes(app)
    role.register_routes(app)
    role_privileges.register_routes(app)
    group.register_routes(app)
