"""
Address Service - إدارة العناوين المتعددة
"""

from database.init import get_database

class AddressService:
    @staticmethod
    def create(address_data):
        """Create new address"""
        db = get_database()
        cursor = db.cursor()
        
        # If this is set as default, unset other defaults
        if address_data.get('is_default'):
            cursor.execute('''
                UPDATE customer_addresses 
                SET is_default = 0 
                WHERE customer_id = ? AND address_type = ?
            ''', (address_data['customer_id'], address_data['address_type']))
        
        cursor.execute('''
            INSERT INTO customer_addresses (
                customer_id, address_type, name, address, city,
                postal_code, country, phone, is_default, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            address_data['customer_id'],
            address_data['address_type'],
            address_data.get('name'),
            address_data.get('address'),
            address_data.get('city'),
            address_data.get('postal_code'),
            address_data.get('country', 'Morocco'),
            address_data.get('phone'),
            address_data.get('is_default', 0),
            address_data.get('notes')
        ))
        
        db.commit()
        return AddressService.get(cursor.lastrowid)
    
    @staticmethod
    def get(address_id):
        """Get address by ID"""
        db = get_database()
        cursor = db.cursor()
        
        cursor.execute('''
            SELECT a.*, c.name as customer_name, c.code as customer_code
            FROM customer_addresses a
            LEFT JOIN customers c ON a.customer_id = c.id
            WHERE a.id = ?
        ''', (address_id,))
        
        row = cursor.fetchone()
        return dict(row) if row else None
    
    @staticmethod
    def list(customer_id=None, address_type=None):
        """List addresses"""
        db = get_database()
        cursor = db.cursor()
        
        query = '''
            SELECT a.*, c.name as customer_name, c.code as customer_code
            FROM customer_addresses a
            LEFT JOIN customers c ON a.customer_id = c.id
            WHERE 1=1
        '''
        params = []
        
        if customer_id:
            query += ' AND a.customer_id = ?'
            params.append(customer_id)
        
        if address_type:
            query += ' AND a.address_type = ?'
            params.append(address_type)
        
        query += ' ORDER BY a.is_default DESC, a.created_at DESC'
        
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]
    
    @staticmethod
    def update(address_id, address_data):
        """Update address"""
        db = get_database()
        cursor = db.cursor()
        
        # Get current address to check customer_id
        current = AddressService.get(address_id)
        if not current:
            raise ValueError('Address not found')
        
        # If this is set as default, unset other defaults
        if address_data.get('is_default'):
            cursor.execute('''
                UPDATE customer_addresses 
                SET is_default = 0 
                WHERE customer_id = ? AND address_type = ? AND id != ?
            ''', (current['customer_id'], current['address_type'], address_id))
        
        cursor.execute('''
            UPDATE customer_addresses SET
                name = ?, address = ?, city = ?,
                postal_code = ?, country = ?, phone = ?,
                is_default = ?, notes = ?
            WHERE id = ?
        ''', (
            address_data.get('name'),
            address_data.get('address'),
            address_data.get('city'),
            address_data.get('postal_code'),
            address_data.get('country'),
            address_data.get('phone'),
            address_data.get('is_default', 0),
            address_data.get('notes'),
            address_id
        ))
        
        db.commit()
        return AddressService.get(address_id)
    
    @staticmethod
    def delete(address_id):
        """Delete address"""
        db = get_database()
        db.execute('DELETE FROM customer_addresses WHERE id = ?', (address_id,))
        db.commit()
        return True
    
    @staticmethod
    def get_default(customer_id, address_type):
        """Get default address for customer and type"""
        db = get_database()
        cursor = db.cursor()
        
        cursor.execute('''
            SELECT * FROM customer_addresses
            WHERE customer_id = ? AND address_type = ? AND is_default = 1
            LIMIT 1
        ''', (customer_id, address_type))
        
        row = cursor.fetchone()
        return dict(row) if row else None

