# -*- coding: utf-8 -*-
"""
وحدة المبيعات والفواتير
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                             QTableWidgetItem, QPushButton, QLineEdit, QDialog,
                             QFormLayout, QMessageBox, QComboBox, QDoubleSpinBox,
                             QDateEdit, QLabel, QHeaderView)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont
from utils.i18n import t
from utils.helpers import generate_code, calculate_tax, calculate_total
from database.models import (Sale, SaleItem, Customer, Product, InventoryItem,
                            Warehouse, Invoice, Session)
from datetime import datetime


class SalesWidget(QWidget):
    """شاشة إدارة المبيعات"""
    
    def __init__(self, current_user=None):
        super().__init__()
        self.current_user = current_user
        self.init_ui()
        self.load_sales()
        
    def init_ui(self):
        """تهيئة واجهة المستخدم"""
        layout = QVBoxLayout()
        
        # شريط البحث والإجراءات
        toolbar = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(t('search') + "...")
        self.search_input.textChanged.connect(self.filter_sales)
        toolbar.addWidget(self.search_input)
        
        btn_new = QPushButton("فاتورة جديدة")
        btn_new.clicked.connect(self.new_invoice)
        toolbar.addWidget(btn_new)
        
        btn_view = QPushButton("عرض")
        btn_view.clicked.connect(self.view_sale)
        toolbar.addWidget(btn_view)
        
        btn_print = QPushButton("طباعة")
        btn_print.clicked.connect(self.print_invoice)
        toolbar.addWidget(btn_print)
        
        layout.addLayout(toolbar)
        
        # جدول المبيعات
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "ID", "Number", t('date'), "Customer", "Type", t('total'),
            "Paid", t('status')
        ])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.doubleClicked.connect(self.view_sale)
        
        layout.addWidget(self.table)
        self.setLayout(layout)
        
    def load_sales(self):
        """تحميل المبيعات من قاعدة البيانات"""
        session = Session()
        try:
            sales = session.query(Sale).order_by(Sale.date.desc()).limit(100).all()
            self.table.setRowCount(len(sales))
            
            for row, sale in enumerate(sales):
                self.table.setItem(row, 0, QTableWidgetItem(str(sale.id)))
                self.table.setItem(row, 1, QTableWidgetItem(sale.number))
                self.table.setItem(row, 2, QTableWidgetItem(sale.date.strftime("%Y-%m-%d")))
                self.table.setItem(row, 3, QTableWidgetItem(
                    sale.customer.name if sale.customer else ""
                ))
                self.table.setItem(row, 4, QTableWidgetItem(sale.type))
                self.table.setItem(row, 5, QTableWidgetItem(f"{sale.total:.2f}"))
                self.table.setItem(row, 6, QTableWidgetItem(f"{sale.paid_amount:.2f}"))
                self.table.setItem(row, 7, QTableWidgetItem(sale.status))
        finally:
            session.close()
            
    def filter_sales(self):
        """تصفية المبيعات حسب البحث"""
        search_text = self.search_input.text().lower()
        for row in range(self.table.rowCount()):
            match = False
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                if item and search_text in item.text().lower():
                    match = True
                    break
            self.table.setRowHidden(row, not match)
            
    def new_invoice(self):
        """فاتورة جديدة"""
        dialog = InvoiceDialog(current_user=self.current_user)
        if dialog.exec_() == QDialog.Accepted:
            self.load_sales()
            
    def view_sale(self):
        """عرض تفاصيل البيع"""
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "تحذير", "يرجى اختيار فاتورة للعرض")
            return
            
        sale_id = int(self.table.item(selected, 0).text())
        session = Session()
        try:
            sale = session.query(Sale).filter(Sale.id == sale_id).first()
            if sale:
                dialog = InvoiceDialog(sale)
                dialog.exec_()
        finally:
            session.close()
            
    def print_invoice(self):
        """طباعة الفاتورة"""
        QMessageBox.information(self, "قريباً", "ميزة الطباعة قيد التطوير")


class InvoiceDialog(QDialog):
    """نافذة إنشاء/تعديل فاتورة"""
    
    def __init__(self, sale=None, current_user=None):
        super().__init__()
        self.sale = sale
        self.current_user = current_user
        if not self.current_user:
            # محاولة الحصول على المستخدم الحالي من الجلسة
            from database.models import Session, User
            session = Session()
            try:
                admin = session.query(User).filter(User.username == 'admin').first()
                if admin:
                    self.current_user = admin
            finally:
                session.close()
        self.items = []
        self.setWindowTitle("فاتورة جديدة" if not sale else "عرض الفاتورة")
        self.setModal(True)
        self.resize(900, 600)
        self.init_ui()
        
        if sale:
            self.load_sale_data()
        
    def init_ui(self):
        """تهيئة واجهة المستخدم"""
        layout = QVBoxLayout()
        
        # معلومات الفاتورة
        info_layout = QFormLayout()
        
        self.number_input = QLineEdit()
        self.number_input.setReadOnly(True)
        info_layout.addRow("رقم الفاتورة:", self.number_input)
        
        self.date_input = QDateEdit()
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setCalendarPopup(True)
        info_layout.addRow(t('date') + ":", self.date_input)
        
        self.customer_combo = QComboBox()
        self.load_customers()
        info_layout.addRow("Customer:", self.customer_combo)
        
        self.type_combo = QComboBox()
        self.type_combo.addItems(["invoice", "quote", "order"])
        info_layout.addRow("Type:", self.type_combo)
        
        layout.addLayout(info_layout)
        
        # جدول العناصر
        items_label = QLabel("عناصر الفاتورة:")
        items_label.setFont(QFont("Arial", 10, QFont.Bold))
        layout.addWidget(items_label)
        
        self.items_table = QTableWidget()
        self.items_table.setColumnCount(7)
        self.items_table.setHorizontalHeaderLabels([
            "Product", t('quantity'), "Unit Price", "Discount %", "Tax %", "Subtotal", "Total"
        ])
        self.items_table.horizontalHeader().setStretchLastSection(True)
        self.items_table.setSelectionBehavior(QTableWidget.SelectRows)
        
        layout.addWidget(self.items_table)
        
        # أزرار إدارة العناصر
        items_buttons = QHBoxLayout()
        btn_add_item = QPushButton("إضافة منتج")
        btn_add_item.clicked.connect(self.add_item)
        items_buttons.addWidget(btn_add_item)
        
        btn_remove_item = QPushButton("حذف منتج")
        btn_remove_item.clicked.connect(self.remove_item)
        items_buttons.addWidget(btn_remove_item)
        
        items_buttons.addStretch()
        layout.addLayout(items_buttons)
        
        # الملخص
        summary_layout = QHBoxLayout()
        
        summary_widget = QWidget()
        summary_form = QFormLayout()
        
        self.subtotal_label = QLabel("0.00")
        summary_form.addRow("المجموع الفرعي:", self.subtotal_label)
        
        self.tax_label = QLabel("0.00")
        summary_form.addRow("الضريبة:", self.tax_label)
        
        self.discount_label = QLabel("0.00")
        summary_form.addRow("الخصم:", self.discount_label)
        
        self.total_label = QLabel("0.00")
        self.total_label.setFont(QFont("Arial", 12, QFont.Bold))
        summary_form.addRow("الإجمالي:", self.total_label)
        
        summary_widget.setLayout(summary_form)
        summary_layout.addWidget(summary_widget)
        summary_layout.addStretch()
        
        layout.addLayout(summary_layout)
        
        # أزرار الحفظ
        buttons = QHBoxLayout()
        buttons.addStretch()
        
        btn_save = QPushButton(t('save'))
        btn_save.clicked.connect(self.save_invoice)
        buttons.addWidget(btn_save)
        
        btn_cancel = QPushButton(t('cancel'))
        btn_cancel.clicked.connect(self.reject)
        buttons.addWidget(btn_cancel)
        
        layout.addLayout(buttons)
        self.setLayout(layout)
        
        # توليد رقم فاتورة تلقائي
        if not self.sale:
            self.generate_invoice_number()
            
    def load_customers(self):
        """تحميل العملاء"""
        session = Session()
        try:
            customers = session.query(Customer).filter(Customer.is_active == True).all()
            self.customer_combo.addItem("-- اختر عميل --", None)
            for customer in customers:
                self.customer_combo.addItem(customer.name, customer.id)
        finally:
            session.close()
            
    def generate_invoice_number(self):
        """توليد رقم فاتورة تلقائي"""
        session = Session()
        try:
            last_sale = session.query(Sale).order_by(Sale.id.desc()).first()
            last_num = int(last_sale.number.split('-')[-1]) if last_sale else 0
            number = generate_code("INV", last_num)
            self.number_input.setText(number)
        finally:
            session.close()
            
    def add_item(self):
        """إضافة منتج للفاتورة"""
        dialog = SaleItemDialog()
        if dialog.exec_() == QDialog.Accepted:
            item_data = dialog.get_item_data()
            self.items.append(item_data)
            self.update_items_table()
            self.calculate_totals()
            
    def remove_item(self):
        """حذف منتج من الفاتورة"""
        selected = self.items_table.currentRow()
        if selected >= 0 and selected < len(self.items):
            self.items.pop(selected)
            self.update_items_table()
            self.calculate_totals()
            
    def update_items_table(self):
        """تحديث جدول العناصر"""
        self.items_table.setRowCount(len(self.items))
        for row, item in enumerate(self.items):
            self.items_table.setItem(row, 0, QTableWidgetItem(item['product_name']))
            self.items_table.setItem(row, 1, QTableWidgetItem(f"{item['quantity']:.2f}"))
            self.items_table.setItem(row, 2, QTableWidgetItem(f"{item['unit_price']:.2f}"))
            self.items_table.setItem(row, 3, QTableWidgetItem(f"{item['discount']:.2f}"))
            self.items_table.setItem(row, 4, QTableWidgetItem(f"{item['tax_rate']:.2f}"))
            self.items_table.setItem(row, 5, QTableWidgetItem(f"{item['subtotal']:.2f}"))
            self.items_table.setItem(row, 6, QTableWidgetItem(f"{item['total']:.2f}"))
            
    def calculate_totals(self):
        """حساب الإجماليات"""
        subtotal = sum([item['subtotal'] for item in self.items])
        discount = sum([item['subtotal'] * (item['discount'] / 100) for item in self.items])
        tax = sum([item['tax_amount'] for item in self.items])
        total = subtotal - discount + tax
        
        self.subtotal_label.setText(f"{subtotal:.2f}")
        self.discount_label.setText(f"{discount:.2f}")
        self.tax_label.setText(f"{tax:.2f}")
        self.total_label.setText(f"{total:.2f}")
        
    def load_sale_data(self):
        """تحميل بيانات البيع"""
        if not self.sale:
            return
            
        self.number_input.setText(self.sale.number)
        self.date_input.setDate(QDate.fromString(self.sale.date.strftime("%Y-%m-%d"), "yyyy-MM-dd"))
        
        if self.sale.customer_id:
            index = self.customer_combo.findData(self.sale.customer_id)
            if index >= 0:
                self.customer_combo.setCurrentIndex(index)
                
        index = self.type_combo.findText(self.sale.type)
        if index >= 0:
            self.type_combo.setCurrentIndex(index)
            
        # تحميل العناصر
        session = Session()
        try:
            for sale_item in self.sale.items:
                item_data = {
                    'product_id': sale_item.product_id,
                    'product_name': sale_item.product.name,
                    'quantity': sale_item.quantity,
                    'unit_price': sale_item.unit_price,
                    'discount': sale_item.discount,
                    'tax_rate': sale_item.tax_rate,
                    'tax_amount': sale_item.tax_amount,
                    'subtotal': sale_item.subtotal,
                    'total': sale_item.total
                }
                self.items.append(item_data)
            self.update_items_table()
            self.calculate_totals()
        finally:
            session.close()
            
    def save_invoice(self):
        """حفظ الفاتورة"""
        if not self.items:
            QMessageBox.warning(self, "خطأ", "يرجى إضافة منتجات للفاتورة")
            return
            
        customer_id = self.customer_combo.currentData()
        if not customer_id:
            QMessageBox.warning(self, "خطأ", "يرجى اختيار عميل")
            return
            
        session = Session()
        try:
            subtotal = sum([item['subtotal'] for item in self.items])
            discount = sum([item['subtotal'] * (item['discount'] / 100) for item in self.items])
            tax = sum([item['tax_amount'] for item in self.items])
            total = subtotal - discount + tax
            
            if self.sale:
                # تحديث
                self.sale.number = self.number_input.text()
                self.sale.date = self.date_input.date().toPyDate()
                self.sale.customer_id = customer_id
                self.sale.type = self.type_combo.currentText()
                self.sale.subtotal = subtotal
                self.sale.discount_amount = discount
                self.sale.tax_amount = tax
                self.sale.total = total
                self.sale.status = 'confirmed'
                
                # حذف العناصر القديمة
                for item in self.sale.items:
                    session.delete(item)
                    
            else:
                # إنشاء جديد
                sale = Sale(
                    number=self.number_input.text(),
                    customer_id=customer_id,
                    user_id=self.current_user.id if self.current_user else 1,
                    date=self.date_input.date().toPyDate(),
                    type=self.type_combo.currentText(),
                    subtotal=subtotal,
                    discount_amount=discount,
                    tax_amount=tax,
                    total=total,
                    status='confirmed'
                )
                session.add(sale)
                session.flush()
                self.sale = sale
                
            # إضافة العناصر
            for item_data in self.items:
                sale_item = SaleItem(
                    sale_id=self.sale.id,
                    product_id=item_data['product_id'],
                    quantity=item_data['quantity'],
                    unit_price=item_data['unit_price'],
                    discount=item_data['discount'],
                    tax_rate=item_data['tax_rate'],
                    tax_amount=item_data['tax_amount'],
                    subtotal=item_data['subtotal'],
                    total=item_data['total']
                )
                session.add(sale_item)
                
                # تحديث المخزون
                if self.sale.type == 'invoice':
                    product = session.query(Product).filter(Product.id == item_data['product_id']).first()
                    if product:
                        default_warehouse = session.query(Warehouse).filter(Warehouse.is_default == True).first()
                        if default_warehouse:
                            inventory = session.query(InventoryItem).filter(
                                InventoryItem.product_id == product.id,
                                InventoryItem.warehouse_id == default_warehouse.id
                            ).first()
                            if inventory:
                                inventory.quantity -= item_data['quantity']
                                inventory.last_updated = datetime.now()
                                
            # إنشاء فاتورة ضريبية
            if self.sale.type == 'invoice':
                invoice = Invoice(
                    number=self.sale.number,
                    sale_id=self.sale.id,
                    customer_id=customer_id,
                    date=self.sale.date,
                    subtotal=subtotal,
                    tax_amount=tax,
                    total=total,
                    status='unpaid'
                )
                session.add(invoice)
                
            session.commit()
            QMessageBox.information(self, "نجح", "تم حفظ الفاتورة بنجاح")
            self.accept()
        except Exception as e:
            session.rollback()
            QMessageBox.critical(self, "خطأ", f"حدث خطأ أثناء الحفظ: {str(e)}")
        finally:
            session.close()


class SaleItemDialog(QDialog):
    """نافذة إضافة عنصر للفاتورة"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("إضافة منتج")
        self.setModal(True)
        self.item_data = None
        self.init_ui()
        
    def init_ui(self):
        """تهيئة واجهة المستخدم"""
        layout = QFormLayout()
        
        self.product_combo = QComboBox()
        self.load_products()
        layout.addRow("Product:", self.product_combo)
        
        self.quantity_input = QDoubleSpinBox()
        self.quantity_input.setMinimum(0.01)
        self.quantity_input.setMaximum(999999.99)
        self.quantity_input.setDecimals(2)
        self.quantity_input.setValue(1.0)
        layout.addRow(t('quantity') + ":", self.quantity_input)
        
        self.unit_price_input = QDoubleSpinBox()
        self.unit_price_input.setMinimum(0.0)
        self.unit_price_input.setMaximum(999999.99)
        self.unit_price_input.setDecimals(2)
        layout.addRow("Unit Price:", self.unit_price_input)
        
        self.discount_input = QDoubleSpinBox()
        self.discount_input.setMinimum(0.0)
        self.discount_input.setMaximum(100.0)
        self.discount_input.setDecimals(2)
        layout.addRow("Discount %:", self.discount_input)
        
        self.tax_rate_input = QDoubleSpinBox()
        self.tax_rate_input.setMinimum(0.0)
        self.tax_rate_input.setMaximum(100.0)
        self.tax_rate_input.setDecimals(2)
        self.tax_rate_input.setValue(19.0)
        layout.addRow("Tax Rate %:", self.tax_rate_input)
        
        # تحديث السعر عند اختيار المنتج
        self.product_combo.currentIndexChanged.connect(self.on_product_changed)
        
        buttons = QHBoxLayout()
        buttons.addStretch()
        
        btn_add = QPushButton("إضافة")
        btn_add.clicked.connect(self.add_item)
        buttons.addWidget(btn_add)
        
        btn_cancel = QPushButton(t('cancel'))
        btn_cancel.clicked.connect(self.reject)
        buttons.addWidget(btn_cancel)
        
        layout.addLayout(buttons)
        self.setLayout(layout)
        
    def load_products(self):
        """تحميل المنتجات"""
        session = Session()
        try:
            products = session.query(Product).filter(Product.is_active == True).all()
            self.product_combo.addItem("-- اختر منتج --", None)
            for product in products:
                self.product_combo.addItem(f"{product.code} - {product.name}", product.id)
        finally:
            session.close()
            
    def on_product_changed(self):
        """عند تغيير المنتج"""
        product_id = self.product_combo.currentData()
        if product_id:
            session = Session()
            try:
                product = session.query(Product).filter(Product.id == product_id).first()
                if product:
                    self.unit_price_input.setValue(product.selling_price)
                    self.tax_rate_input.setValue(product.tax_rate)
            finally:
                session.close()
                
    def add_item(self):
        """إضافة العنصر"""
        product_id = self.product_combo.currentData()
        if not product_id:
            QMessageBox.warning(self, "خطأ", "يرجى اختيار منتج")
            return
            
        quantity = self.quantity_input.value()
        unit_price = self.unit_price_input.value()
        discount = self.discount_input.value()
        tax_rate = self.tax_rate_input.value()
        
        subtotal = quantity * unit_price
        discount_amount = subtotal * (discount / 100)
        subtotal_after_discount = subtotal - discount_amount
        tax_amount = subtotal_after_discount * (tax_rate / 100)
        total = subtotal_after_discount + tax_amount
        
        session = Session()
        try:
            product = session.query(Product).filter(Product.id == product_id).first()
            self.item_data = {
                'product_id': product_id,
                'product_name': product.name,
                'quantity': quantity,
                'unit_price': unit_price,
                'discount': discount,
                'tax_rate': tax_rate,
                'tax_amount': tax_amount,
                'subtotal': subtotal,
                'total': total
            }
            self.accept()
        finally:
            session.close()
            
    def get_item_data(self):
        """الحصول على بيانات العنصر"""
        return self.item_data

