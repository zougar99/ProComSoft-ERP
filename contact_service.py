"""
Contact Service - إدارة الاتصالات
"""

from database.init import get_database

class ContactService:
    @staticmethod
    def create(contact_data):
        """Create new contact"""
        db = get_database()
        cursor = db.cursor()
        
        # If this is set as primary, unset other primaries
        if contact_data.get('is_primary'):
            if contact_data.get('customer_id'):
                cursor.execute('''
                    UPDATE contacts 
                    SET is_primary = 0 
                    WHERE customer_id = ?
                ''', (contact_data['customer_id'],))
            elif contact_data.get('supplier_id'):
                cursor.execute('''
                    UPDATE contacts 
                    SET is_primary = 0 
                    WHERE supplier_id = ?
                ''', (contact_data['supplier_id'],))
        
        cursor.execute('''
            INSERT INTO contacts (
                customer_id, supplier_id, first_name, last_name,
                job_title, email, phone, mobile, department,
                is_primary, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            contact_data.get('customer_id'),
            contact_data.get('supplier_id'),
            contact_data['first_name'],
            contact_data.get('last_name'),
            contact_data.get('job_title'),
            contact_data.get('email'),
            contact_data.get('phone'),
            contact_data.get('mobile'),
            contact_data.get('department'),
            contact_data.get('is_primary', 0),
            contact_data.get('notes')
        ))
        
        db.commit()
        return ContactService.get(cursor.lastrowid)
    
    @staticmethod
    def get(contact_id):
        """Get contact by ID"""
        db = get_database()
        cursor = db.cursor()
        
        cursor.execute('''
            SELECT c.*, 
                   cust.name as customer_name, cust.code as customer_code,
                   supp.name as supplier_name, supp.code as supplier_code
            FROM contacts c
            LEFT JOIN customers cust ON c.customer_id = cust.id
            LEFT JOIN suppliers supp ON c.supplier_id = supp.id
            WHERE c.id = ?
        ''', (contact_id,))
        
        row = cursor.fetchone()
        return dict(row) if row else None
    
    @staticmethod
    def list(customer_id=None, supplier_id=None):
        """List contacts"""
        db = get_database()
        cursor = db.cursor()
        
        query = '''
            SELECT c.*, 
                   cust.name as customer_name, cust.code as customer_code,
                   supp.name as supplier_name, supp.code as supplier_code
            FROM contacts c
            LEFT JOIN customers cust ON c.customer_id = cust.id
            LEFT JOIN suppliers supp ON c.supplier_id = supp.id
            WHERE 1=1
        '''
        params = []
        
        if customer_id:
            query += ' AND c.customer_id = ?'
            params.append(customer_id)
        
        if supplier_id:
            query += ' AND c.supplier_id = ?'
            params.append(supplier_id)
        
        query += ' ORDER BY c.is_primary DESC, c.first_name, c.last_name'
        
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]
    
    @staticmethod
    def update(contact_id, contact_data):
        """Update contact"""
        db = get_database()
        cursor = db.cursor()
        
        # Get current contact
        current = ContactService.get(contact_id)
        if not current:
            raise ValueError('Contact not found')
        
        # If this is set as primary, unset other primaries
        if contact_data.get('is_primary'):
            if current.get('customer_id'):
                cursor.execute('''
                    UPDATE contacts 
                    SET is_primary = 0 
                    WHERE customer_id = ? AND id != ?
                ''', (current['customer_id'], contact_id))
            elif current.get('supplier_id'):
                cursor.execute('''
                    UPDATE contacts 
                    SET is_primary = 0 
                    WHERE supplier_id = ? AND id != ?
                ''', (current['supplier_id'], contact_id))
        
        cursor.execute('''
            UPDATE contacts SET
                first_name = ?, last_name = ?, job_title = ?,
                email = ?, phone = ?, mobile = ?, department = ?,
                is_primary = ?, notes = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (
            contact_data.get('first_name'),
            contact_data.get('last_name'),
            contact_data.get('job_title'),
            contact_data.get('email'),
            contact_data.get('phone'),
            contact_data.get('mobile'),
            contact_data.get('department'),
            contact_data.get('is_primary', 0),
            contact_data.get('notes'),
            contact_id
        ))
        
        db.commit()
        return ContactService.get(contact_id)
    
    @staticmethod
    def delete(contact_id):
        """Delete contact"""
        db = get_database()
        db.execute('DELETE FROM contacts WHERE id = ?', (contact_id,))
        db.commit()
        return True

