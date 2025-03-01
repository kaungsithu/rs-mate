from fasthtml.common import *
from app.models.user import PostgresUser
from app.models.role import PostgresGroup

# Get the app instance from the main module
from __main__ import app, rt

@rt('/users')
def get():
    """List all PostgreSQL users"""
    users = PostgresUser.get_all()
    
    return Title("PostgreSQL Users") + Div(
        H1("PostgreSQL Users"),
        A("Add New User", href="/users/new", cls="btn btn-primary mb-3"),
        Table(
            Thead(
                Tr(
                    Th("Username"),
                    Th("Superuser"),
                    Th("Create DB"),
                    Th("Create Role"),
                    Th("Login"),
                    Th("Connection Limit"),
                    Th("Groups"),
                    Th("Actions")
                )
            ),
            Tbody(
                [
                    Tr(
                        Td(user.username),
                        Td("Yes" if user.superuser else "No"),
                        Td("Yes" if user.createdb else "No"),
                        Td("Yes" if user.createrole else "No"),
                        Td("Yes" if user.login else "No"),
                        Td(str(user.connection_limit)),
                        Td(", ".join(user.groups) if user.groups else "None"),
                        Td(
                            A("View", href=f"/users/{user.username}", cls="btn btn-sm btn-info me-1"),
                            A("Edit", href=f"/users/{user.username}/edit", cls="btn btn-sm btn-warning me-1"),
                            Form(
                                Button("Delete", type="submit", cls="btn btn-sm btn-danger", 
                                       onclick="return confirm('Are you sure?')"),
                                method="POST", action=f"/users/{user.username}/delete", style="display: inline;"
                            )
                        )
                    ) for user in users
                ]
            ),
            cls="table table-striped"
        ),
        cls="container mt-4"
    )

@rt('/users/new')
def new_user():
    """Show form to create a new PostgreSQL user"""
    groups = PostgresGroup.get_all()
    
    return Title("New PostgreSQL User") + Div(
        H1("New PostgreSQL User"),
        Form(
            Div(
                Label("Username", for_="username", cls="form-label"),
                Input(type="text", id="username", name="username", required=True, cls="form-control"),
                cls="mb-3"
            ),
            Div(
                Label("Password", for_="password", cls="form-label"),
                Input(type="password", id="password", name="password", required=True, cls="form-control"),
                cls="mb-3"
            ),
            Div(
                Div(
                    Input(type="checkbox", id="superuser", name="superuser", cls="form-check-input"),
                    Label("Superuser", for_="superuser", cls="form-check-label"),
                    cls="form-check"
                ),
                cls="mb-3"
            ),
            Div(
                Div(
                    Input(type="checkbox", id="createdb", name="createdb", cls="form-check-input"),
                    Label("Can Create Databases", for_="createdb", cls="form-check-label"),
                    cls="form-check"
                ),
                cls="mb-3"
            ),
            Div(
                Div(
                    Input(type="checkbox", id="createrole", name="createrole", cls="form-check-input"),
                    Label("Can Create Roles", for_="createrole", cls="form-check-label"),
                    cls="form-check"
                ),
                cls="mb-3"
            ),
            Div(
                Div(
                    Input(type="checkbox", id="login", name="login", cls="form-check-input", checked=True),
                    Label("Can Login", for_="login", cls="form-check-label"),
                    cls="form-check"
                ),
                cls="mb-3"
            ),
            Div(
                Label("Connection Limit (-1 for unlimited)", for_="connection_limit", cls="form-label"),
                Input(type="number", id="connection_limit", name="connection_limit", value="-1", cls="form-control"),
                cls="mb-3"
            ),
            Div(
                Label("Valid Until (leave empty for no expiration)", for_="valid_until", cls="form-label"),
                Input(type="datetime-local", id="valid_until", name="valid_until", cls="form-control"),
                cls="mb-3"
            ),
            Div(
                Label("Groups", for_="groups", cls="form-label"),
                Select(
                    [Option(group.name, value=group.name) for group in groups],
                    id="groups", name="groups", multiple=True, cls="form-select"
                ),
                P("Hold Ctrl/Cmd to select multiple groups", cls="form-text"),
                cls="mb-3"
            ),
            Button("Create User", type="submit", cls="btn btn-primary me-2"),
            A("Cancel", href="/users", cls="btn btn-secondary"),
            method="POST", action="/users"
        ),
        cls="container mt-4"
    )

@app.post('/users')
def create_user():
    """Create a new PostgreSQL user"""
    username = request.form.get('username')
    password = request.form.get('password')
    superuser = 'superuser' in request.form
    createdb = 'createdb' in request.form
    createrole = 'createrole' in request.form
    login = 'login' in request.form
    connection_limit = int(request.form.get('connection_limit', -1))
    valid_until = request.form.get('valid_until')
    groups = request.form.getlist('groups')
    
    user = PostgresUser.create(
        username=username,
        password=password,
        superuser=superuser,
        createdb=createdb,
        createrole=createrole,
        login=login,
        connection_limit=connection_limit,
        valid_until=valid_until
    )
    
    if user:
        # Add user to selected groups
        for group_name in groups:
            user.add_to_group(group_name)
        
        return redirect('/users')
    else:
        return Title("Error") + Div(
            Div(
                "Failed to create PostgreSQL user. Username may already be in use.",
                cls="alert alert-danger"
            ),
            A("Try Again", href="/users/new", cls="btn btn-primary"),
            cls="container mt-4"
        )

@rt('/users/<username>')
def view_user(username):
    """View a PostgreSQL user's details"""
    user = PostgresUser.get_by_username(username)
    
    if not user:
        return Title("User Not Found") + Div(
            Div("PostgreSQL user not found.", cls="alert alert-danger"),
            A("Back to Users", href="/users", cls="btn btn-primary"),
            cls="container mt-4"
        )
    
    all_groups = PostgresGroup.get_all()
    available_groups = [g for g in all_groups if g.name not in user.groups]
    
    return Title(f"PostgreSQL User: {user.username}") + Div(
        H1("PostgreSQL User Details"),
        Div(
            Div(
                H5(user.username, cls="card-title"),
                P(B("Superuser: "), "Yes" if user.superuser else "No", cls="card-text"),
                P(B("Can Create Databases: "), "Yes" if user.createdb else "No", cls="card-text"),
                P(B("Can Create Roles: "), "Yes" if user.createrole else "No", cls="card-text"),
                P(B("Can Login: "), "Yes" if user.login else "No", cls="card-text"),
                P(B("Connection Limit: "), str(user.connection_limit), cls="card-text"),
                P(B("Valid Until: "), str(user.valid_until) if user.valid_until else "No expiration", cls="card-text"),
                cls="card-body"
            ),
            cls="card"
        ),
        
        H2("Groups", cls="mt-4"),
        Div(
            Ul(
                [
                    Li(
                        Div(
                            Span(group_name),
                            Form(
                                Button("Remove", type="submit", cls="btn btn-sm btn-danger"),
                                method="POST", action=f"/users/{user.username}/groups/{group_name}/remove", 
                                style="display: inline; float: right;"
                            ),
                            cls="d-flex justify-content-between align-items-center"
                        ),
                        cls="list-group-item"
                    ) for group_name in user.groups
                ],
                cls="list-group"
            ) if user.groups else P("No groups assigned."),
            cls="mb-4"
        ),
        
        H3("Add to Group", cls="mt-3"),
        Form(
            Div(
                Select(
                    [Option(group.name, value=group.name) for group in available_groups],
                    name="group_name", cls="form-select"
                ),
                Button("Add", type="submit", cls="btn btn-primary ms-2"),
                cls="input-group"
            ),
            method="POST", action=f"/users/{user.username}/groups/add", 
            cls="mb-4"
        ) if available_groups else P("No more groups available to add."),
        
        Div(
            A("Edit", href=f"/users/{user.username}/edit", cls="btn btn-warning me-2"),
            A("Back to Users", href="/users", cls="btn btn-secondary"),
            cls="mt-3"
        ),
        cls="container mt-4"
    )

@rt('/users/<username>/edit')
def edit_user(username):
    """Show form to edit a PostgreSQL user"""
    user = PostgresUser.get_by_username(username)
    
    if not user:
        return Title("User Not Found") + Div(
            Div("PostgreSQL user not found.", cls="alert alert-danger"),
            A("Back to Users", href="/users", cls="btn btn-primary"),
            cls="container mt-4"
        )
    
    return Title(f"Edit PostgreSQL User: {user.username}") + Div(
        H1("Edit PostgreSQL User"),
        Form(
            Div(
                Label("Username", for_="username", cls="form-label"),
                Input(type="text", id="username", name="username", value=user.username, disabled=True, cls="form-control"),
                P("Username cannot be changed. Create a new user if needed.", cls="form-text"),
                cls="mb-3"
            ),
            Div(
                Label("New Password (leave empty to keep current)", for_="password", cls="form-label"),
                Input(type="password", id="password", name="password", cls="form-control"),
                cls="mb-3"
            ),
            Div(
                Div(
                    Input(type="checkbox", id="superuser", name="superuser", checked=user.superuser, cls="form-check-input"),
                    Label("Superuser", for_="superuser", cls="form-check-label"),
                    cls="form-check"
                ),
                cls="mb-3"
            ),
            Div(
                Div(
                    Input(type="checkbox", id="createdb", name="createdb", checked=user.createdb, cls="form-check-input"),
                    Label("Can Create Databases", for_="createdb", cls="form-check-label"),
                    cls="form-check"
                ),
                cls="mb-3"
            ),
            Div(
                Div(
                    Input(type="checkbox", id="createrole", name="createrole", checked=user.createrole, cls="form-check-input"),
                    Label("Can Create Roles", for_="createrole", cls="form-check-label"),
                    cls="form-check"
                ),
                cls="mb-3"
            ),
            Div(
                Div(
                    Input(type="checkbox", id="login", name="login", checked=user.login, cls="form-check-input"),
                    Label("Can Login", for_="login", cls="form-check-label"),
                    cls="form-check"
                ),
                cls="mb-3"
            ),
            Div(
                Label("Connection Limit (-1 for unlimited)", for_="connection_limit", cls="form-label"),
                Input(type="number", id="connection_limit", name="connection_limit", value=str(user.connection_limit), cls="form-control"),
                cls="mb-3"
            ),
            Div(
                Label("Valid Until (leave empty for no expiration)", for_="valid_until", cls="form-label"),
                Input(type="datetime-local", id="valid_until", name="valid_until", value=user.valid_until, cls="form-control"),
                cls="mb-3"
            ),
            Button("Update User", type="submit", cls="btn btn-primary me-2"),
            A("Cancel", href=f"/users/{user.username}", cls="btn btn-secondary"),
            method="POST", action=f"/users/{user.username}/update"
        ),
        cls="container mt-4"
    )

@app.post('/users/<username>/update')
def update_user(username):
    """Update a PostgreSQL user"""
    user = PostgresUser.get_by_username(username)
    
    if not user:
        return Title("User Not Found") + Div(
            Div("PostgreSQL user not found.", cls="alert alert-danger"),
            A("Back to Users", href="/users", cls="btn btn-primary"),
            cls="container mt-4"
        )
    
    password = request.form.get('password')
    superuser = 'superuser' in request.form
    createdb = 'createdb' in request.form
    createrole = 'createrole' in request.form
    login = 'login' in request.form
    connection_limit = int(request.form.get('connection_limit', -1))
    valid_until = request.form.get('valid_until')
    
    if user.update(
        password=password if password else None,
        superuser=superuser,
        createdb=createdb,
        createrole=createrole,
        login=login,
        connection_limit=connection_limit,
        valid_until=valid_until
    ):
        return redirect(f'/users/{username}')
    else:
        return Title("Error") + Div(
            Div("Failed to update PostgreSQL user.", cls="alert alert-danger"),
            A("Try Again", href=f"/users/{username}/edit", cls="btn btn-primary"),
            cls="container mt-4"
        )

@app.post('/users/<username>/delete')
def delete_user(username):
    """Delete a PostgreSQL user"""
    user = PostgresUser.get_by_username(username)
    
    if not user:
        return Title("User Not Found") + Div(
            Div("PostgreSQL user not found.", cls="alert alert-danger"),
            A("Back to Users", href="/users", cls="btn btn-primary"),
            cls="container mt-4"
        )
    
    if user.delete():
        return redirect('/users')
    else:
        return Title("Error") + Div(
            Div(
                "Failed to delete PostgreSQL user. The user may own database objects or have privileges granted.",
                cls="alert alert-danger"
            ),
            A("Back to Users", href="/users", cls="btn btn-primary"),
            cls="container mt-4"
        )

@app.post('/users/<username>/groups/add')
def add_user_to_group(username):
    """Add a PostgreSQL user to a group"""
    user = PostgresUser.get_by_username(username)
    
    if not user:
        return Title("User Not Found") + Div(
            Div("PostgreSQL user not found.", cls="alert alert-danger"),
            A("Back to Users", href="/users", cls="btn btn-primary"),
            cls="container mt-4"
        )
    
    group_name = request.form.get('group_name')
    
    if not group_name:
        return redirect(f'/users/{username}')
    
    if user.add_to_group(group_name):
        return redirect(f'/users/{username}')
    else:
        return Title("Error") + Div(
            Div("Failed to add user to group.", cls="alert alert-danger"),
            A("Back to User", href=f"/users/{username}", cls="btn btn-primary"),
            cls="container mt-4"
        )

@app.post('/users/<username>/groups/<group_name>/remove')
def remove_user_from_group(username, group_name):
    """Remove a PostgreSQL user from a group"""
    user = PostgresUser.get_by_username(username)
    
    if not user:
        return Title("User Not Found") + Div(
            Div("PostgreSQL user not found.", cls="alert alert-danger"),
            A("Back to Users", href="/users", cls="btn btn-primary"),
            cls="container mt-4"
        )
    
    if user.remove_from_group(group_name):
        return redirect(f'/users/{username}')
    else:
        return Title("Error") + Div(
            Div("Failed to remove user from group.", cls="alert alert-danger"),
            A("Back to User", href=f"/users/{username}", cls="btn btn-primary"),
            cls="container mt-4"
        )