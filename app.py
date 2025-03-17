from dataclasses import Field
from fasthtml.common import *
from redshift import DBInfo, store_db_info, test_conn
from user import RedshiftUser
from pico_customs import css
from helper import session_store_obj, session_get_obj

hdrs = (picolink, css)

app, rt = fast_app(hdrs=hdrs, htmlkw={'data-theme': 'light'}, debug=True, live=True)
setup_toasts(app)

def mk_db_frm(db_info=None):
    db_frm = Form(
            Input(id='host', placeholder='Database Host'),
            Input(id='port', placeholder='Database Port', ),
            Input(id='name', placeholder='Database Name'),
            Input(id='user', placeholder='Username'),
            Input(id='pwd', type='password', placeholder='Password'),
            Button('Connect'),
            hx_post='/', target_id='app-area'
        )
    
    if not db_info:
        db_info = DBInfo(host=None, port=5439, name='dev', user=None, pwd=None)
    else:
        db_info.pwd = None

    fill_form(db_frm, db_info)
    
    return Card(db_frm, header=H3('Redshift Connection Info'), footer=PicoBusy())

# Home, DB info form
@rt('/')
def get(session):
    return Title('RS-Mate'), Container(
        Div(mk_db_frm(), id='app-area'),

        Div(mk_user_form(RedshiftUser(
            user_id=1, user_name='test', super_user=True, groups=['group1', 'group2'], roles=['role1', 'role2']
        )))
    )

def mk_btn_bar(active_btn:str=None, **kw):
    btn_users_cls = btn_roles_cls = btn_perm_cls = 'outline contrast'
    if active_btn == 'users': btn_users_cls = 'outline'
    if active_btn == 'roles': btn_roles_cls = 'outline'
    if active_btn == 'perm': btn_perm_cls = 'outline'

    btn_bar = Div(
                    Button('Manage Users', PicoBusy(), id='btn-users', hx_get='/users', hx_target='#content-area', cls=btn_users_cls),
                    Nbsp(), Nbsp(),
                    Button('Manage Roles', id='btn-roles', cls=btn_roles_cls),
                    Nbsp(), Nbsp(),
                    Button('Manage Permissions', id='btn-perm', cls=btn_perm_cls),
                    id='btn-bar', **kw
                )
    return btn_bar

# Connect to Redshift, show control buttons
@rt('/')
def post(session, db:DBInfo):
    if not (db.host and db.port and db.name and db.user and db.pwd):
        add_toast(session, 'All connection fields are required!', 'error')
        return mk_db_frm(db)

    if not test_conn(db):
        add_toast(session, 'There was a problem connecting to Redshift!', 'error')
        return mk_db_frm(db)
    store_db_info(db, session)

    return mk_btn_bar(), Div(None, id='content-area')

@rt('/user-groups/{user_id}')
def get(session, user_id:int):
    groups = RedshiftUser.get_user_groups(user_id, session)

    user = session_get_obj(session, f'user-{user_id}', RedshiftUser)
    user.groups = groups
    session_store_obj(session, f'user-{user_id}', user)

    return ", ".join(groups) if groups else "-" 

# Get user roles for each user
@rt('/user-roles/{user_id}')
def get(session, user_id:int):
    roles = RedshiftUser.get_user_roles(user_id, session)

    user = session_get_obj(session, f'user-{user_id}', RedshiftUser)
    user.roles = roles
    session_store_obj(session, f'user-{user_id}', user)

    return ", ".join(roles) if roles else "-" 

def mk_user_table(session):
    users = RedshiftUser.get_all(session)

    if users is None or len(users) == 0:
        return Div(H3('No users found in Redshift.'))
    
    # keep users in session
    map(session_store_obj, users, [f'user-{user.user_id}' for user in users])

    rows = []
    for user in users:
        rows.append(
            Tr(Td(user.user_id), 
               Td(A(user.user_name, hx_get=f'/users/{user.user_id}')),
               Td("✅" if user.super_user else "-"),
               Td(PicoBusy(), hx_get=f'/user-groups/{user.user_id}', hx_trigger='revealed'),
               Td(PicoBusy(), hx_get=f'/user-roles/{user.user_id}', hx_trigger='revealed')
            )
        )
    headers = ['ID', 'Username', 'Super', 'Groups', 'Roles']
    tbl = Table(
                Thead(Tr(*map(Th, headers))),
                Tbody(*rows),
                title='Redshift Users',
                cls='striped'
            )
    return Div(tbl)

@rt('/users')
def get(session):
    return mk_user_table(session), mk_btn_bar('users', hx_swap_oob='true')


def mk_user_form(user):
    ufrm = Card(
                Form(
                    Input(id='user_id', type='hidden'),
                    Grid(
                        Fieldset(CheckboxX(user.super_user, 'Super User', role='switch')),
                        Fieldset(CheckboxX(user.can_create_db, 'Create DB', role='switch')),
                        Fieldset(CheckboxX(user.can_update_catalog, 'Update Catalog', role='switch')),
                        Div()
                    ),
                    Fieldset(
                        Label('Password Expiry ', 
                                CheckboxX(user.password_expiry, '', role='switch', id='password_expiry_enabled'),
                                Input(id='password_expiry', type='date'), 
                        style='margin-top:1em;')), 
                    Fieldset(
                        Label('Connection Limit', 
                            CheckboxX(user.connection_limit, '', role='switch', id='connection_limit_enabled'),
                            Input(id='connection_limit'))),  
                Card(
                    Ul(*[Li(group) for group in user.groups]),
                    header=H4('Groups')
                ),
                Card(
                    Ul(*[Li(role) for role in user.roles]),
                header=H4('Roles')
            ),
                ),
        header=H3(f'Manage User: {user.user_id} - {user.user_name}'),
        footer=Div(Button('Save'))
    )

    return ufrm

@rt('/users/{user_id}:int')
def get(session, user_id):
    user = session_get_obj(session, f'user-{user_id}', RedshiftUser)





if __name__ == "__main__":
    try: serve()
    except KeyboardInterrupt: pass
    finally:
        sys.exit(0)