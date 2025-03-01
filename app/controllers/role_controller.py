from fasthtml import app, html, redirect, request, url_for
from app.models import Role, Permission

@app.route('/roles')
def list_roles():
    """List all roles"""
    roles = Role.get_all()
    return html(
        title="Roles",
        body="""
        <div class="container mt-4">
            <h1>Roles</h1>
            <a href="/roles/new" class="btn btn-primary mb-3">Add New Role</a>
            <table class="table table-striped">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Name</th>
                        <th>Description</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {% for role in roles %}
                    <tr>
                        <td>{{ role.id }}</td>
                        <td>{{ role.name }}</td>
                        <td>{{ role.description or '' }}</td>
                        <td>
                            <a href="/roles/{{ role.id }}" class="btn btn-sm btn-info">View</a>
                            <a href="/roles/{{ role.id }}/edit" class="btn btn-sm btn-warning">Edit</a>
                            <form method="POST" action="/roles/{{ role.id }}/delete" style="display: inline;">
                                <button type="submit" class="btn btn-sm btn-danger" onclick="return confirm('Are you sure?')">Delete</button>
                            </form>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
        """,
        roles=roles
    )

@app.route('/roles/new')
def new_role():
    """Show form to create a new role"""
    return html(
        title="New Role",
        body="""
        <div class="container mt-4">
            <h1>New Role</h1>
            <form method="POST" action="/roles">
                <div class="mb-3">
                    <label for="name" class="form-label">Name</label>
                    <input type="text" class="form-control" id="name" name="name" required>
                </div>
                <div class="mb-3">
                    <label for="description" class="form-label">Description</label>
                    <textarea class="form-control" id="description" name="description" rows="3"></textarea>
                </div>
                <button type="submit" class="btn btn-primary">Create Role</button>
                <a href="/roles" class="btn btn-secondary">Cancel</a>
            </form>
        </div>
        """
    )

@app.route('/roles', methods=['POST'])
def create_role():
    """Create a new role"""
    name = request.form.get('name')
    description = request.form.get('description')
    
    role = Role.create(name, description)
    
    if role:
        return redirect('/roles')
    else:
        return html(
            title="Error",
            body="""
            <div class="container mt-4">
                <div class="alert alert-danger">
                    Failed to create role. Role name may already be in use.
                </div>
                <a href="/roles/new" class="btn btn-primary">Try Again</a>
            </div>
            """
        )

@app.route('/roles/<int:role_id>')
def view_role(role_id):
    """View a role's details"""
    role = Role.get_by_id(role_id)
    
    if not role:
        return html(
            title="Role Not Found",
            body="""
            <div class="container mt-4">
                <div class="alert alert-danger">Role not found.</div>
                <a href="/roles" class="btn btn-primary">Back to Roles</a>
            </div>
            """
        )
    
    permissions = role.get_permissions()
    users = role.get_users()
    
    return html(
        title=f"Role: {role.name}",
        body="""
        <div class="container mt-4">
            <h1>Role Details</h1>
            <div class="card">
                <div class="card-body">
                    <h5 class="card-title">{{ role.name }}</h5>
                    <p class="card-text"><strong>Description:</strong> {{ role.description or 'N/A' }}</p>
                </div>
            </div>
            
            <h2 class="mt-4">Permissions</h2>
            {% if permissions %}
            <ul class="list-group">
                {% for permission in permissions %}
                <li class="list-group-item d-flex justify-content-between align-items-center">
                    {{ permission.name }}
                    <form method="POST" action="/roles/{{ role.id }}/permissions/{{ permission.id }}/remove" style="display: inline;">
                        <button type="submit" class="btn btn-sm btn-danger">Remove</button>
                    </form>
                </li>
                {% endfor %}
            </ul>
            {% else %}
            <p>No permissions assigned.</p>
            {% endif %}
            
            <h3 class="mt-3">Assign Permission</h3>
            <form method="POST" action="/roles/{{ role.id }}/permissions/assign" class="mb-4">
                <div class="input-group">
                    <select name="permission_id" class="form-select">
                        <!-- This will be populated with available permissions -->
                        <option value="">Select a permission...</option>
                    </select>
                    <button type="submit" class="btn btn-primary">Assign</button>
                </div>
            </form>
            
            <h2 class="mt-4">Users with this Role</h2>
            {% if users %}
            <ul class="list-group">
                {% for user in users %}
                <li class="list-group-item">
                    <a href="/users/{{ user.id }}">{{ user.username }}</a> ({{ user.email }})
                </li>
                {% endfor %}
            </ul>
            {% else %}
            <p>No users have this role.</p>
            {% endif %}
            
            <div class="mt-3">
                <a href="/roles/{{ role.id }}/edit" class="btn btn-warning">Edit</a>
                <a href="/roles" class="btn btn-secondary">Back to Roles</a>
            </div>
        </div>
        """,
        role=role,
        permissions=permissions,
        users=users
    )

@app.route('/roles/<int:role_id>/edit')
def edit_role(role_id):
    """Show form to edit a role"""
    role = Role.get_by_id(role_id)
    
    if not role:
        return html(
            title="Role Not Found",
            body="""
            <div class="container mt-4">
                <div class="alert alert-danger">Role not found.</div>
                <a href="/roles" class="btn btn-primary">Back to Roles</a>
            </div>
            """
        )
    
    return html(
        title=f"Edit Role: {role.name}",
        body="""
        <div class="container mt-4">
            <h1>Edit Role</h1>
            <form method="POST" action="/roles/{{ role.id }}/update">
                <div class="mb-3">
                    <label for="name" class="form-label">Name</label>
                    <input type="text" class="form-control" id="name" name="name" value="{{ role.name }}" required>
                </div>
                <div class="mb-3">
                    <label for="description" class="form-label">Description</label>
                    <textarea class="form-control" id="description" name="description" rows="3">{{ role.description or '' }}</textarea>
                </div>
                <button type="submit" class="btn btn-primary">Update Role</button>
                <a href="/roles/{{ role.id }}" class="btn btn-secondary">Cancel</a>
            </form>
        </div>
        """,
        role=role
    )

@app.route('/roles/<int:role_id>/update', methods=['POST'])
def update_role(role_id):
    """Update a role"""
    role = Role.get_by_id(role_id)
    
    if not role:
        return html(
            title="Role Not Found",
            body="""
            <div class="container mt-4">
                <div class="alert alert-danger">Role not found.</div>
                <a href="/roles" class="btn btn-primary">Back to Roles</a>
            </div>
            """
        )
    
    role.name = request.form.get('name')
    role.description = request.form.get('description')
    
    if role.update():
        return redirect(f'/roles/{role_id}')
    else:
        return html(
            title="Error",
            body="""
            <div class="container mt-4">
                <div class="alert alert-danger">
                    Failed to update role. Role name may already be in use.
                </div>
                <a href="/roles/{{ role.id }}/edit" class="btn btn-primary">Try Again</a>
            </div>
            """,
            role=role
        )

@app.route('/roles/<int:role_id>/delete', methods=['POST'])
def delete_role(role_id):
    """Delete a role"""
    role = Role.get_by_id(role_id)
    
    if not role:
        return html(
            title="Role Not Found",
            body="""
            <div class="container mt-4">
                <div class="alert alert-danger">Role not found.</div>
                <a href="/roles" class="btn btn-primary">Back to Roles</a>
            </div>
            """
        )
    
    if role.delete():
        return redirect('/roles')
    else:
        return html(
            title="Error",
            body="""
            <div class="container mt-4">
                <div class="alert alert-danger">Failed to delete role.</div>
                <a href="/roles" class="btn btn-primary">Back to Roles</a>
            </div>
            """
        )

@app.route('/roles/<int:role_id>/permissions/assign', methods=['POST'])
def assign_permission_to_role(role_id):
    """Assign a permission to a role"""
    role = Role.get_by_id(role_id)
    
    if not role:
        return html(
            title="Role Not Found",
            body="""
            <div class="container mt-4">
                <div class="alert alert-danger">Role not found.</div>
                <a href="/roles" class="btn btn-primary">Back to Roles</a>
            </div>
            """
        )
    
    permission_id = request.form.get('permission_id')
    
    if not permission_id:
        return redirect(f'/roles/{role_id}')
    
    if role.assign_permission(permission_id):
        return redirect(f'/roles/{role_id}')
    else:
        return html(
            title="Error",
            body="""
            <div class="container mt-4">
                <div class="alert alert-danger">Failed to assign permission.</div>
                <a href="/roles/{{ role.id }}" class="btn btn-primary">Back to Role</a>
            </div>
            """,
            role=role
        )

@app.route('/roles/<int:role_id>/permissions/<int:permission_id>/remove', methods=['POST'])
def remove_permission_from_role(role_id, permission_id):
    """Remove a permission from a role"""
    role = Role.get_by_id(role_id)
    
    if not role:
        return html(
            title="Role Not Found",
            body="""
            <div class="container mt-4">
                <div class="alert alert-danger">Role not found.</div>
                <a href="/roles" class="btn btn-primary">Back to Roles</a>
            </div>
            """
        )
    
    if role.remove_permission(permission_id):
        return redirect(f'/roles/{role_id}')
    else:
        return html(
            title="Error",
            body="""
            <div class="container mt-4">
                <div class="alert alert-danger">Failed to remove permission.</div>
                <a href="/roles/{{ role.id }}" class="btn btn-primary">Back to Role</a>
            </div>
            """,
            role=role
        )