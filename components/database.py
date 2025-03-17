from fasthtml.common import *
from monsterui.all import *
from components.common import MainLayout
from redshift.database import Redshift

# ===== Database Connection Form =====
def mk_db_frm(rs: Redshift = None):
    db_frm = Form(
                Card(
                    LabelInput('Host', id='host', placeholder='Database Host'),
                    LabelInput('Port', id='port', placeholder='Database Port'),
                    LabelInput('Database', id='name', placeholder='Database Name'),
                    LabelInput('Username', id='user', placeholder='Username'),
                    LabelInput(
                        'Password', id='pwd', type='password', placeholder='Password'
                    ),
                    header=(
                        H3('Connect Redshift'),
                        Subtitle('Enter the Redshift connection details'),
                        DividerLine(),
                    ),
                    footer=(Button('Connect', id='btn-connect', cls=ButtonT.primary),
                            Loading((LoadingT.bars, LoadingT.lg, 'mx-4'), htmx_indicator=True)               
                    ),
                ),
                # hx_post='/', target_id='app-area',
                action='/', method='post',
                hx_disabled_elt='#btn-connect',
                cls='w-full md:w-2/3 lg:w-1/2',
            )
    return fill_form(db_frm, rs or Redshift())

