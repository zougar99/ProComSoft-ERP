# -*- coding: utf-8 -*-
"""
وحدة إدارة العملاء (CRM)
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                             QTableWidgetItem, QPushButton, QLineEdit, QDialog,
                             QFormLayout, QMessageBox, QHeaderView, QLabel)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from utils.i18n import t
from utils.helpers import validate_email, validate_phone, generate_code
from database.models import Customer, Session
from datetime import datetime


class CustomersWidget(QWidget):
    """شاشة إدارة العملاء"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.load_customers()
        
    def init_ui(self):
        """تهيئة واجهة المستخدم"""
        layout = QVBoxLayout()
        
        # شريط البحث والإجراءات
        toolbar = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(t('search') + "...")
        self.search_input.textChanged.connect(self.filter_customers)
        toolbar.addWidget(self.search_input)
        
        btn_add = QPushButton(t('add') + " " + t('customers'))
        btn_add.clicked.connect(self.add_customer)
        toolbar.addWidget(btn_add)
        
        btn_edit = QPushButton(t('edit'))
        btn_edit.clicked.connect(self.edit_customer)
        toolbar.addWidget(btn_edit)
        
        btn_delete = QPushButton(t('delete'))
        btn_delete.clicked.connect(self.delete_customer)
        toolbar.addWidget(btn_delete)
        
        layout.addLayout(toolbar)
        
        # جدول العملاء
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "ID", t('code'), t('name'), t('name') + " (AR)", t('name') + " (FR)",
            "Phone", "Email", t('balance')
        ])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.doubleClicked.connect(self.edit_customer)
        
        layout.addWidget(self.table)
        self.setLayout(layout)
        
    def load_customers(self):
        """تحميل العملاء من قاعدة البيانات"""
        session = Session()
        try:
            customers = session.query(Customer).filter(Customer.is_active == True).all()
            self.table.setRowCount(len(customers))
            
            for row, customer in enumerate(customers):
                self.table.setItem(row, 0, QTableWidgetItem(str(customer.id)))
                self.table.setItem(row, 1, QTableWidgetItem(customer.code or ""))
                self.table.setItem(row, 2, QTableWidgetItem(customer.name))
                self.table.setItem(row, 3, QTableWidgetItem(customer.name_ar or ""))
                self.table.setItem(row, 4, QTableWidgetItem(customer.name_fr or ""))
                self.table.setItem(row, 5, QTableWidgetItem(customer.phone or ""))
                self.table.setItem(row, 6, QTableWidgetItem(customer.email or ""))
                self.table.setItem(row, 7, QTableWidgetItem(f"{customer.balance:.2f}"))
        finally:
            session.close()
            
    def filter_customers(self):
        """تصفية العملاء حسب البحث"""
        search_text = self.search_input.text().lower()
        for row in range(self.table.rowCount()):
            match = False
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                if item and search_text in item.text().lower():
                    match = True
                    break
            self.table.setRowHidden(row, not match)
            
    def add_customer(self):
        """إضافة عميل جديد"""
        dialog = CustomerDialog()
        if dialog.exec_() == QDialog.Accepted:
            self.load_customers()
            
    def edit_customer(self):
        """تعديل عميل"""
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "تحذير", "يرجى اختيار عميل للتعديل")
            return
            
        customer_id = int(self.table.item(selected, 0).text())
        session = Session()
        try:
            customer = session.query(Customer).filter(Customer.id == customer_id).first()
            if customer:
                dialog = CustomerDialog(customer)
                if dialog.exec_() == QDialog.Accepted:
                    self.load_customers()
        finally:
            session.close()
            
    def delete_customer(self):
        """حذف عميل"""
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "تحذير", "يرجى اختيار عميل للحذف")
            return
            
        reply = QMessageBox.question(self, "تأكيد", "هل أنت متأكد من حذف هذا العميل؟",
                                    QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            customer_id = int(self.table.item(selected, 0).text())
            session = Session()
            try:
                customer = session.query(Customer).filter(Customer.id == customer_id).first()
                if customer:
                    customer.is_active = False
                    session.commit()
                    self.load_customers()
            finally:
                session.close()


class CustomerDialog(QDialog):
    """نافذة إضافة/تعديل عميل"""
    
    def __init__(self, customer=None):
        super().__init__()
        self.customer = customer
        self.setWindowTitle(t('add') + " " + t('customers') if not customer else t('edit') + " " + t('customers'))
        self.setModal(True)
        self.init_ui()
        
    def init_ui(self):
        """تهيئة واجهة المستخدم"""
        layout = QVBoxLayout()
        
        form = QFormLayout()
        
        self.code_input = QLineEdit()
        form.addRow(t('code') + ":", self.code_input)
        
        self.name_input = QLineEdit()
        form.addRow(t('name') + ":", self.name_input)
        
        self.name_ar_input = QLineEdit()
        form.addRow(t('name') + " (AR):", self.name_ar_input)
        
        self.name_fr_input = QLineEdit()
        form.addRow(t('name') + " (FR):", self.name_fr_input)
        
        self.phone_input = QLineEdit()
        form.addRow("Phone:", self.phone_input)
        
        self.email_input = QLineEdit()
        form.addRow("Email:", self.email_input)
        
        self.address_input = QLineEdit()
        form.addRow("Address:", self.address_input)
        
        self.city_input = QLineEdit()
        form.addRow("City:", self.city_input)
        
        self.tax_id_input = QLineEdit()
        form.addRow("Tax ID:", self.tax_id_input)
        
        layout.addLayout(form)
        
        # أزرار
        buttons = QHBoxLayout()
        buttons.addStretch()
        
        btn_save = QPushButton(t('save'))
        btn_save.clicked.connect(self.save_customer)
        buttons.addWidget(btn_save)
        
        btn_cancel = QPushButton(t('cancel'))
        btn_cancel.clicked.connect(self.reject)
        buttons.addWidget(btn_cancel)
        
        layout.addLayout(buttons)
        self.setLayout(layout)
        
        # تحميل البيانات إذا كان تعديل
        if self.customer:
            self.code_input.setText(self.customer.code or "")
            self.name_input.setText(self.customer.name or "")
            self.name_ar_input.setText(self.customer.name_ar or "")
            self.name_fr_input.setText(self.customer.name_fr or "")
            self.phone_input.setText(self.customer.phone or "")
            self.email_input.setText(self.customer.email or "")
            self.address_input.setText(self.customer.address or "")
            self.city_input.setText(self.customer.city or "")
            self.tax_id_input.setText(self.customer.tax_id or "")
            
    def save_customer(self):
        """حفظ العميل"""
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "خطأ", "يرجى إدخال اسم العميل")
            return
            
        # التحقق من البريد الإلكتروني
        email = self.email_input.text().strip()
        if email and not validate_email(email):
            QMessageBox.warning(self, "خطأ", "البريد الإلكتروني غير صحيح")
            return
            
        # التحقق من الهاتف
        phone = self.phone_input.text().strip()
        if phone and not validate_phone(phone):
            QMessageBox.warning(self, "خطأ", "رقم الهاتف غير صحيح")
            return
            
        session = Session()
        try:
            if self.customer:
                # تحديث
                self.customer.code = self.code_input.text().strip() or None
                self.customer.name = name
                self.customer.name_ar = self.name_ar_input.text().strip() or None
                self.customer.name_fr = self.name_fr_input.text().strip() or None
                self.customer.phone = phone or None
                self.customer.email = email or None
                self.customer.address = self.address_input.text().strip() or None
                self.customer.city = self.city_input.text().strip() or None
                self.customer.tax_id = self.tax_id_input.text().strip() or None
            else:
                # إضافة جديد
                code = self.code_input.text().strip()
                if not code:
                    # توليد كود تلقائي
                    last_customer = session.query(Customer).order_by(Customer.id.desc()).first()
                    last_num = int(last_customer.code.split('-')[-1]) if last_customer and last_customer.code else 0
                    code = generate_code("CUST", last_num)
                    
                customer = Customer(
                    code=code,
                    name=name,
                    name_ar=self.name_ar_input.text().strip() or None,
                    name_fr=self.name_fr_input.text().strip() or None,
                    phone=phone or None,
                    email=email or None,
                    address=self.address_input.text().strip() or None,
                    city=self.city_input.text().strip() or None,
                    tax_id=self.tax_id_input.text().strip() or None,
                    is_active=True
                )
                session.add(customer)
                
            session.commit()
            QMessageBox.information(self, "نجح", "تم حفظ العميل بنجاح")
            self.accept()
        except Exception as e:
            session.rollback()
            QMessageBox.critical(self, "خطأ", f"حدث خطأ أثناء الحفظ: {str(e)}")
        finally:
            session.close()

