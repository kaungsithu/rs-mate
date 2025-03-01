from fasthtml import app, html, redirect, request, url_for
from app.models import Permission

@app.route('/permissions')
def list_permissions():
    """List all permissions"""
    permissions = Permission.get_all()
    return html(
        title="Permissions",
        body="""
        <div class="container mt-4">
            <h1>Permissions</h1>
            <a href="/permissions/new" class="btn btn-primary mb-3">Add New Permission</a>
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
                    {% for permission in permissions %}
                    <tr>
                        <td>{{ permission.id }}</td>
                        <td>{{ permission.name }}</td>
                        <td>{{ permission.description or '' }}</td>
                        <td>
                            <a href="/permissions/{{ permission.id }}" class="btn btn-sm btn-info">View</a>
                            <a href="/permissions/{{ permission.id }}/edit" class="btn btn-sm btn-warning">Edit</a>
                            <form method="POST" action="/permissions/{{ permission.id }}/delete" style="display: inline;">
                                <button type="submit" class="btn btn-sm btn-danger" onclick="return confirm('Are you sure?')">Delete</button>
                            </form>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
        """,
        permissions=permissions
    )

@app.route('/permissions/new')
def new_permission():
    """Show form to create a new permission"""
    return html(
        title="New Permission",
        body="""
        <div class="container mt-4">
            <h1>New Permission</h1>
            <form method="POST" action="/permissions">
                <div class="mb-3">
                    <label for="name" class="form-label">Name</label>
                    <input type="text" class="form-control" id="name" name="name" required>
                </div>
                <div class="mb-3">
                    <label for="description" class="form-label">Description</label>
                    <textarea class="form-control" id="description" name="description" rows="3"></textarea>
                </div>
                <button type="submit" class="btn btn-primary">Create Permission</button>
                <a href="/permissions" class="btn btn-secondary">Cancel</a>
            </form>
        </div>
        """
    )

@app.route('/permissions', methods=['POST'])
def create_permission():
    """Create a new permission"""
    name = request.form.get('name')
    description = request.form.get('description')
    
    permission = Permission.create(name, description)
    
    if permission:
        return redirect('/permissions')
    else:
        return html(
            title="Error",
            body="""
            <div class="container mt-4">
                <div class="alert alert-danger">
                    Failed to create permission. Permission name may already be in use.
                </div>
                <a href="/permissions/new" class="btn btn-primary">Try Again</a>
            </div>
            """
        )

@app.route('/permissions/<int:permission_id>')
def view_permission(permission_id):
    """View a permission's details"""
    permission = Permission.get_by_id(permission_id)
    
    if not permission:
        return html(
            title="Permission Not Found",
            body="""
            <div class="container mt-4">
                <div class="alert alert-danger">Permission not found.</div>
                <a href="/permissions" class="btn btn-primary">Back to Permissions</a>
            </div>
            """
        )
    
    roles = permission.get_roles()
    
    return html(
        title=f"Permission: {permission.name}",
        body="""
        <div class="container mt-4">
            <h1>Permission Details</h1>
            <div class="card">
                <div class="card-body">
                    <h5 class="card-title">{{ permission.name }}</h5>
                    <p class="card-text"><strong>Description:</strong> {{ permission.description or 'N/A' }}</p>
                </div>
            </div>
            
            <h2 class="mt-4">Roles with this Permission</h2>
            {% if roles %}
            <ul class="list-group">
                {% for role in roles %}
                <li class="list-group-item">
                    <a href="/roles/{{ role.id }}">{{ role.name }}</a>
                    {% if role.description %}
                    <small class="text-muted">{{ role.description }}</small>
                    {% endif %}
                </li>
                {% endfor %}
            </ul>
            {% else %}
            <p>No roles have this permission.</p>
            {% endif %}
            
            <div class="mt-3">
                <a href="/permissions/{{ permission.id }}/edit" class="btn btn-warning">Edit</a>
                <a href="/permissions" class="btn btn-secondary">Back to Permissions</a>
            </div>
        </div>
        """,
        permission=permission,
        roles=roles
    )

@app.route('/permissions/<int:permission_id>/edit')
def edit_permission(permission_id):
    """Show form to edit a permission"""
    permission = Permission.get_by_id(permission_id)
    
    if not permission:
        return html(
            title="Permission Not Found",
            body="""
            <div class="container mt-4">
                <div class="alert alert-danger">Permission not found.</div>
                <a href="/permissions" class="btn btn-primary">Back to Permissions</a>
            </div>
            """
        )
    
    return html(
        title=f"Edit Permission: {permission.name}",
        body="""
        <div class="container mt-4">
            <h1>Edit Permission</h1>
            <form method="POST" action="/permissions/{{ permission.id }}/update">
                <div class="mb-3">
                    <label for="name" class="form-label">Name</label>
                    <input type="text" class="form-control" id="name" name="name" value="{{ permission.name }}" required>
                </div>
                <div class="mb-3">
                    <label for="description" class="form-label">Description</label>
                    <textarea class="form-control" id="description" name="description" rows="3">{{ permission.description or '' }}</textarea>
                </div>
                <button type="submit" class="btn btn-primary">Update Permission</button>
                <a href="/permissions/{{ permission.id }}" class="btn btn-secondary">Cancel</a>
            </form>
        </div>
        """,
        permission=permission
    )

@app.route('/permissions/<int:permission_id>/update', methods=['POST'])
def update_permission(permission_id):
    """Update a permission"""
    permission = Permission.get_by_id(permission_id)
    
    if not permission:
        return html(
            title="Permission Not Found",
            body="""
            <div class="container mt-4">
                <div class="alert alert-danger">Permission not found.</div>
                <a href="/permissions" class="btn btn-primary">Back to Permissions</a>
            </div>
            """
        )
    
    permission.name = request.form.get('name')
    permission.description = request.form.get('description')
    
    if permission.update():
        return redirect(f'/permissions/{permission_id}')
    else:
        return html(
            title="Error",
            body="""
            <div class="container mt-4">
                <div class="alert alert-danger">
                    Failed to update permission. Permission name may already be in use.
                </div>
                <a href="/permissions/{{ permission.id }}/edit" class="btn btn-primary">Try Again</a>
            </div>
            """,
            permission=permission
        )

@app.route('/permissions/<int:permission_id>/delete', methods=['POST'])
def delete_permission(permission_id):
    """Delete a permission"""
    permission = Permission.get_by_id(permission_id)
    
    if not permission:
        return html(
            title="Permission Not Found",
            body="""
            <div class="container mt-4">
                <div class="alert alert-danger">Permission not found.</div>
                <a href="/permissions" class="btn btn-primary">Back to Permissions</a>
            </div>
            """
        )
    
    if permission.delete():
        return redirect('/permissions')
    else:
        return html(
            title="Error",
            body="""
            <div class="container mt-4">
                <div class="alert alert-danger">Failed to delete permission.</div>
                <a href="/permissions" class="btn btn-primary">Back to Permissions</a>
            </div>
            """
        )