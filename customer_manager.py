<<<<<<< HEAD
"""
Customer management module
"""

class CustomerManager:
    """Manage customers"""
    
    def __init__(self, db):
        self.db = db
    
    def add_customer(self, name, phone=None, email=None, address=None, city=None):
        """Add customer"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO customers (name, phone, email, address, city)
            VALUES (?, ?, ?, ?, ?)
        ''', (name, phone, email, address, city))
        conn.commit()
        conn.close()
        return cursor.lastrowid
    
    def get_customer(self, customer_id):
        """Get customer"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM customers WHERE id = ?", (customer_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
    
    def get_all_customers(self):
        """Get all customers"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM customers ORDER BY name")
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def search_customers(self, query):
        """Search customers"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM customers WHERE name LIKE ? OR phone LIKE ? ORDER BY name",
            (f'%{query}%', f'%{query}%')
        )
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def update_customer(self, customer_id, **kwargs):
        """Update customer"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        updates = ", ".join([f"{k} = ?" for k in kwargs.keys()])
        values = list(kwargs.values()) + [customer_id]
        
        cursor.execute(f"UPDATE customers SET {updates}, updated_at = CURRENT_TIMESTAMP WHERE id = ?", values)
        conn.commit()
        conn.close()
        return True
    
    def delete_customer(self, customer_id):
        """Delete customer"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM customers WHERE id = ?", (customer_id,))
        conn.commit()
        conn.close()
        return True
=======
"""
Customer management module
"""

class CustomerManager:
    """Manage customers"""
    
    def __init__(self, db):
        self.db = db
    
    def add_customer(self, name, phone=None, email=None, address=None, city=None):
        """Add customer"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO customers (name, phone, email, address, city)
            VALUES (?, ?, ?, ?, ?)
        ''', (name, phone, email, address, city))
        conn.commit()
        conn.close()
        return cursor.lastrowid
    
    def get_customer(self, customer_id):
        """Get customer"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM customers WHERE id = ?", (customer_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
    
    def get_all_customers(self):
        """Get all customers"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM customers ORDER BY name")
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def search_customers(self, query):
        """Search customers"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM customers WHERE name LIKE ? OR phone LIKE ? ORDER BY name",
            (f'%{query}%', f'%{query}%')
        )
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def update_customer(self, customer_id, **kwargs):
        """Update customer"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        updates = ", ".join([f"{k} = ?" for k in kwargs.keys()])
        values = list(kwargs.values()) + [customer_id]
        
        cursor.execute(f"UPDATE customers SET {updates}, updated_at = CURRENT_TIMESTAMP WHERE id = ?", values)
        conn.commit()
        conn.close()
        return True
    
    def delete_customer(self, customer_id):
        """Delete customer"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM customers WHERE id = ?", (customer_id,))
        conn.commit()
        conn.close()
        return True
>>>>>>> 5058b63e17bc5c42e66a4f03a260eae69ba8e457
