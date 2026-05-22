"""
Sales and invoicing module
"""
from pos_app.utils.auth import generate_invoice_number
from pos_app.utils.printer import ReceiptPrinter
from datetime import datetime

class SalesManager:
    """Manage sales and invoices"""
    
    def __init__(self, db):
        self.db = db
        self.printer = ReceiptPrinter()
    
    def get_next_invoice_number(self):
        """Generate next invoice number"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT invoice_number FROM invoices ORDER BY id DESC LIMIT 1")
        row = cursor.fetchone()
        conn.close()
        
        last_number = row['invoice_number'] if row else None
        return generate_invoice_number(last_number)
    
    def create_invoice(self, customer_id, cashier_id, payment_method, items, discount=0, tax=0, notes=''):
        """Create invoice"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        invoice_number = self.get_next_invoice_number()
        subtotal = sum(item['subtotal'] for item in items)
        total = subtotal - discount + tax
        
        cursor.execute('''
            INSERT INTO invoices (invoice_number, customer_id, cashier_id, subtotal, discount, tax, total, payment_method, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (invoice_number, customer_id, cashier_id, subtotal, discount, tax, total, payment_method, notes))
        
        invoice_id = cursor.lastrowid
        
        for item in items:
            cursor.execute('''
                INSERT INTO invoice_items (invoice_id, product_id, quantity, unit_price, subtotal)
                VALUES (?, ?, ?, ?, ?)
            ''', (invoice_id, item['product_id'], item['quantity'], item['unit_price'], item['subtotal']))
        
        conn.commit()
        conn.close()
        return invoice_id
    
    def get_invoice(self, invoice_id):
        """Get invoice"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM invoices WHERE id = ?", (invoice_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
    
    def get_all_invoices(self, limit=100):
        """Get all invoices"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM invoices ORDER BY id DESC LIMIT ?", (limit,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def print_invoice(self, invoice_id, to_pdf=False, pdf_path=None):
        """Print invoice"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM invoices WHERE id = ?", (invoice_id,))
        invoice = dict(cursor.fetchone())
        
        cursor.execute("SELECT * FROM invoice_items WHERE invoice_id = ?", (invoice_id,))
        items_rows = cursor.fetchall()
        
        cursor.execute("SELECT full_name FROM users WHERE id = ?", (invoice['cashier_id'],))
        cashier_row = cursor.fetchone()
        
        conn.close()
        
        invoice_data = {
            'invoice_number': invoice['invoice_number'],
            'date': invoice['created_at'],
            'cashier': cashier_row['full_name'] if cashier_row else 'Unknown',
            'subtotal': invoice['subtotal'],
            'discount': invoice['discount'],
            'tax': invoice['tax'],
            'total': invoice['total'],
            'payment_method': invoice['payment_method'],
            'items': [dict(item) for item in items_rows]
        }
        
        try:
            result = self.printer.print_receipt(invoice_data, to_pdf=to_pdf, pdf_path=pdf_path)
            return True, result
        except Exception as e:
            return False, str(e)
