"""
User management and authentication
"""
from pos_app.utils.auth import hash_password, verify_password

class UserManager:
    """Manage users and authentication"""
    
    def __init__(self, db):
        self.db = db
    
    def create_user(self, username, password, role, full_name=None, email=None):
        """Create a new user"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        if cursor.fetchone():
            return None, "Username already exists"
        
        password_hash = hash_password(password)
        try:
            cursor.execute('''
                INSERT INTO users (username, password_hash, role, full_name, email)
                VALUES (?, ?, ?, ?, ?)
            ''', (username, password_hash, role, full_name, email))
            conn.commit()
            return cursor.lastrowid, "User created successfully"
        except Exception as e:
            return None, str(e)
        finally:
            conn.close()
    
    def authenticate(self, username, password):
        """Authenticate user"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        conn.close()
        
        if row and verify_password(password, row['password_hash']):
            return dict(row), "Authentication successful"
        return None, "Invalid credentials"
    
    def get_user(self, user_id):
        """Get user by ID"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
    
    def get_all_users(self):
        """Get all users"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users")
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def update_user(self, user_id, **kwargs):
        """Update user"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        updates = ", ".join([f"{k} = ?" for k in kwargs.keys()])
        values = list(kwargs.values()) + [user_id]
        
        cursor.execute(f"UPDATE users SET {updates} WHERE id = ?", values)
        conn.commit()
        conn.close()
        return True
    
    def deactivate_user(self, user_id):
        """Deactivate user"""
        return self.update_user(user_id, is_active=0)
    
    def activate_user(self, user_id):
        """Activate user"""
        return self.update_user(user_id, is_active=1)
