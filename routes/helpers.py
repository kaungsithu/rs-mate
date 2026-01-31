"""
Shared helpers and utilities for route handlers.
"""
from redshift.database import Redshift
from redshift.user import RedshiftUser
from redshift.role import RedshiftRole
from helpers.session_helper import sess_get_obj, sess_store_obj


def get_rs(session) -> Redshift:
    """Get the Redshift connection from session."""
    return sess_get_obj(session, 'redshift')


def set_rs(session, rs: Redshift):
    """Store the Redshift connection in session."""
    sess_store_obj(session, 'redshift', rs)


def get_role(session) -> RedshiftRole:
    """Get the current role from session."""
    return sess_get_obj(session, 'rsrole')


def set_role(session, role: RedshiftRole):
    """Store the current role in session."""
    sess_store_obj(session, 'rsrole', role)


def add_toast(session, message: str, toast_type: str = 'info', persist: bool = False):
    """Add a toast notification to the session."""
    if 'toasts' not in session:
        session['toasts'] = []
    session['toasts'].append({
        'message': message,
        'type': toast_type,
        'persist': persist
    })


def is_connected(session) -> bool:
    """Check if user is connected to Redshift."""
    return get_rs(session) is not None
