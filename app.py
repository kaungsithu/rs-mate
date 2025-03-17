from fasthtml.common import *
from fasthtml.common import CheckboxX as fhCheckboxX
from redshift import DBInfo, store_db_info, test_conn
from user import RedshiftUser
from helper import session_store_obj, session_get_obj
from monsterui.all import *
import json

# listjs
listjs = Script(src='https://cdnjs.cloudflare.com/ajax/libs/list.js/2.3.1/list.min.js')

# hdrs = (picolink, css)
hdrs = (Theme.violet.headers(mode='light'), listjs)


app, rt = fast_app(hdrs=hdrs, debug=True, live=True)
setup_toasts(app)


def mk_db_frm(db_info=None):
    db_frm = DivCentered(
        Form(
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
                        Loading(htmx_indicator=True, cls='mx-4')               
                ),
            ),
            hx_post='/',
            target_id='app-area',
            hx_disabled_elt='#btn-connect',
            cls='w-full md:w-2/3 lg:w-1/2',
        )
    )

    if not db_info:
        db_info = DBInfo(host=None, port=5439, name='dev', user=None, pwd=None)
    else:
        db_info.pwd = None

    fill_form(db_frm, db_info)

    # return Card(db_frm, header=H3('Redshift Connection Info'), footer=PicoBusy())
    return db_frm

def mk_brand(): return DivLAligned(H1('RSMate', cls=TextT.primary))

def mk_nav_bar(session, **kw):
    active_btn = session.get('active_btn')
    btn_users_cls = btn_roles_cls = ButtonT.default
    if active_btn == 'users': btn_users_cls = ButtonT.primary
    if active_btn == 'roles': btn_roles_cls = ButtonT.primary

    return Div(NavBar(
        Button(UkIcon('users'), Nbsp(), 'Users', Nbsp(), Loading(htmx_indicator=True),
               id='btn-users', submit=False,
               hx_get='/users', hx_target='#content-area',
               cls=btn_users_cls),
        Button(UkIcon('user-cog'), Nbsp(), 'Roles', hx_get='/roles', cls=btn_roles_cls),
        Button(UkIcon('arrow-left-right'), Nbsp(), 'Switch Database', hx_get='/'),
        brand=mk_brand(),
    ), id='nav-bar', **kw)

# Home, DB info form
@rt('/')
def get(session):
    return (Title('RSMate'), Container(
            NavBar(None, brand=mk_brand()),
            mk_db_frm(),
            id='app-area',
        ),
        # DividerLine(),
        # Div(
        #     mk_nav_bar(),
        # ),
        # DividerLine(),
        # Div(
        #     mk_user_form(
        #         RedshiftUser(
        #             user_id=1,
        #             user_name='test',
        #             super_user=True,
        #             groups=['group1', 'group2'],
        #             roles=['role1', 'role2'],
        #         )
        #     )
        # ),

    )

# Connect to Redshift, show Nav, User Table
# TODO: Disable updating admin user
@rt('/')
def post(session, db: DBInfo):
    if not (db.host and db.port and db.name and db.user and db.pwd):
        add_toast(session, 'All connection fields are required!', 'error', True)
        return mk_db_frm(db)

    if not test_conn(db):
        add_toast(session, 'There was a problem connecting to Redshift!', 'error', True)
        return mk_db_frm(db)

    store_db_info(db, session)

    session['active_btn'] = 'users'

    return Div(
        mk_nav_bar(session),
        Div(mk_user_table(session), id='content-area'),
    )


@rt('/user-groups/{user_id}')
def get(session, user_id: int):
    groups = RedshiftUser.get_user_groups(user_id, session)

    user = session_get_obj(session, f'user-{user_id}', RedshiftUser)
    user.groups = groups
    session_store_obj(session, f'user-{user_id}', user)

    return ', '.join(groups) if groups else '-'


# Get user roles for each user
@rt('/user-roles/{user_id}')
def get(session, user_id: int):
    roles = RedshiftUser.get_user_roles(user_id, session)

    user = session_get_obj(session, f'user-{user_id}', RedshiftUser)
    user.roles = roles
    session_store_obj(session, f'user-{user_id}', user)

    return ', '.join(roles) if roles else '-'


def mk_user_table(session):
    users = RedshiftUser.get_all(session)

    if users is None or len(users) == 0:
        return DivCentered(H3('No users retrieved from Redshift.'), cls='mt-10 text-red-400')

    rows = []
    for user in users:
        # keep users in session
        session_store_obj(session, f'user-{user.user_id}', user)

        rows.append(
            Tr(
                Td(user.user_id, cls='ID'),
                Td(A(user.user_name, 
                     hx_get=f'/user/{user.user_id}'), 
                     hx_target='#content-area',
                     cls='Username text-blue-500'),
                Td('✅' if user.super_user else '-'),
                Td(
                    Loading((LoadingT.dots, LoadingT.xs), htmx_indicator=True),
                    hx_get=f'/user-groups/{user.user_id}',
                    hx_trigger='revealed',
                    cls='Groups',
                ),
                Td(
                    Loading((LoadingT.dots, LoadingT.xs), htmx_indicator=True),
                    hx_get=f'/user-roles/{user.user_id}',
                    hx_trigger='revealed',
                    cls='Roles',
                ),
            )
        )

    tbl_headers = ['ID', 'Username', 'Super', 'Groups', 'Roles']
    tbl = Table(Thead(Tr(*map(Th, tbl_headers))), Tbody(*rows, cls='list'), cls=(TableT.striped))
    card_header=(H4('Redshift Users'), Subtitle('Click on each username to manage user details'))
    ctrls = DivFullySpaced(
                Div(Input(cls='w-sm search', placeholder='Filter users...')),
                Button(UkIcon('plus'), 'Add User', cls=ButtonT.primary)
    )

    card = Card(ctrls, tbl, header=card_header, id='users-table', cls='mt-4 w-full lg:w-3/4')
    list_script = Script(f"new List('users-table', {{ valueNames: {json.dumps(tbl_headers)} }})")

    return DivCentered(card, list_script)


@rt('/users')
def get(session):
    return Div(
        mk_user_table(session)
    ) 

def FormSectionDiv(*c, cls='space-y-2', **kwargs): return Div(*c, cls=cls, **kwargs)
def HelpText(c): return P(c,cls=TextPresets.muted_sm)

def mk_user_props(session, user:RedshiftUser):
    user_props_frm = Div(
                H4('User Properties', cls='mb-4'),
                Form(
                    Hidden(id='user_id', value=user.user_id), Hidden(id='user_name', value=user.user_name),
                    Hidden(id='can_update_catalog', value=user.can_update_catalog),
                    FormLabel(f'Last DDL Time: {user.last_ddl_time}'),
                    Grid(
                        fhCheckboxX(id='super_user', label='Super User', cls='uk-checkbox'),
                        fhCheckboxX(id='can_create_db', label='Create DB', cls='uk-checkbox'),
                        # fhCheckboxX(id='can_update_catalog', label='Update Catalog', 
                        #             cls=('uk-checkbox', LabelT.secondary), disabled='', hidden=''),
                        cols=3 
                    ),
                    Grid(
                        FormSectionDiv(LabelInput('Connection Limit', type='number', id='connection_limit'),
                                        HelpText('0 for unlimited')),
                        FormSectionDiv(LabelInput('Session Timeout', type='number', 
                                                   min=60, max='1728000', id='session_timeout'),
                                       HelpText('Seconds - 60 to 1728000 (20 days)')), 
                        FormSectionDiv(LabelSelect(
                                Option('RESTRICTED', value='RESTRICTED', selected=(user.syslog_access == 'RESTRICTED')), 
                                Option('UNRESTRICTED', value='UNRESTRICTED', selected=(user.syslog_access == 'UNRESTRICTED')),
                                label='System Log Access', id='syslog_access'),
                                HelpText('UNRESTRICTED: View all logs, RESTRICTED: Only own logs')),
                        FormSectionDiv(LabelInput('Password Expiry', type='date', id='password_expiry'),
                                        HelpText('Password expires on 00:00 hours of selected date')),
                    ),
                    Button('Save User Properties', id='btn-props', cls=ButtonT.primary),
                    Loading(htmx_indicator=True, cls='mx-4'),
                    
                    cls='space-y-6',
                    hx_post='/user/save-props',
                    hx_target="#user-props",
                    hx_disabled_elt='#btn-props'
                )
            )
    return fill_form(user_props_frm, user)

def mk_user_groups(session, user:RedshiftUser):
    user_groups_frm = Div(
                H4('Groups', cls='mb-4'),
                Form(
                    Hidden(id='user_id', value=user.user_id), Hidden(id='user_name', value=user.user_name),
                    
                    Grid(
                        fhCheckboxX(id='super_user', label='Super User', cls='uk-checkbox'),
                        fhCheckboxX(id='can_create_db', label='Create DB', cls='uk-checkbox'),
                        # fhCheckboxX(id='can_update_catalog', label='Update Catalog', 
                        #             cls=('uk-checkbox', LabelT.secondary), disabled='', hidden=''),
                        cols=3 
                    ),
                    Grid(
                        FormSectionDiv(LabelInput('Connection Limit', type='number', id='connection_limit'),
                                        HelpText('0 for unlimited')),
                        FormSectionDiv(LabelInput('Session Timeout', type='number', 
                                                   min=60, max='1728000', id='session_timeout'),
                                       HelpText('Seconds - 60 to 1728000 (20 days)')), 
                        FormSectionDiv(LabelSelect(
                                Option('RESTRICTED', value='RESTRICTED', selected=(user.syslog_access == 'RESTRICTED')), 
                                Option('UNRESTRICTED', value='UNRESTRICTED', selected=(user.syslog_access == 'UNRESTRICTED')),
                                label='System Log Access', id='syslog_access'),
                                HelpText('UNRESTRICTED: View all logs, RESTRICTED: Only own logs')),
                        FormSectionDiv(LabelInput('Password Expiry', type='date', id='password_expiry'),
                                        HelpText('Password expires on 00:00 hours of selected date')),
                    ),
                    Button('Save User Properties', id='btn-props', cls=ButtonT.primary),
                    Loading(htmx_indicator=True, cls='mx-4'),
                    
                    cls='space-y-6',
                    hx_post='/user/save-groups',
                    hx_target="#user-groups",
                    hx_disabled_elt='#btn-groups'
                )
            )
    return fill_form(user_groups_frm, user)


def mk_user_form(session, user):
    ufrm = Card(
                CardHeader(
                    DivFullySpaced(
                        DivLAligned(
                            H3(f'{user.user_name}', cls=TextT.primary), 
                            P(Output(f'ID: {user.user_id}')),
                        ),
                        Button(UkIcon('arrow-left'), 'All Users', 
                               cls=ButtonT.default, 
                               hx_get='/users', hx_target='#content-area'),
                    )
                ),
                CardBody(
                    Div(mk_user_props(session, user), id='user-props'),
                    DividerSplit(cls='mt-4 mb-4'),
                    Div(mk_user_groups(session, user), id='user-groups'),
                )
        )

    return ufrm

# Show user details
@rt('/user/{user_id}')
def get(session, user_id:int):
    user = None 
    try:
        if f'user-{user_id}' in session:
            user = session_get_obj(session, f'user-{user_id}', RedshiftUser)
            if user.syslog_access is None:
                svv_user_info = RedshiftUser.get_svv_user_info(user_id, session)
                user.update_fields(svv_user_info)
                session_store_obj(session, f'user-{user_id}', user)
        else:
            user = RedshiftUser.get_user(user_id, session)
            session_store_obj(session, f'user-{user_id}', user)      
    except Exception as e:
        add_toast(session, f'Error retrieving user with ID: {user_id}', 'error', True)

    return mk_user_form(session, user)

@rt('/user/save-props')
def post(session, user:RedshiftUser):
    try:
        ori_user = session_get_obj(session, f'user-{user.user_id}', RedshiftUser)
    except:
        add_toast(session, f'Error updating user with ID: {user.user_id}', 'error', True)
        return mk_user_props(session, user)
    
    if user.update(ori_user, session):
        session_store_obj(session, f'user-{user.user_id}', user)
        add_toast(session, 'User properties saved successfully!', 'success', True)
    else:
        add_toast(session, 'Error saving user properties!', 'error', True)

    return mk_user_props(session, user)

@rt('/user/save-groups')
def post(session, user:RedshiftUser):
    # try:
    #     ori_user = session_get_obj(session, f'user-{user.user_id}', RedshiftUser)
    # except:
    #     add_toast(session, f'Error updating user with ID: {user.user_id}', 'error', True)
    #     return mk_user_props(session, user)
    
    # if user.update(ori_user, session):
    #     session_store_obj(session, f'user-{user.user_id}', user)
    #     add_toast(session, 'User properties saved successfully!', 'success', True)
    # else:
    add_toast(session, 'two submit btn works', 'success', True)

    return mk_user_groups(session, user)


if __name__ == '__main__':
    try:
        serve()
    except KeyboardInterrupt:
        pass
    finally:
        sys.exit(0)



    """
def mk_btn_bar(active_btn: str = None, **kw):
    btn_users_cls = btn_roles_cls = btn_perm_cls = 'outline contrast'
    if active_btn == 'users':
        btn_users_cls = 'outline'
    if active_btn == 'roles':
        btn_roles_cls = 'outline'
    if active_btn == 'perm':
        btn_perm_cls = 'outline'

    btn_bar = Div(
        Button(
            'Manage Users',
            PicoBusy(),
            id='btn-users',
            hx_get='/users',
            hx_target='#content-area',
            cls=btn_users_cls,
        ),
        Nbsp(),
        Nbsp(),
        Button('Manage Roles', id='btn-roles', cls=btn_roles_cls),
        Nbsp(),
        Nbsp(),
        Button('Manage Permissions', id='btn-perm', cls=btn_perm_cls),
        id='btn-bar',
        **kw,
    )
    return btn_bar


    """