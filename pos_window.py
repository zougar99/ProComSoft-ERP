from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QLineEdit, QDialog, QFormLayout, QDialogButtonBox, QComboBox, QTextEdit
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
from services.sale_service import SaleService
from services.product_service import ProductService
from services.customer_service import CustomerService


class POSWindow(QWidget):
    """Point of Sale window"""
    
    sale_completed = pyqtSignal(int)
    
    def __init__(self, parent=None, user=None):
        super().__init__(parent)
        self.user = user
        self.cart_items = []
        self.all_products = []
        self.init_ui()
        self.load_products()
    
    def init_ui(self):
        layout = QHBoxLayout()
        
        left_panel = QWidget()
        left_layout = QVBoxLayout()
        
        products_header = QHBoxLayout()
        products_title = QLabel('Available Products')
        products_title_font = QFont()
        products_title_font.setPointSize(14)
        products_title_font.setBold(True)
        products_title.setFont(products_title_font)
        products_header.addWidget(products_title)
        products_header.addStretch()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText('Search products...')
        self.search_input.textChanged.connect(self.filter_products)
        products_header.addWidget(self.search_input)
        
        left_layout.addLayout(products_header)
        
        self.products_table = QTableWidget()
        self.products_table.setColumnCount(4)
        self.products_table.setHorizontalHeaderLabels(['Code', 'Name', 'Price', 'Stock'])
        self.products_table.horizontalHeader().setStretchLastSection(True)
        self.products_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.products_table.setSelectionMode(QTableWidget.SingleSelection)
        self.products_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.products_table.doubleClicked.connect(self.add_to_cart)
        left_layout.addWidget(self.products_table)
        
        left_panel.setLayout(left_layout)
        layout.addWidget(left_panel, 2)
        
        right_panel = QWidget()
        right_layout = QVBoxLayout()
        
        cart_title = QLabel('Shopping Cart')
        cart_title_font = QFont()
        cart_title_font.setPointSize(14)
        cart_title_font.setBold(True)
        cart_title.setFont(cart_title_font)
        right_layout.addWidget(cart_title)
        
        self.cart_table = QTableWidget()
        self.cart_table.setColumnCount(5)
        self.cart_table.setHorizontalHeaderLabels(['Product', 'Price', 'Qty', 'Total', ''])
        self.cart_table.horizontalHeader().setStretchLastSection(True)
        self.cart_table.setEditTriggers(QTableWidget.NoEditTriggers)
        right_layout.addWidget(self.cart_table)
        
        summary_layout = QVBoxLayout()
        
        self.subtotal_label = QLabel('Subtotal: 0.00')
        self.discount_label = QLabel('Discount: 0.00')
        self.tax_label = QLabel('Tax (20%): 0.00')
        self.total_label = QLabel('Total: 0.00')
        total_font = QFont()
        total_font.setPointSize(12)
        total_font.setBold(True)
        self.total_label.setFont(total_font)
        
        summary_layout.addWidget(self.subtotal_label)
        summary_layout.addWidget(self.discount_label)
        summary_layout.addWidget(self.tax_label)
        summary_layout.addWidget(self.total_label)
        
        discount_layout = QHBoxLayout()
        discount_layout.addWidget(QLabel('Discount:'))
        self.discount_input = QLineEdit()
        self.discount_input.setPlaceholderText('0.00')
        self.discount_input.textChanged.connect(self.update_totals)
        discount_layout.addWidget(self.discount_input)
        summary_layout.addLayout(discount_layout)
        
        right_layout.addLayout(summary_layout)
        
        btn_layout = QHBoxLayout()
        
        self.clear_btn = QPushButton('Clear Cart')
        self.clear_btn.clicked.connect(self.clear_cart)
        btn_layout.addWidget(self.clear_btn)
        
        self.checkout_btn = QPushButton('Checkout')
        self.checkout_btn.setStyleSheet('background-color: #4CAF50; color: white; font-weight: bold; padding: 10px;')
        self.checkout_btn.clicked.connect(self.checkout)
        btn_layout.addWidget(self.checkout_btn)
        
        right_layout.addLayout(btn_layout)
        
        right_panel.setLayout(right_layout)
        layout.addWidget(right_panel, 1)
        
        self.setLayout(layout)
    
    def load_products(self):
        try:
            products = ProductService.list()
            self.all_products = products
            self.products_table.setRowCount(len(products))
            
            for row, product in enumerate(products):
                self.products_table.setItem(row, 0, QTableWidgetItem(product.get('code', '')))
                self.products_table.setItem(row, 1, QTableWidgetItem(product.get('name', '')))
                self.products_table.setItem(row, 2, QTableWidgetItem(str(product.get('sale_price', 0))))
                self.products_table.setItem(row, 3, QTableWidgetItem(str(product.get('stock_quantity', 0))))
                self.products_table.item(row, 0).setData(Qt.UserRole, product)
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Error loading products: {str(e)}')
    
    def filter_products(self, text):
        if not self.all_products:
            return
        
        filtered = [p for p in self.all_products 
                   if text.lower() in p.get('name', '').lower() 
                   or text.lower() in p.get('code', '').lower()]
        
        self.products_table.setRowCount(len(filtered))
        for row, product in enumerate(filtered):
            self.products_table.setItem(row, 0, QTableWidgetItem(product.get('code', '')))
            self.products_table.setItem(row, 1, QTableWidgetItem(product.get('name', '')))
            self.products_table.setItem(row, 2, QTableWidgetItem(str(product.get('sale_price', 0))))
            self.products_table.setItem(row, 3, QTableWidgetItem(str(product.get('stock_quantity', 0))))
            self.products_table.item(row, 0).setData(Qt.UserRole, product)
    
    def add_to_cart(self):
        current_row = self.products_table.currentRow()
        if current_row < 0:
            return
        
        item = self.products_table.item(current_row, 0)
        if not item:
            return
        
        product = item.data(Qt.UserRole)
        if not product:
            return
        
        stock = product.get('stock_quantity', 0)
        if stock <= 0:
            QMessageBox.warning(self, 'Warning', 'Product out of stock')
            return
        
        for i, cart_item in enumerate(self.cart_items):
            if cart_item['product_id'] == product['id']:
                if cart_item['quantity'] < stock:
                    cart_item['quantity'] += 1
                    cart_item['total'] = cart_item['price'] * cart_item['quantity']
                    self.update_cart_display()
                    return
                else:
                    QMessageBox.warning(self, 'Warning', 'Insufficient stock')
                    return
        
        price = product.get('sale_price', 0)
        self.cart_items.append({
            'product_id': product['id'],
            'name': product.get('name', ''),
            'price': price,
            'quantity': 1,
            'total': price
        })
        
        self.update_cart_display()
    
    def remove_from_cart(self, row):
        if 0 <= row < len(self.cart_items):
            self.cart_items.pop(row)
            self.update_cart_display()
    
    def clear_cart(self):
        reply = QMessageBox.question(
            self, 'Confirm',
            'Clear the cart?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.cart_items = []
            self.update_cart_display()
    
    def update_cart_display(self):
        self.cart_table.setRowCount(len(self.cart_items))
        
        for row, item in enumerate(self.cart_items):
            self.cart_table.setItem(row, 0, QTableWidgetItem(item['name']))
            self.cart_table.setItem(row, 1, QTableWidgetItem(str(item['price'])))
            self.cart_table.setItem(row, 2, QTableWidgetItem(str(item['quantity'])))
            self.cart_table.setItem(row, 3, QTableWidgetItem(str(item['total'])))
            
            remove_btn = QPushButton('X')
            remove_btn.clicked.connect(lambda checked, r=row: self.remove_from_cart(r))
            self.cart_table.setCellWidget(row, 4, remove_btn)
        
        self.update_totals()
    
    def update_totals(self):
        subtotal = sum(item['total'] for item in self.cart_items)
        
        try:
            discount = float(self.discount_input.text() or 0)
        except:
            discount = 0
        
        tax = subtotal * 0.20
        total = subtotal - discount + tax
        
        self.subtotal_label.setText(f'Subtotal: {subtotal:.2f}')
        self.discount_label.setText(f'Discount: {discount:.2f}')
        self.tax_label.setText(f'Tax (20%): {tax:.2f}')
        self.total_label.setText(f'Total: {total:.2f}')
    
    def checkout(self):
        if not self.cart_items:
            QMessageBox.warning(self, 'Warning', 'Cart is empty')
            return
        
        dialog = CheckoutDialog(self, self.cart_items, self.user)
        if dialog.exec_() == QDialog.Accepted:
            sale_data = dialog.get_sale_data()
            
            sale_data['items'] = []
            for item in self.cart_items:
                sale_data['items'].append({
                    'product_id': item['product_id'],
                    'quantity': item['quantity'],
                    'unit_price': item['price'],
                    'discount_percent': 0,
                    'line_total': item['total']
                })
            
            subtotal = sum(item['total'] for item in self.cart_items)
            try:
                discount = float(self.discount_input.text() or 0)
            except:
                discount = 0
            tax = subtotal * 0.20
            total = subtotal - discount + tax
            
            sale_data['subtotal'] = subtotal
            sale_data['discount_amount'] = discount
            sale_data['tax_amount'] = tax
            sale_data['total_amount'] = total
            sale_data['created_by'] = self.user.get('id') if self.user else 1
            
            try:
                sale = SaleService.create(sale_data)
                QMessageBox.information(self, 'Success', f'Sale completed!\nSale #: {sale["sale_number"]}')
                self.sale_completed.emit(sale['id'])
                self.clear_cart()
            except Exception as e:
                QMessageBox.critical(self, 'Error', f'Sale failed: {str(e)}')


class CheckoutDialog(QDialog):
    def __init__(self, parent=None, cart_items=None, user=None):
        super().__init__(parent)
        self.cart_items = cart_items or []
        self.user = user
        self.setWindowTitle('Checkout')
        self.setModal(True)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        form = QFormLayout()
        
        self.customer_combo = QComboBox()
        self.customer_combo.addItem('Walk-in Customer', None)
        self.load_customers()
        form.addRow('Customer:', self.customer_combo)
        
        self.payment_method = QComboBox()
        self.payment_method.addItems(['Cash', 'Card', 'Check', 'Transfer'])
        form.addRow('Payment Method:', self.payment_method)
        
        self.notes_input = QTextEdit()
        self.notes_input.setMaximumHeight(80)
        form.addRow('Notes:', self.notes_input)
        
        layout.addLayout(form)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.setLayout(layout)
        self.resize(400, 200)
    
    def load_customers(self):
        try:
            customers = CustomerService.list()
            for customer in customers:
                self.customer_combo.addItem(f"{customer['code']} - {customer['name']}", customer['id'])
        except:
            pass
    
    def get_sale_data(self):
        payment_methods = {'Cash': 'cash', 'Card': 'card', 'Check': 'check', 'Transfer': 'transfer'}
        
        return {
            'customer_id': self.customer_combo.currentData(),
            'payment_method': payment_methods.get(self.payment_method.currentText(), 'cash'),
            'payment_status': 'paid' if self.payment_method.currentText() == 'Cash' else 'unpaid',
            'notes': self.notes_input.toPlainText()
        }
