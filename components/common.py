from fasthtml.common import *
from monsterui.all import *


# Main Layout
def MainLayout(*c, nav_btns=True, active_btn=None, **kwargs):
    return (Title('RSMate'), Container(mk_nav_bar(nav_btns, active_btn), DivCentered(*c, id='app-area', cls='mb-6')))

# Form Components
def FormSectionDiv(*c, cls='space-y-2', **kwargs): return Div(*c, cls=cls, **kwargs)
def HelpText(c): return P(c,cls=TextPresets.muted_sm)

# Link Button 
def LinkButton(*c, icon: str, href: str='#', cls=(), **kw):
    return A(Span(UkIcon(icon), cls='mr-2 size-4'), *c,
                cls=('uk-btn') + cls, href=href, **kw)

# Brand
def mk_brand(): return DivLAligned(H1('RSMate', cls=TextT.primary))

# Nav Bar
def mk_nav_bar(nav_btns=True, active_btn=None):
    # active_btn = session.get('active_btn')
    if nav_btns:
        btn_users_cls = btn_roles_cls = ButtonT.default
        if not active_btn or active_btn == 'users': btn_users_cls = ButtonT.primary
        if active_btn == 'roles': btn_roles_cls = ButtonT.primary
        btns = (
            LinkButton('Users', icon='users', href='/users', cls=btn_users_cls),
            LinkButton('Roles', icon='user-cog', href='/roles', cls=btn_roles_cls),
            LinkButton('Switch Database', icon='arrow-left-right', href='/', cls=ButtonT.default),
        )
    else: btns = None

    return Div(NavBar(btns, brand=mk_brand()), id='nav-bar')


# ===== Lists and Selects =====

# Horizontal list of labels
def LabelList(labels: list):
    return Span(*[Label(l, cls=(TextT.sm, 'mx-1')) for l in labels])

def BadgeList(labels: list):
     return Span(*[Span(l, cls=(TextT.sm, 'uk-badge', 'm-1')) for l in labels])

# Options for select with same label and value
def SelectOptions(items: list, vals: list=None):
    if vals:
        return [Option(item, value=val) for item, val in zip(items, vals)]
    else:
        return [Option(item, value=item) for item in items]

# Removable list 
def RemovableList(items: list, id: str, hx_post: str, hx_target: str):
        return Ul(*[Li(
            DivHStacked(
                UkIconLink('trash-2', button=True, cls=ButtonT.destructive, 
                           id=f'btn-remove-{id}-{item}', name=item,
                            hx_post=hx_post, hx_target=hx_target, hx_swap='outerHTML'
                            ), 
                Strong(item)
            )) for item in items], cls=ListT.bullet, id=id),

# Set of controls to add, remove list items
def ListAddRemove(*options, items, placeholder, id, ls_id, add_hx_post, remove_hx_post):
    return Grid(
        DivFullySpaced(   
            Select(*options, placeholder=placeholder,
                    id=id, name=id, searchable=True, cls='w-full'),
            Button('Add', id=f'btn-add-{id}', 
                    hx_post=add_hx_post, hx_target=f'#{ls_id}', hx_swap='outerHTML'
            ), cls='space-x-4'
        ),
        RemovableList(items, id=ls_id, hx_post=remove_hx_post, hx_target=f'#{ls_id}'),
        id=f'grid{id}'
    )