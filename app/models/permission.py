from app.database.connection import DatabaseConnection

class Permission:
    """
    Permission model for handling permission-related operations
    """
    def __init__(self, id=None, name=None, description=None):
        self.id = id
        self.name = name
        self.description = description
    
    @classmethod
    def create(cls, name, description=None):
        """
        Create a new permission
        
        Args:
            name (str): Permission name
            description (str, optional): Permission description
            
        Returns:
            Permission: Created permission object or None if failed
        """
        try:
            query = """
            INSERT INTO permissions (name, description)
            VALUES (%s, %s)
            RETURNING id, name, description;
            """
            params = (name, description)
            result = DatabaseConnection.execute_query(query, params)
            
            if result and len(result) > 0:
                perm_data = result[0]
                return cls(
                    id=perm_data[0],
                    name=perm_data[1],
                    description=perm_data[2]
                )
            return None
        except Exception as e:
            print(f"Error creating permission: {e}")
            return None
    
    @classmethod
    def get_by_id(cls, permission_id):
        """
        Get a permission by ID
        
        Args:
            permission_id (int): Permission ID
            
        Returns:
            Permission: Permission object or None if not found
        """
        query = """
        SELECT id, name, description
        FROM permissions
        WHERE id = %s;
        """
        result = DatabaseConnection.execute_query(query, (permission_id,))
        
        if result and len(result) > 0:
            perm_data = result[0]
            return cls(
                id=perm_data[0],
                name=perm_data[1],
                description=perm_data[2]
            )
        return None
    
    @classmethod
    def get_by_name(cls, name):
        """
        Get a permission by name
        
        Args:
            name (str): Permission name
            
        Returns:
            Permission: Permission object or None if not found
        """
        query = """
        SELECT id, name, description
        FROM permissions
        WHERE name = %s;
        """
        result = DatabaseConnection.execute_query(query, (name,))
        
        if result and len(result) > 0:
            perm_data = result[0]
            return cls(
                id=perm_data[0],
                name=perm_data[1],
                description=perm_data[2]
            )
        return None
    
    @classmethod
    def get_all(cls, limit=100, offset=0):
        """
        Get all permissions with pagination
        
        Args:
            limit (int): Maximum number of permissions to return
            offset (int): Number of permissions to skip
            
        Returns:
            list: List of Permission objects
        """
        query = """
        SELECT id, name, description
        FROM permissions
        ORDER BY id
        LIMIT %s OFFSET %s;
        """
        results = DatabaseConnection.execute_query(query, (limit, offset))
        
        permissions = []
        for perm_data in results:
            permissions.append(cls(
                id=perm_data[0],
                name=perm_data[1],
                description=perm_data[2]
            ))
        return permissions
    
    def update(self):
        """
        Update permission information
        
        Returns:
            bool: True if successful, False otherwise
        """
        query = """
        UPDATE permissions
        SET name = %s, description = %s
        WHERE id = %s;
        """
        params = (self.name, self.description, self.id)
        rows_affected = DatabaseConnection.execute_query(query, params, fetch=False)
        return rows_affected > 0
    
    def delete(self):
        """
        Delete a permission
        
        Returns:
            bool: True if successful, False otherwise
        """
        query = "DELETE FROM permissions WHERE id = %s;"
        rows_affected = DatabaseConnection.execute_query(query, (self.id,), fetch=False)
        return rows_affected > 0
    
    def get_roles(self):
        """
        Get all roles that have this permission
        
        Returns:
            list: List of role dictionaries
        """
        query = """
        SELECT r.id, r.name, r.description
        FROM roles r
        JOIN role_permissions rp ON r.id = rp.role_id
        WHERE rp.permission_id = %s;
        """
        results = DatabaseConnection.execute_query(query, (self.id,))
        
        roles = []
        for role_data in results:
            roles.append({
                'id': role_data[0],
                'name': role_data[1],
                'description': role_data[2]
            })
        return roles