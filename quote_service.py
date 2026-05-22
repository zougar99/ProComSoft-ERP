"""
Quote Service - إدارة التقديرات/العروض
"""

from datetime import datetime
from database.init import get_database

class QuoteService:
    @staticmethod
    def generate_quote_number():
        """Generate unique quote number"""
        db = get_database()
        cursor = db.cursor()
        
        # Get last quote number
        cursor.execute('''
            SELECT quote_number FROM quotes 
            ORDER BY id DESC LIMIT 1
        ''')
        
        last_quote = cursor.fetchone()
        if last_quote:
            try:
                last_num = int(last_quote['quote_number'].split('-')[-1])
                new_num = last_num + 1
            except:
                new_num = 1
        else:
            new_num = 1
        
        year = datetime.now().year
        return f'QT-{year}-{new_num:05d}'
    
    @staticmethod
    def create(quote_data):
        """Create new quote"""
        db = get_database()
        cursor = db.cursor()
        
        # Generate quote number if not provided
        if not quote_data.get('quote_number'):
            quote_data['quote_number'] = QuoteService.generate_quote_number()
        
        # Insert quote
        cursor.execute('''
            INSERT INTO quotes (
                quote_number, customer_id, quote_date, valid_until,
                subtotal, tax_amount, discount_amount, total_amount,
                status, currency, exchange_rate, notes, created_by
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            quote_data['quote_number'],
            quote_data['customer_id'],
            quote_data['quote_date'],
            quote_data.get('valid_until'),
            quote_data.get('subtotal', 0),
            quote_data.get('tax_amount', 0),
            quote_data.get('discount_amount', 0),
            quote_data.get('total_amount', 0),
            quote_data.get('status', 'draft'),
            quote_data.get('currency', 'MAD'),
            quote_data.get('exchange_rate', 1),
            quote_data.get('notes'),
            quote_data.get('created_by')
        ))
        
        quote_id = cursor.lastrowid
        
        # Insert quote items
        if 'items' in quote_data:
            for item in quote_data['items']:
                cursor.execute('''
                    INSERT INTO quote_items (
                        quote_id, product_id, description, quantity,
                        unit_price, discount_percent, tax_rate, line_total, sort_order
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    quote_id,
                    item.get('product_id'),
                    item.get('description'),
                    item['quantity'],
                    item['unit_price'],
                    item.get('discount_percent', 0),
                    item.get('tax_rate', 0),
                    item['line_total'],
                    item.get('sort_order', 0)
                ))
        
        db.commit()
        return QuoteService.get(quote_id)
    
    @staticmethod
    def get(quote_id):
        """Get quote by ID"""
        db = get_database()
        cursor = db.cursor()
        
        cursor.execute('''
            SELECT q.*, c.name as customer_name, c.code as customer_code
            FROM quotes q
            LEFT JOIN customers c ON q.customer_id = c.id
            WHERE q.id = ?
        ''', (quote_id,))
        
        quote = cursor.fetchone()
        if not quote:
            return None
        
        quote_dict = dict(quote)
        
        # Get quote items
        cursor.execute('''
            SELECT qi.*, p.code as product_code, p.name as product_name
            FROM quote_items qi
            LEFT JOIN products p ON qi.product_id = p.id
            WHERE qi.quote_id = ?
            ORDER BY qi.sort_order
        ''', (quote_id,))
        
        quote_dict['items'] = [dict(row) for row in cursor.fetchall()]
        
        return quote_dict
    
    @staticmethod
    def list(filters=None):
        """List quotes with filters"""
        db = get_database()
        cursor = db.cursor()
        
        query = '''
            SELECT q.*, c.name as customer_name, c.code as customer_code
            FROM quotes q
            LEFT JOIN customers c ON q.customer_id = c.id
            WHERE 1=1
        '''
        params = []
        
        if filters:
            if filters.get('customer_id'):
                query += ' AND q.customer_id = ?'
                params.append(filters['customer_id'])
            
            if filters.get('status'):
                query += ' AND q.status = ?'
                params.append(filters['status'])
            
            if filters.get('date_from'):
                query += ' AND q.quote_date >= ?'
                params.append(filters['date_from'])
            
            if filters.get('date_to'):
                query += ' AND q.quote_date <= ?'
                params.append(filters['date_to'])
        
        query += ' ORDER BY q.quote_date DESC, q.id DESC'
        
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]
    
    @staticmethod
    def update(quote_id, quote_data):
        """Update quote"""
        db = get_database()
        cursor = db.cursor()
        
        # Update quote
        cursor.execute('''
            UPDATE quotes SET
                customer_id = ?, quote_date = ?, valid_until = ?,
                subtotal = ?, tax_amount = ?, discount_amount = ?, total_amount = ?,
                status = ?, currency = ?, exchange_rate = ?, notes = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (
            quote_data.get('customer_id'),
            quote_data.get('quote_date'),
            quote_data.get('valid_until'),
            quote_data.get('subtotal', 0),
            quote_data.get('tax_amount', 0),
            quote_data.get('discount_amount', 0),
            quote_data.get('total_amount', 0),
            quote_data.get('status'),
            quote_data.get('currency', 'MAD'),
            quote_data.get('exchange_rate', 1),
            quote_data.get('notes'),
            quote_id
        ))
        
        # Delete old items
        cursor.execute('DELETE FROM quote_items WHERE quote_id = ?', (quote_id,))
        
        # Insert new items
        if 'items' in quote_data:
            for item in quote_data['items']:
                cursor.execute('''
                    INSERT INTO quote_items (
                        quote_id, product_id, description, quantity,
                        unit_price, discount_percent, tax_rate, line_total, sort_order
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    quote_id,
                    item.get('product_id'),
                    item.get('description'),
                    item['quantity'],
                    item['unit_price'],
                    item.get('discount_percent', 0),
                    item.get('tax_rate', 0),
                    item['line_total'],
                    item.get('sort_order', 0)
                ))
        
        db.commit()
        return QuoteService.get(quote_id)
    
    @staticmethod
    def delete(quote_id):
        """Delete quote"""
        db = get_database()
        db.execute('DELETE FROM quotes WHERE id = ?', (quote_id,))
        db.commit()
        return True
    
    @staticmethod
    def convert_to_invoice(quote_id, invoice_data):
        """Convert quote to invoice"""
        # Note: InvoiceService will be implemented separately
        # For now, this method prepares the data structure
        
        quote = QuoteService.get(quote_id)
        if not quote:
            raise ValueError('Quote not found')
        
        # Prepare invoice data from quote
        invoice_data['invoice_type'] = invoice_data.get('invoice_type', 'sale')
        invoice_data['customer_id'] = quote['customer_id']
        invoice_data['invoice_date'] = invoice_data.get('invoice_date', datetime.now().date().isoformat())
        invoice_data['items'] = []
        
        for item in quote['items']:
            invoice_data['items'].append({
                'product_id': item.get('product_id'),
                'description': item.get('description'),
                'quantity': item['quantity'],
                'unit_price': item['unit_price'],
                'discount_percent': item.get('discount_percent', 0),
                'tax_rate': item.get('tax_rate', 0),
                'line_total': item['line_total'],
                'sort_order': item.get('sort_order', 0)
            })
        
        invoice_data['subtotal'] = quote.get('subtotal', 0)
        invoice_data['tax_amount'] = quote.get('tax_amount', 0)
        invoice_data['discount_amount'] = quote.get('discount_amount', 0)
        invoice_data['total_amount'] = quote.get('total_amount', 0)
        
        # TODO: Create invoice using InvoiceService when available
        # For now, just update quote status
        db = get_database()
        db.execute('''
            UPDATE quotes SET
                status = 'converted',
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (quote_id,))
        db.commit()
        
        return invoice_data

