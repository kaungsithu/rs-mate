"""
Database connection routes.
"""
from fasthtml.common import RedirectResponse
from redshift.database import Redshift
from components.database import mk_db_frm
from components.common import MainLayout
from routes.helpers import set_rs, add_toast


def register_routes(app):
    """Register all database connection routes."""

    @app.rt('/')
    def get(session):
        """Show database connection form."""
        session.clear()
        return MainLayout(mk_db_frm(), nav_btns=False)

    @app.rt('/')
    def post(session, rs: Redshift):
        """Connect to Redshift and redirect to users page."""
        session.clear()
        if not (rs.host and rs.port and rs.name and rs.user and rs.pwd):
            add_toast(session, 'All connection fields are required!', 'error', True)
            return RedirectResponse('/', status_code=303)

        if not rs.test_conn():
            add_toast(session, 'There was a problem connecting to Redshift!', 'error', True)
            return RedirectResponse('/', status_code=303)

        set_rs(session, rs)
        session['active_btn'] = 'users'

        return RedirectResponse('/users', status_code=303)
