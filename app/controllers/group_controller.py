from fasthtml.common import *
from app.models.role import PostgresGroup

app = FastHTML()

@app.get('/groups')
def list_groups():
    """List all PostgreSQL groups"""
    groups = PostgresGroup.get_all()
    
    return Title("PostgreSQL Groups") + Div(
        H1("PostgreSQL Groups"),
        A("Add New Group", href="/groups/new", cls="btn btn-primary mb-3"),
        Table(
            Thead(
                Tr(
                    Th("Name"),
                    Th("Group ID"),
                    Th("Members"),
                    Th("Actions")
                )
            ),
            Tbody(
                [
                    Tr(
                        Td(group.name),
                        Td(str(group.gid)),
                        Td(", ".join(group.members) if group.members else "None"),
                        Td(
                            A("View", href=f"/groups/{group.name}", cls="btn btn-sm btn-info me-1"),
                            A("Edit", href=f"/groups/{group.name}/edit", cls="btn btn-sm btn-warning me-1"),
                            Form(
                                Button("Delete", type="submit", cls="btn btn-sm btn-danger", 
                                       onclick="return confirm('Are you sure?')"),
                                method="POST", action=f"/groups/{group.name}/delete", style="display: inline;"
                            )
                        )
                    ) for group in groups
                ]
            ),
            cls="table table-striped"
        ),
        cls="container mt-4"
    )

@app.get('/groups/new')
def new_group():
    """Show form to create a new PostgreSQL group"""
    from app.models.user import PostgresUser
    users = PostgresUser.get_all()
    
    return Title("New PostgreSQL Group") + Div(
        H1("New PostgreSQL Group"),
        Form(
            Div(
                Label("Group Name", for_="name", cls="form-label"),
                Input(type="text", id="name", name="name", required=True, cls="form-control"),
                cls="mb-3"
            ),
            Div(
                Label("Members", for_="members", cls="form-label"),
                Select(
                    [Option(user.username, value=user.username) for user in users],
                    id="members", name="members", multiple=True, cls="form-select"
                ),
                P("Hold Ctrl/Cmd to select multiple users", cls="form-text"),
                cls="mb-3"
            ),
            Button("Create Group", type="submit", cls="btn btn-primary me-2"),
            A("Cancel", href="/groups", cls="btn btn-secondary"),
            method="POST", action="/groups"
        ),
        cls="container mt-4"
    )

@app.post('/groups')
def create_group():
    """Create a new PostgreSQL group"""
    name = request.form.get('name')
    members = request.form.getlist('members')
    
    group = PostgresGroup.create(name, members)
    
    if group:
        return redirect('/groups')
    else:
        return Title("Error") + Div(
            Div(
                "Failed to create PostgreSQL group. Group name may already be in use.",
                cls="alert alert-danger"
            ),
            A("Try Again", href="/groups/new", cls="btn btn-primary"),
            cls="container mt-4"
        )

@app.get('/groups/<name>')
def view_group(name):
    """View a PostgreSQL group's details"""
    group = PostgresGroup.get_by_name(name)
    
    if not group:
        return Title("Group Not Found") + Div(
            Div("PostgreSQL group not found.", cls="alert alert-danger"),
            A("Back to Groups", href="/groups", cls="btn btn-primary"),
            cls="container mt-4"
        )
    
    from app.models.user import PostgresUser
    all_users = PostgresUser.get_all()
    available_users = [u for u in all_users if u.username not in group.members]
    
    return Title(f"PostgreSQL Group: {group.name}") + Div(
        H1("PostgreSQL Group Details"),
        Div(
            Div(
                H5(group.name, cls="card-title"),
                P(B("Group ID: "), str(group.gid), cls="card-text"),
                cls="card-body"
            ),
            cls="card"
        ),
        
        H2("Members", cls="mt-4"),
        Div(
            Ul(
                [
                    Li(
                        Div(
                            Span(username),
                            Form(
                                Button("Remove", type="submit", cls="btn btn-sm btn-danger"),
                                method="POST", action=f"/groups/{group.name}/members/{username}/remove", 
                                style="display: inline; float: right;"
                            ),
                            cls="d-flex justify-content-between align-items-center"
                        ),
                        cls="list-group-item"
                    ) for username in group.members
                ],
                cls="list-group"
            ) if group.members else P("No members in this group."),
            cls="mb-4"
        ),
        
        H3("Add Member", cls="mt-3"),
        Form(
            Div(
                Select(
                    [Option(user.username, value=user.username) for user in available_users],
                    name="username", cls="form-select"
                ),
                Button("Add", type="submit", cls="btn btn-primary ms-2"),
                cls="input-group"
            ),
            method="POST", action=f"/groups/{group.name}/members/add", 
            cls="mb-4"
        ) if available_users else P("No more users available to add."),
        
        Div(
            A("Edit", href=f"/groups/{group.name}/edit", cls="btn btn-warning me-2"),
            A("Back to Groups", href="/groups", cls="btn btn-secondary"),
            cls="mt-3"
        ),
        cls="container mt-4"
    )

@app.get('/groups/<name>/edit')
def edit_group(name):
    """Show form to edit a PostgreSQL group"""
    group = PostgresGroup.get_by_name(name)
    
    if not group:
        return Title("Group Not Found") + Div(
            Div("PostgreSQL group not found.", cls="alert alert-danger"),
            A("Back to Groups", href="/groups", cls="btn btn-primary"),
            cls="container mt-4"
        )
    
    return Title(f"Edit PostgreSQL Group: {group.name}") + Div(
        H1("Edit PostgreSQL Group"),
        Form(
            Div(
                Label("New Group Name", for_="new_name", cls="form-label"),
                Input(type="text", id="new_name", name="new_name", value=group.name, cls="form-control"),
                cls="mb-3"
            ),
            Button("Rename Group", type="submit", cls="btn btn-primary me-2"),
            A("Cancel", href=f"/groups/{group.name}", cls="btn btn-secondary"),
            method="POST", action=f"/groups/{group.name}/update"
        ),
        cls="container mt-4"
    )

@app.post('/groups/<name>/update')
def update_group(name):
    """Update a PostgreSQL group"""
    group = PostgresGroup.get_by_name(name)
    
    if not group:
        return Title("Group Not Found") + Div(
            Div("PostgreSQL group not found.", cls="alert alert-danger"),
            A("Back to Groups", href="/groups", cls="btn btn-primary"),
            cls="container mt-4"
        )
    
    new_name = request.form.get('new_name')
    
    if new_name and new_name != name:
        if group.rename(new_name):
            return redirect(f'/groups/{new_name}')
        else:
            return Title("Error") + Div(
                Div("Failed to rename PostgreSQL group.", cls="alert alert-danger"),
                A("Try Again", href=f"/groups/{name}/edit", cls="btn btn-primary"),
                cls="container mt-4"
            )
    else:
        return redirect(f'/groups/{name}')

@app.post('/groups/<name>/delete')
def delete_group(name):
    """Delete a PostgreSQL group"""
    group = PostgresGroup.get_by_name(name)
    
    if not group:
        return Title("Group Not Found") + Div(
            Div("PostgreSQL group not found.", cls="alert alert-danger"),
            A("Back to Groups", href="/groups", cls="btn btn-primary"),
            cls="container mt-4"
        )
    
    if group.delete():
        return redirect('/groups')
    else:
        return Title("Error") + Div(
            Div(
                "Failed to delete PostgreSQL group.",
                cls="alert alert-danger"
            ),
            A("Back to Groups", href="/groups", cls="btn btn-primary"),
            cls="container mt-4"
        )

@app.post('/groups/<name>/members/add')
def add_member_to_group(name):
    """Add a member to a PostgreSQL group"""
    group = PostgresGroup.get_by_name(name)
    
    if not group:
        return Title("Group Not Found") + Div(
            Div("PostgreSQL group not found.", cls="alert alert-danger"),
            A("Back to Groups", href="/groups", cls="btn btn-primary"),
            cls="container mt-4"
        )
    
    username = request.form.get('username')
    
    if not username:
        return redirect(f'/groups/{name}')
    
    if group.add_user(username):
        return redirect(f'/groups/{name}')
    else:
        return Title("Error") + Div(
            Div("Failed to add user to group.", cls="alert alert-danger"),
            A("Back to Group", href=f"/groups/{name}", cls="btn btn-primary"),
            cls="container mt-4"
        )

@app.post('/groups/<name>/members/<username>/remove')
def remove_member_from_group(name, username):
    """Remove a member from a PostgreSQL group"""
    group = PostgresGroup.get_by_name(name)
    
    if not group:
        return Title("Group Not Found") + Div(
            Div("PostgreSQL group not found.", cls="alert alert-danger"),
            A("Back to Groups", href="/groups", cls="btn btn-primary"),
            cls="container mt-4"
        )
    
    if group.remove_user(username):
        return redirect(f'/groups/{name}')
    else:
        return Title("Error") + Div(
            Div("Failed to remove user from group.", cls="alert alert-danger"),
            A("Back to Group", href=f"/groups/{name}", cls="btn btn-primary"),
            cls="container mt-4"
        )