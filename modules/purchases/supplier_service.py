"""
Supplier Service - إدارة الموردين
"""

from database.init import get_database

class SupplierService:
    @staticmethod
    def generate_supplier_code():
        """Generate unique supplier code"""
        db = get_database()
        cursor = db.cursor()
        
        cursor.execute('SELECT code FROM suppliers ORDER BY id DESC LIMIT 1')
        last_supplier = cursor.fetchone()
        
        if last_supplier:
            try:
                last_num = int(last_supplier['code'].split('-')[-1])
                new_num = last_num + 1
            except:
                new_num = 1
        else:
            new_num = 1
        
        return f'SUP-{new_num:05d}'
    
    @staticmethod
    def create(supplier_data):
        """Create new supplier"""
        db = get_database()
        cursor = db.cursor()
        
        # Generate code if not provided
        if not supplier_data.get('code'):
            supplier_data['code'] = SupplierService.generate_supplier_code()
        
        cursor.execute('''
            INSERT INTO suppliers (
                code, name, name_ar, name_fr, email, phone, mobile,
                address, city, country, tax_id, payment_terms,
                is_active, notes, created_by
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            supplier_data['code'],
            supplier_data['name'],
            supplier_data.get('name_ar'),
            supplier_data.get('name_fr'),
            supplier_data.get('email'),
            supplier_data.get('phone'),
            supplier_data.get('mobile'),
            supplier_data.get('address'),
            supplier_data.get('city'),
            supplier_data.get('country', 'Morocco'),
            supplier_data.get('tax_id'),
            supplier_data.get('payment_terms'),
            supplier_data.get('is_active', 1),
            supplier_data.get('notes'),
            supplier_data.get('created_by')
        ))
        
        db.commit()
        return SupplierService.get(cursor.lastrowid)
    
    @staticmethod
    def get(supplier_id):
        """Get supplier by ID"""
        db = get_database()
        cursor = db.cursor()
        
        cursor.execute('''
            SELECT s.*, u.full_name as created_by_name
            FROM suppliers s
            LEFT JOIN users u ON s.created_by = u.id
            WHERE s.id = ?
        ''', (supplier_id,))
        
        row = cursor.fetchone()
        return dict(row) if row else None
    
    @staticmethod
    def list(filters=None):
        """List suppliers with filters"""
        db = get_database()
        cursor = db.cursor()
        
        query = 'SELECT * FROM suppliers WHERE 1=1'
        params = []
        
        if filters:
            if filters.get('is_active') is not None:
                query += ' AND is_active = ?'
                params.append(filters['is_active'])
        
        query += ' ORDER BY name'
        
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]
    
    @staticmethod
    def update(supplier_id, supplier_data):
        """Update supplier"""
        db = get_database()
        cursor = db.cursor()
        
        cursor.execute('''
            UPDATE suppliers SET
                name = ?, name_ar = ?, name_fr = ?, email = ?,
                phone = ?, mobile = ?, address = ?, city = ?,
                country = ?, tax_id = ?, payment_terms = ?,
                is_active = ?, notes = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (
            supplier_data.get('name'),
            supplier_data.get('name_ar'),
            supplier_data.get('name_fr'),
            supplier_data.get('email'),
            supplier_data.get('phone'),
            supplier_data.get('mobile'),
            supplier_data.get('address'),
            supplier_data.get('city'),
            supplier_data.get('country'),
            supplier_data.get('tax_id'),
            supplier_data.get('payment_terms'),
            supplier_data.get('is_active', 1),
            supplier_data.get('notes'),
            supplier_id
        ))
        
        db.commit()
        return SupplierService.get(supplier_id)
    
    @staticmethod
    def delete(supplier_id):
        """Delete supplier"""
        db = get_database()
        db.execute('DELETE FROM suppliers WHERE id = ?', (supplier_id,))
        db.commit()
        return True

