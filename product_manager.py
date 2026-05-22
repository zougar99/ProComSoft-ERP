<<<<<<< HEAD
"""
Product management module
"""

class ProductManager:
    """Manage products and inventory"""
    
    def __init__(self, db):
        self.db = db
    
    def add_product(self, name, sku, purchase_price, selling_price, category, barcode=None, min_stock=10):
        """Add a new product"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO products (name, sku, purchase_price, selling_price, category, barcode, min_stock)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (name, sku, purchase_price, selling_price, category, barcode, min_stock))
            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            return None
        finally:
            conn.close()
    
    def get_product(self, product_id):
        """Get product by ID"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
    
    def get_all_products(self):
        """Get all products"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM products ORDER BY name")
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def search_products(self, query):
        """Search products"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM products WHERE name LIKE ? OR sku LIKE ? ORDER BY name",
            (f'%{query}%', f'%{query}%')
        )
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def get_product_by_sku(self, sku):
        """Get product by SKU"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM products WHERE sku = ?", (sku,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
    
    def update_product(self, product_id, **kwargs):
        """Update product"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        updates = ", ".join([f"{k} = ?" for k in kwargs.keys()])
        values = list(kwargs.values()) + [product_id]
        
        cursor.execute(f"UPDATE products SET {updates}, updated_at = CURRENT_TIMESTAMP WHERE id = ?", values)
        conn.commit()
        conn.close()
        return True
    
    def delete_product(self, product_id):
        """Delete product"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
        conn.commit()
        conn.close()
        return True
    
    def remove_stock(self, product_id, quantity, reason='Sale'):
        """Remove stock"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT quantity FROM products WHERE id = ?", (product_id,))
        row = cursor.fetchone()
        
        if row and row['quantity'] >= quantity:
            cursor.execute("UPDATE products SET quantity = quantity - ? WHERE id = ?", (quantity, product_id))
            cursor.execute(
                "INSERT INTO stock_movements (product_id, quantity, type, reason) VALUES (?, ?, ?, ?)",
                (product_id, quantity, 'out', reason)
            )
            conn.commit()
            conn.close()
            return True
        
        conn.close()
        return False

    def add_stock(self, product_id, quantity, reason='Restock'):
        """Add stock to a product and create a stock movement record"""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("UPDATE products SET quantity = quantity + ? WHERE id = ?", (quantity, product_id))
            cursor.execute(
                "INSERT INTO stock_movements (product_id, quantity, type, reason) VALUES (?, ?, ?, ?)",
                (product_id, quantity, 'in', reason)
            )
            conn.commit()
            return True
        except Exception:
            return False
        finally:
            conn.close()
=======
"""
Product management module
"""

class ProductManager:
    """Manage products and inventory"""
    
    def __init__(self, db):
        self.db = db
    
    def add_product(self, name, sku, purchase_price, selling_price, category, barcode=None, min_stock=10):
        """Add a new product"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO products (name, sku, purchase_price, selling_price, category, barcode, min_stock)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (name, sku, purchase_price, selling_price, category, barcode, min_stock))
            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            return None
        finally:
            conn.close()
    
    def get_product(self, product_id):
        """Get product by ID"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
    
    def get_all_products(self):
        """Get all products"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM products ORDER BY name")
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def search_products(self, query):
        """Search products"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM products WHERE name LIKE ? OR sku LIKE ? ORDER BY name",
            (f'%{query}%', f'%{query}%')
        )
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def get_product_by_sku(self, sku):
        """Get product by SKU"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM products WHERE sku = ?", (sku,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
    
    def update_product(self, product_id, **kwargs):
        """Update product"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        updates = ", ".join([f"{k} = ?" for k in kwargs.keys()])
        values = list(kwargs.values()) + [product_id]
        
        cursor.execute(f"UPDATE products SET {updates}, updated_at = CURRENT_TIMESTAMP WHERE id = ?", values)
        conn.commit()
        conn.close()
        return True
    
    def delete_product(self, product_id):
        """Delete product"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
        conn.commit()
        conn.close()
        return True
    
    def remove_stock(self, product_id, quantity, reason='Sale'):
        """Remove stock"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT quantity FROM products WHERE id = ?", (product_id,))
        row = cursor.fetchone()
        
        if row and row['quantity'] >= quantity:
            cursor.execute("UPDATE products SET quantity = quantity - ? WHERE id = ?", (quantity, product_id))
            cursor.execute(
                "INSERT INTO stock_movements (product_id, quantity, type, reason) VALUES (?, ?, ?, ?)",
                (product_id, quantity, 'out', reason)
            )
            conn.commit()
            conn.close()
            return True
        
        conn.close()
        return False

    def add_stock(self, product_id, quantity, reason='Restock'):
        """Add stock to a product and create a stock movement record"""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("UPDATE products SET quantity = quantity + ? WHERE id = ?", (quantity, product_id))
            cursor.execute(
                "INSERT INTO stock_movements (product_id, quantity, type, reason) VALUES (?, ?, ?, ?)",
                (product_id, quantity, 'in', reason)
            )
            conn.commit()
            return True
        except Exception:
            return False
        finally:
            conn.close()
>>>>>>> 5058b63e17bc5c42e66a4f03a260eae69ba8e457
