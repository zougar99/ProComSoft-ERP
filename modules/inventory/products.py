# -*- coding: utf-8 -*-
"""
وحدة إدارة المنتجات والمخزون
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                             QTableWidgetItem, QPushButton, QLineEdit, QDialog,
                             QFormLayout, QMessageBox, QComboBox, QDoubleSpinBox)
from PyQt5.QtCore import Qt
from utils.i18n import t
from utils.helpers import generate_code
from database.models import Product, Category, InventoryItem, Warehouse, Session
from datetime import datetime


class ProductsWidget(QWidget):
    """شاشة إدارة المنتجات"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.load_products()
        
    def init_ui(self):
        """تهيئة واجهة المستخدم"""
        layout = QVBoxLayout()
        
        # شريط البحث والإجراءات
        toolbar = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(t('search') + "...")
        self.search_input.textChanged.connect(self.filter_products)
        toolbar.addWidget(self.search_input)
        
        btn_add = QPushButton(t('add') + " " + t('products'))
        btn_add.clicked.connect(self.add_product)
        toolbar.addWidget(btn_add)
        
        btn_edit = QPushButton(t('edit'))
        btn_edit.clicked.connect(self.edit_product)
        toolbar.addWidget(btn_edit)
        
        btn_delete = QPushButton(t('delete'))
        btn_delete.clicked.connect(self.delete_product)
        toolbar.addWidget(btn_delete)
        
        layout.addLayout(toolbar)
        
        # جدول المنتجات
        self.table = QTableWidget()
        self.table.setColumnCount(10)
        self.table.setHorizontalHeaderLabels([
            "ID", t('code'), "Barcode", t('name'), t('name') + " (AR)",
            "Category", "Cost", "Price", "Stock", "Min Stock"
        ])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.doubleClicked.connect(self.edit_product)
        
        layout.addWidget(self.table)
        self.setLayout(layout)
        
    def load_products(self):
        """تحميل المنتجات من قاعدة البيانات"""
        session = Session()
        try:
            products = session.query(Product).filter(Product.is_active == True).all()
            self.table.setRowCount(len(products))
            
            for row, product in enumerate(products):
                # حساب المخزون الإجمالي
                total_stock = sum([item.quantity for item in product.inventory_items])
                
                self.table.setItem(row, 0, QTableWidgetItem(str(product.id)))
                self.table.setItem(row, 1, QTableWidgetItem(product.code))
                self.table.setItem(row, 2, QTableWidgetItem(product.barcode or ""))
                self.table.setItem(row, 3, QTableWidgetItem(product.name))
                self.table.setItem(row, 4, QTableWidgetItem(product.name_ar or ""))
                self.table.setItem(row, 5, QTableWidgetItem(
                    product.category.name if product.category else ""
                ))
                self.table.setItem(row, 6, QTableWidgetItem(f"{product.cost_price:.2f}"))
                self.table.setItem(row, 7, QTableWidgetItem(f"{product.selling_price:.2f}"))
                self.table.setItem(row, 8, QTableWidgetItem(f"{total_stock:.2f}"))
                self.table.setItem(row, 9, QTableWidgetItem(f"{product.min_stock:.2f}"))
        finally:
            session.close()
            
    def filter_products(self):
        """تصفية المنتجات حسب البحث"""
        search_text = self.search_input.text().lower()
        for row in range(self.table.rowCount()):
            match = False
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                if item and search_text in item.text().lower():
                    match = True
                    break
            self.table.setRowHidden(row, not match)
            
    def add_product(self):
        """إضافة منتج جديد"""
        dialog = ProductDialog()
        if dialog.exec_() == QDialog.Accepted:
            self.load_products()
            
    def edit_product(self):
        """تعديل منتج"""
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "تحذير", "يرجى اختيار منتج للتعديل")
            return
            
        product_id = int(self.table.item(selected, 0).text())
        session = Session()
        try:
            product = session.query(Product).filter(Product.id == product_id).first()
            if product:
                dialog = ProductDialog(product)
                if dialog.exec_() == QDialog.Accepted:
                    self.load_products()
        finally:
            session.close()
            
    def delete_product(self):
        """حذف منتج"""
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "تحذير", "يرجى اختيار منتج للحذف")
            return
            
        reply = QMessageBox.question(self, "تأكيد", "هل أنت متأكد من حذف هذا المنتج؟",
                                    QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            product_id = int(self.table.item(selected, 0).text())
            session = Session()
            try:
                product = session.query(Product).filter(Product.id == product_id).first()
                if product:
                    product.is_active = False
                    session.commit()
                    self.load_products()
            finally:
                session.close()


class ProductDialog(QDialog):
    """نافذة إضافة/تعديل منتج"""
    
    def __init__(self, product=None):
        super().__init__()
        self.product = product
        self.setWindowTitle(t('add') + " " + t('products') if not product else t('edit') + " " + t('products'))
        self.setModal(True)
        self.init_ui()
        
    def init_ui(self):
        """تهيئة واجهة المستخدم"""
        layout = QVBoxLayout()
        
        form = QFormLayout()
        
        self.code_input = QLineEdit()
        form.addRow(t('code') + ":", self.code_input)
        
        self.barcode_input = QLineEdit()
        form.addRow("Barcode:", self.barcode_input)
        
        self.name_input = QLineEdit()
        form.addRow(t('name') + ":", self.name_input)
        
        self.name_ar_input = QLineEdit()
        form.addRow(t('name') + " (AR):", self.name_ar_input)
        
        self.name_fr_input = QLineEdit()
        form.addRow(t('name') + " (FR):", self.name_fr_input)
        
        self.category_combo = QComboBox()
        self.load_categories()
        form.addRow("Category:", self.category_combo)
        
        self.unit_input = QLineEdit()
        self.unit_input.setText("pcs")
        form.addRow("Unit:", self.unit_input)
        
        self.cost_price_input = QDoubleSpinBox()
        self.cost_price_input.setMaximum(999999.99)
        self.cost_price_input.setDecimals(2)
        form.addRow("Cost Price:", self.cost_price_input)
        
        self.selling_price_input = QDoubleSpinBox()
        self.selling_price_input.setMaximum(999999.99)
        self.selling_price_input.setDecimals(2)
        form.addRow("Selling Price:", self.selling_price_input)
        
        self.min_stock_input = QDoubleSpinBox()
        self.min_stock_input.setMaximum(999999.99)
        self.min_stock_input.setDecimals(2)
        form.addRow("Min Stock:", self.min_stock_input)
        
        self.tax_rate_input = QDoubleSpinBox()
        self.tax_rate_input.setMaximum(100.0)
        self.tax_rate_input.setDecimals(2)
        self.tax_rate_input.setValue(19.0)
        form.addRow("Tax Rate (%):", self.tax_rate_input)
        
        layout.addLayout(form)
        
        # أزرار
        buttons = QHBoxLayout()
        buttons.addStretch()
        
        btn_save = QPushButton(t('save'))
        btn_save.clicked.connect(self.save_product)
        buttons.addWidget(btn_save)
        
        btn_cancel = QPushButton(t('cancel'))
        btn_cancel.clicked.connect(self.reject)
        buttons.addWidget(btn_cancel)
        
        layout.addLayout(buttons)
        self.setLayout(layout)
        
        # تحميل البيانات إذا كان تعديل
        if self.product:
            self.code_input.setText(self.product.code)
            self.barcode_input.setText(self.product.barcode or "")
            self.name_input.setText(self.product.name)
            self.name_ar_input.setText(self.product.name_ar or "")
            self.name_fr_input.setText(self.product.name_fr or "")
            self.unit_input.setText(self.product.unit)
            self.cost_price_input.setValue(self.product.cost_price)
            self.selling_price_input.setValue(self.product.selling_price)
            self.min_stock_input.setValue(self.product.min_stock)
            self.tax_rate_input.setValue(self.product.tax_rate)
            
            # تحديد الفئة
            if self.product.category_id:
                index = self.category_combo.findData(self.product.category_id)
                if index >= 0:
                    self.category_combo.setCurrentIndex(index)
                    
    def load_categories(self):
        """تحميل الفئات"""
        session = Session()
        try:
            categories = session.query(Category).filter(Category.is_active == True).all()
            self.category_combo.addItem("-- اختر فئة --", None)
            for category in categories:
                self.category_combo.addItem(category.name, category.id)
        finally:
            session.close()
            
    def save_product(self):
        """حفظ المنتج"""
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "خطأ", "يرجى إدخال اسم المنتج")
            return
            
        code = self.code_input.text().strip()
        if not code:
            QMessageBox.warning(self, "خطأ", "يرجى إدخال كود المنتج")
            return
            
        session = Session()
        try:
            # التحقق من عدم تكرار الكود
            if not self.product:
                existing = session.query(Product).filter(Product.code == code).first()
                if existing:
                    QMessageBox.warning(self, "خطأ", "كود المنتج موجود بالفعل")
                    return
                    
            if self.product:
                # تحديث
                self.product.code = code
                self.product.barcode = self.barcode_input.text().strip() or None
                self.product.name = name
                self.product.name_ar = self.name_ar_input.text().strip() or None
                self.product.name_fr = self.name_fr_input.text().strip() or None
                self.product.category_id = self.category_combo.currentData()
                self.product.unit = self.unit_input.text().strip() or "pcs"
                self.product.cost_price = self.cost_price_input.value()
                self.product.selling_price = self.selling_price_input.value()
                self.product.min_stock = self.min_stock_input.value()
                self.product.tax_rate = self.tax_rate_input.value()
            else:
                # إضافة جديد
                product = Product(
                    code=code,
                    barcode=self.barcode_input.text().strip() or None,
                    name=name,
                    name_ar=self.name_ar_input.text().strip() or None,
                    name_fr=self.name_fr_input.text().strip() or None,
                    category_id=self.category_combo.currentData(),
                    unit=self.unit_input.text().strip() or "pcs",
                    cost_price=self.cost_price_input.value(),
                    selling_price=self.selling_price_input.value(),
                    min_stock=self.min_stock_input.value(),
                    tax_rate=self.tax_rate_input.value(),
                    is_active=True
                )
                session.add(product)
                
                # إنشاء سجل مخزون افتراضي في المخزن الافتراضي
                default_warehouse = session.query(Warehouse).filter(Warehouse.is_default == True).first()
                if default_warehouse:
                    inventory_item = InventoryItem(
                        product_id=product.id,
                        warehouse_id=default_warehouse.id,
                        quantity=0.0
                    )
                    session.add(inventory_item)
                
            session.commit()
            QMessageBox.information(self, "نجح", "تم حفظ المنتج بنجاح")
            self.accept()
        except Exception as e:
            session.rollback()
            QMessageBox.critical(self, "خطأ", f"حدث خطأ أثناء الحفظ: {str(e)}")
        finally:
            session.close()

