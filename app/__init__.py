from fasthtml.common import *
from fasthtml.common import CheckboxX as fhCheckboxX
from monsterui.all import *
import sys

# listjs
listjs = Script(src='https://cdnjs.cloudflare.com/ajax/libs/list.js/2.3.1/list.min.js')
hdrs = (Theme.violet.headers(mode='light'), listjs)
app, rt = fast_app(hdrs=hdrs, debug=True, live=True)
setup_toasts(app)

# Import routes
from app.routes import home, users, user_groups, user_roles, roles, role_nested_roles, role_privileges, role_schema

def serve_app():
    try:
        serve()
    except KeyboardInterrupt:
        pass
    finally:
        sys.exit(0)

if __name__ == '__main__':
    serve_app()
