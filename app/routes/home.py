from fasthtml.common import *
from app import app, rt
from redshift.database import Redshift
from helpers.session_helper import *
from components import *
from starlette.responses import RedirectResponse

# Home, DB info form
@rt('/')
def get(session):
    session.clear()
    return MainLayout(mk_db_frm(), nav_btns=False)

# Connect to Redshift, show Nav, User Table
@rt('/')
def post(session, rs: Redshift):
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
