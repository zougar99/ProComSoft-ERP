"""
Pricing Service - إدارة التعريفات/الأسعار
"""

from datetime import datetime
from database.init import get_database

class PricingService:
    @staticmethod
    def create(tariff_data):
        """Create new pricing tariff"""
        db = get_database()
        cursor = db.cursor()
        
        cursor.execute('''
            INSERT INTO pricing_tariffs (
                name, name_ar, name_fr, valid_from, valid_until,
                is_active, notes, created_by
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            tariff_data['name'],
            tariff_data.get('name_ar'),
            tariff_data.get('name_fr'),
            tariff_data.get('valid_from'),
            tariff_data.get('valid_until'),
            tariff_data.get('is_active', 1),
            tariff_data.get('notes'),
            tariff_data.get('created_by')
        ))
        
        tariff_id = cursor.lastrowid
        
        # Insert tariff items
        if 'items' in tariff_data:
            for item in tariff_data['items']:
                cursor.execute('''
                    INSERT INTO pricing_tariff_items (
                        tariff_id, product_id, customer_id, category_id,
                        price, discount_percent, min_quantity
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    tariff_id,
                    item.get('product_id'),
                    item.get('customer_id'),
                    item.get('category_id'),
                    item['price'],
                    item.get('discount_percent', 0),
                    item.get('min_quantity', 0)
                ))
        
        db.commit()
        return PricingService.get(tariff_id)
    
    @staticmethod
    def get(tariff_id):
        """Get tariff by ID"""
        db = get_database()
        cursor = db.cursor()
        
        cursor.execute('''
            SELECT t.*, u.full_name as created_by_name
            FROM pricing_tariffs t
            LEFT JOIN users u ON t.created_by = u.id
            WHERE t.id = ?
        ''', (tariff_id,))
        
        row = cursor.fetchone()
        if not row:
            return None
        
        tariff_dict = dict(row)
        
        # Get tariff items
        cursor.execute('''
            SELECT ti.*, 
                   p.code as product_code, p.name as product_name,
                   c.name as customer_name, c.code as customer_code,
                   cat.name as category_name, cat.code as category_code
            FROM pricing_tariff_items ti
            LEFT JOIN products p ON ti.product_id = p.id
            LEFT JOIN customers c ON ti.customer_id = c.id
            LEFT JOIN categories cat ON ti.category_id = cat.id
            WHERE ti.tariff_id = ?
        ''', (tariff_id,))
        
        tariff_dict['items'] = [dict(row) for row in cursor.fetchall()]
        
        return tariff_dict
    
    @staticmethod
    def list(filters=None):
        """List tariffs with filters"""
        db = get_database()
        cursor = db.cursor()
        
        query = '''
            SELECT t.*, u.full_name as created_by_name
            FROM pricing_tariffs t
            LEFT JOIN users u ON t.created_by = u.id
            WHERE 1=1
        '''
        params = []
        
        if filters:
            if filters.get('is_active') is not None:
                query += ' AND t.is_active = ?'
                params.append(filters['is_active'])
        
        query += ' ORDER BY t.created_at DESC'
        
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]
    
    @staticmethod
    def update(tariff_id, tariff_data):
        """Update tariff"""
        db = get_database()
        cursor = db.cursor()
        
        cursor.execute('''
            UPDATE pricing_tariffs SET
                name = ?, name_ar = ?, name_fr = ?,
                valid_from = ?, valid_until = ?,
                is_active = ?, notes = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (
            tariff_data.get('name'),
            tariff_data.get('name_ar'),
            tariff_data.get('name_fr'),
            tariff_data.get('valid_from'),
            tariff_data.get('valid_until'),
            tariff_data.get('is_active', 1),
            tariff_data.get('notes'),
            tariff_id
        ))
        
        # Delete old items
        cursor.execute('DELETE FROM pricing_tariff_items WHERE tariff_id = ?', (tariff_id,))
        
        # Insert new items
        if 'items' in tariff_data:
            for item in tariff_data['items']:
                cursor.execute('''
                    INSERT INTO pricing_tariff_items (
                        tariff_id, product_id, customer_id, category_id,
                        price, discount_percent, min_quantity
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    tariff_id,
                    item.get('product_id'),
                    item.get('customer_id'),
                    item.get('category_id'),
                    item['price'],
                    item.get('discount_percent', 0),
                    item.get('min_quantity', 0)
                ))
        
        db.commit()
        return PricingService.get(tariff_id)
    
    @staticmethod
    def delete(tariff_id):
        """Delete tariff"""
        db = get_database()
        db.execute('DELETE FROM pricing_tariffs WHERE id = ?', (tariff_id,))
        db.commit()
        return True
    
    @staticmethod
    def get_price(product_id, customer_id=None, category_id=None, quantity=1):
        """Get price for product based on tariffs"""
        db = get_database()
        cursor = db.cursor()
        
        # Get product base price
        cursor.execute('SELECT sale_price FROM products WHERE id = ?', (product_id,))
        product = cursor.fetchone()
        base_price = product['sale_price'] if product else 0
        
        # Try to find matching tariff
        query = '''
            SELECT ti.price, ti.discount_percent, ti.min_quantity
            FROM pricing_tariff_items ti
            INNER JOIN pricing_tariffs t ON ti.tariff_id = t.id
            WHERE t.is_active = 1
            AND (t.valid_from IS NULL OR t.valid_from <= DATE('now'))
            AND (t.valid_until IS NULL OR t.valid_until >= DATE('now'))
            AND ti.product_id = ?
            AND (ti.min_quantity = 0 OR ti.min_quantity <= ?)
        '''
        params = [product_id, quantity]
        
        if customer_id:
            query += ' AND (ti.customer_id IS NULL OR ti.customer_id = ?)'
            params.append(customer_id)
        
        if category_id:
            query += ' AND (ti.category_id IS NULL OR ti.category_id = ?)'
            params.append(category_id)
        
        query += ' ORDER BY ti.min_quantity DESC, ti.customer_id DESC LIMIT 1'
        
        cursor.execute(query, params)
        tariff_item = cursor.fetchone()
        
        if tariff_item:
            price = tariff_item['price']
            if tariff_item['discount_percent']:
                price = price * (1 - tariff_item['discount_percent'] / 100)
            return price
        
        return base_price

