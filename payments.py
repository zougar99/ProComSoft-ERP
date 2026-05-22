<<<<<<< HEAD
# -*- coding: utf-8 -*-
"""
وحدة إدارة المدفوعات والدفعات
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                             QTableWidgetItem, QPushButton, QLineEdit, QDialog,
                             QFormLayout, QMessageBox, QComboBox, QDoubleSpinBox,
                             QDateEdit, QLabel)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont
from utils.i18n import t
from database.models import Payment, Invoice, Customer, Session
from datetime import datetime


class PaymentsWidget(QWidget):
    """شاشة إدارة المدفوعات"""
    
    def __init__(self, invoice_id=None):
        super().__init__()
        self.invoice_id = invoice_id
        self.init_ui()
        self.load_payments()
        
    def init_ui(self):
        """تهيئة واجهة المستخدم"""
        layout = QVBoxLayout()
        
        # شريط الإجراءات
        toolbar = QHBoxLayout()
        
        btn_add = QPushButton("إضافة دفعة")
        btn_add.clicked.connect(self.add_payment)
        toolbar.addWidget(btn_add)
        
        btn_edit = QPushButton(t('edit'))
        btn_edit.clicked.connect(self.edit_payment)
        toolbar.addWidget(btn_edit)
        
        btn_delete = QPushButton(t('delete'))
        btn_delete.clicked.connect(self.delete_payment)
        toolbar.addWidget(btn_delete)
        
        toolbar.addStretch()
        layout.addLayout(toolbar)
        
        # جدول المدفوعات
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "ID", "رقم الفاتورة", t('date'), "المبلغ", "طريقة الدفع",
            "المرجع", "الملاحظات"
        ])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.doubleClicked.connect(self.edit_payment)
        
        layout.addWidget(self.table)
        self.setLayout(layout)
        
    def load_payments(self):
        """تحميل المدفوعات"""
        session = Session()
        try:
            query = session.query(Payment)
            if self.invoice_id:
                query = query.filter(Payment.invoice_id == self.invoice_id)
            payments = query.order_by(Payment.date.desc()).all()
            
            self.table.setRowCount(len(payments))
            for row, payment in enumerate(payments):
                self.table.setItem(row, 0, QTableWidgetItem(str(payment.id)))
                self.table.setItem(row, 1, QTableWidgetItem(
                    payment.invoice.number if payment.invoice else ""
                ))
                self.table.setItem(row, 2, QTableWidgetItem(
                    payment.date.strftime("%Y-%m-%d")
                ))
                self.table.setItem(row, 3, QTableWidgetItem(f"{payment.amount:.2f}"))
                self.table.setItem(row, 4, QTableWidgetItem(payment.method or ""))
                self.table.setItem(row, 5, QTableWidgetItem(payment.reference or ""))
                self.table.setItem(row, 6, QTableWidgetItem(payment.notes or ""))
        finally:
            session.close()
            
    def add_payment(self):
        """إضافة دفعة جديدة"""
        dialog = PaymentDialog(invoice_id=self.invoice_id)
        if dialog.exec_() == QDialog.Accepted:
            self.load_payments()
            
    def edit_payment(self):
        """تعديل دفعة"""
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "تحذير", "يرجى اختيار دفعة للتعديل")
            return
            
        payment_id = int(self.table.item(selected, 0).text())
        session = Session()
        try:
            payment = session.query(Payment).filter(Payment.id == payment_id).first()
            if payment:
                dialog = PaymentDialog(payment=payment)
                if dialog.exec_() == QDialog.Accepted:
                    self.load_payments()
        finally:
            session.close()
            
    def delete_payment(self):
        """حذف دفعة"""
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "تحذير", "يرجى اختيار دفعة للحذف")
            return
            
        reply = QMessageBox.question(self, "تأكيد", "هل أنت متأكد من حذف هذه الدفعة؟",
                                    QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            payment_id = int(self.table.item(selected, 0).text())
            session = Session()
            try:
                payment = session.query(Payment).filter(Payment.id == payment_id).first()
                if payment:
                    # تحديث رصيد الفاتورة
                    invoice = payment.invoice
                    if invoice:
                        invoice.paid_amount -= payment.amount
                        if invoice.paid_amount <= 0:
                            invoice.status = 'unpaid'
                        elif invoice.paid_amount >= invoice.total:
                            invoice.status = 'paid'
                        else:
                            invoice.status = 'partial'
                    
                    session.delete(payment)
                    session.commit()
                    self.load_payments()
            finally:
                session.close()


class PaymentDialog(QDialog):
    """نافذة إضافة/تعديل دفعة"""
    
    def __init__(self, payment=None, invoice_id=None):
        super().__init__()
        self.payment = payment
        self.invoice_id = invoice_id
        self.setWindowTitle("إضافة دفعة" if not payment else "تعديل دفعة")
        self.setModal(True)
        self.init_ui()
        
        if payment:
            self.load_payment_data()
            
    def init_ui(self):
        """تهيئة واجهة المستخدم"""
        layout = QVBoxLayout()
        
        form = QFormLayout()
        
        # اختيار الفاتورة
        self.invoice_combo = QComboBox()
        self.load_invoices()
        form.addRow("الفاتورة:", self.invoice_combo)
        
        # التاريخ
        self.date_input = QDateEdit()
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setCalendarPopup(True)
        form.addRow(t('date') + ":", self.date_input)
        
        # المبلغ
        self.amount_input = QDoubleSpinBox()
        self.amount_input.setMinimum(0.01)
        self.amount_input.setMaximum(999999.99)
        self.amount_input.setDecimals(2)
        form.addRow("المبلغ:", self.amount_input)
        
        # طريقة الدفع
        self.method_combo = QComboBox()
        self.method_combo.addItems(["نقدي", "شيك", "تحويل بنكي", "بطاقة", "أخرى"])
        form.addRow("طريقة الدفع:", self.method_combo)
        
        # المرجع
        self.reference_input = QLineEdit()
        form.addRow("المرجع:", self.reference_input)
        
        # الملاحظات
        self.notes_input = QLineEdit()
        form.addRow("الملاحظات:", self.notes_input)
        
        layout.addLayout(form)
        
        # أزرار
        buttons = QHBoxLayout()
        buttons.addStretch()
        
        btn_save = QPushButton(t('save'))
        btn_save.clicked.connect(self.save_payment)
        buttons.addWidget(btn_save)
        
        btn_cancel = QPushButton(t('cancel'))
        btn_cancel.clicked.connect(self.reject)
        buttons.addWidget(btn_cancel)
        
        layout.addLayout(buttons)
        self.setLayout(layout)
        
    def load_invoices(self):
        """تحميل الفواتير"""
        session = Session()
        try:
            invoices = session.query(Invoice).filter(
                Invoice.status.in_(['unpaid', 'partial'])
            ).all()
            self.invoice_combo.addItem("-- اختر فاتورة --", None)
            for invoice in invoices:
                remaining = invoice.total - invoice.paid_amount
                self.invoice_combo.addItem(
                    f"{invoice.number} - المتبقي: {remaining:.2f}",
                    invoice.id
                )
            
            if self.invoice_id:
                index = self.invoice_combo.findData(self.invoice_id)
                if index >= 0:
                    self.invoice_combo.setCurrentIndex(index)
        finally:
            session.close()
            
    def load_payment_data(self):
        """تحميل بيانات الدفعة"""
        if not self.payment:
            return
            
        self.date_input.setDate(QDate.fromString(
            self.payment.date.strftime("%Y-%m-%d"), "yyyy-MM-dd"
        ))
        self.amount_input.setValue(self.payment.amount)
        
        method_index = self.method_combo.findText(self.payment.method or "")
        if method_index >= 0:
            self.method_combo.setCurrentIndex(method_index)
            
        self.reference_input.setText(self.payment.reference or "")
        self.notes_input.setText(self.payment.notes or "")
        
        if self.payment.invoice_id:
            index = self.invoice_combo.findData(self.payment.invoice_id)
            if index >= 0:
                self.invoice_combo.setCurrentIndex(index)
                
    def save_payment(self):
        """حفظ الدفعة"""
        invoice_id = self.invoice_combo.currentData()
        if not invoice_id:
            QMessageBox.warning(self, "خطأ", "يرجى اختيار فاتورة")
            return
            
        amount = self.amount_input.value()
        if amount <= 0:
            QMessageBox.warning(self, "خطأ", "المبلغ يجب أن يكون أكبر من الصفر")
            return
            
        session = Session()
        try:
            invoice = session.query(Invoice).filter(Invoice.id == invoice_id).first()
            if not invoice:
                QMessageBox.warning(self, "خطأ", "الفاتورة غير موجودة")
                return
                
            # التحقق من عدم تجاوز المبلغ المتبقي
            remaining = invoice.total - invoice.paid_amount
            if amount > remaining:
                reply = QMessageBox.question(
                    self, "تحذير",
                    f"المبلغ ({amount:.2f}) أكبر من المتبقي ({remaining:.2f}). هل تريد المتابعة؟",
                    QMessageBox.Yes | QMessageBox.No
                )
                if reply == QMessageBox.No:
                    return
                    
            if self.payment:
                # تحديث
                old_amount = self.payment.amount
                invoice.paid_amount = invoice.paid_amount - old_amount + amount
                
                self.payment.date = self.date_input.date().toPyDate()
                self.payment.amount = amount
                self.payment.method = self.method_combo.currentText()
                self.payment.reference = self.reference_input.text().strip() or None
                self.payment.notes = self.notes_input.text().strip() or None
            else:
                # إضافة جديد
                payment = Payment(
                    invoice_id=invoice_id,
                    customer_id=invoice.customer_id,
                    date=self.date_input.date().toPyDate(),
                    amount=amount,
                    method=self.method_combo.currentText(),
                    reference=self.reference_input.text().strip() or None,
                    notes=self.notes_input.text().strip() or None
                )
                session.add(payment)
                invoice.paid_amount += amount
                
            # تحديث حالة الفاتورة
            if invoice.paid_amount >= invoice.total:
                invoice.status = 'paid'
            elif invoice.paid_amount > 0:
                invoice.status = 'partial'
            else:
                invoice.status = 'unpaid'
                
            session.commit()
            QMessageBox.information(self, "نجح", "تم حفظ الدفعة بنجاح")
            self.accept()
        except Exception as e:
            session.rollback()
            QMessageBox.critical(self, "خطأ", f"حدث خطأ أثناء الحفظ: {str(e)}")
        finally:
            session.close()

=======
# -*- coding: utf-8 -*-
"""
وحدة إدارة المدفوعات والدفعات
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                             QTableWidgetItem, QPushButton, QLineEdit, QDialog,
                             QFormLayout, QMessageBox, QComboBox, QDoubleSpinBox,
                             QDateEdit, QLabel)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont
from utils.i18n import t
from database.models import Payment, Invoice, Customer, Session
from datetime import datetime


class PaymentsWidget(QWidget):
    """شاشة إدارة المدفوعات"""
    
    def __init__(self, invoice_id=None):
        super().__init__()
        self.invoice_id = invoice_id
        self.init_ui()
        self.load_payments()
        
    def init_ui(self):
        """تهيئة واجهة المستخدم"""
        layout = QVBoxLayout()
        
        # شريط الإجراءات
        toolbar = QHBoxLayout()
        
        btn_add = QPushButton("إضافة دفعة")
        btn_add.clicked.connect(self.add_payment)
        toolbar.addWidget(btn_add)
        
        btn_edit = QPushButton(t('edit'))
        btn_edit.clicked.connect(self.edit_payment)
        toolbar.addWidget(btn_edit)
        
        btn_delete = QPushButton(t('delete'))
        btn_delete.clicked.connect(self.delete_payment)
        toolbar.addWidget(btn_delete)
        
        toolbar.addStretch()
        layout.addLayout(toolbar)
        
        # جدول المدفوعات
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "ID", "رقم الفاتورة", t('date'), "المبلغ", "طريقة الدفع",
            "المرجع", "الملاحظات"
        ])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.doubleClicked.connect(self.edit_payment)
        
        layout.addWidget(self.table)
        self.setLayout(layout)
        
    def load_payments(self):
        """تحميل المدفوعات"""
        session = Session()
        try:
            query = session.query(Payment)
            if self.invoice_id:
                query = query.filter(Payment.invoice_id == self.invoice_id)
            payments = query.order_by(Payment.date.desc()).all()
            
            self.table.setRowCount(len(payments))
            for row, payment in enumerate(payments):
                self.table.setItem(row, 0, QTableWidgetItem(str(payment.id)))
                self.table.setItem(row, 1, QTableWidgetItem(
                    payment.invoice.number if payment.invoice else ""
                ))
                self.table.setItem(row, 2, QTableWidgetItem(
                    payment.date.strftime("%Y-%m-%d")
                ))
                self.table.setItem(row, 3, QTableWidgetItem(f"{payment.amount:.2f}"))
                self.table.setItem(row, 4, QTableWidgetItem(payment.method or ""))
                self.table.setItem(row, 5, QTableWidgetItem(payment.reference or ""))
                self.table.setItem(row, 6, QTableWidgetItem(payment.notes or ""))
        finally:
            session.close()
            
    def add_payment(self):
        """إضافة دفعة جديدة"""
        dialog = PaymentDialog(invoice_id=self.invoice_id)
        if dialog.exec_() == QDialog.Accepted:
            self.load_payments()
            
    def edit_payment(self):
        """تعديل دفعة"""
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "تحذير", "يرجى اختيار دفعة للتعديل")
            return
            
        payment_id = int(self.table.item(selected, 0).text())
        session = Session()
        try:
            payment = session.query(Payment).filter(Payment.id == payment_id).first()
            if payment:
                dialog = PaymentDialog(payment=payment)
                if dialog.exec_() == QDialog.Accepted:
                    self.load_payments()
        finally:
            session.close()
            
    def delete_payment(self):
        """حذف دفعة"""
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "تحذير", "يرجى اختيار دفعة للحذف")
            return
            
        reply = QMessageBox.question(self, "تأكيد", "هل أنت متأكد من حذف هذه الدفعة؟",
                                    QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            payment_id = int(self.table.item(selected, 0).text())
            session = Session()
            try:
                payment = session.query(Payment).filter(Payment.id == payment_id).first()
                if payment:
                    # تحديث رصيد الفاتورة
                    invoice = payment.invoice
                    if invoice:
                        invoice.paid_amount -= payment.amount
                        if invoice.paid_amount <= 0:
                            invoice.status = 'unpaid'
                        elif invoice.paid_amount >= invoice.total:
                            invoice.status = 'paid'
                        else:
                            invoice.status = 'partial'
                    
                    session.delete(payment)
                    session.commit()
                    self.load_payments()
            finally:
                session.close()


class PaymentDialog(QDialog):
    """نافذة إضافة/تعديل دفعة"""
    
    def __init__(self, payment=None, invoice_id=None):
        super().__init__()
        self.payment = payment
        self.invoice_id = invoice_id
        self.setWindowTitle("إضافة دفعة" if not payment else "تعديل دفعة")
        self.setModal(True)
        self.init_ui()
        
        if payment:
            self.load_payment_data()
            
    def init_ui(self):
        """تهيئة واجهة المستخدم"""
        layout = QVBoxLayout()
        
        form = QFormLayout()
        
        # اختيار الفاتورة
        self.invoice_combo = QComboBox()
        self.load_invoices()
        form.addRow("الفاتورة:", self.invoice_combo)
        
        # التاريخ
        self.date_input = QDateEdit()
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setCalendarPopup(True)
        form.addRow(t('date') + ":", self.date_input)
        
        # المبلغ
        self.amount_input = QDoubleSpinBox()
        self.amount_input.setMinimum(0.01)
        self.amount_input.setMaximum(999999.99)
        self.amount_input.setDecimals(2)
        form.addRow("المبلغ:", self.amount_input)
        
        # طريقة الدفع
        self.method_combo = QComboBox()
        self.method_combo.addItems(["نقدي", "شيك", "تحويل بنكي", "بطاقة", "أخرى"])
        form.addRow("طريقة الدفع:", self.method_combo)
        
        # المرجع
        self.reference_input = QLineEdit()
        form.addRow("المرجع:", self.reference_input)
        
        # الملاحظات
        self.notes_input = QLineEdit()
        form.addRow("الملاحظات:", self.notes_input)
        
        layout.addLayout(form)
        
        # أزرار
        buttons = QHBoxLayout()
        buttons.addStretch()
        
        btn_save = QPushButton(t('save'))
        btn_save.clicked.connect(self.save_payment)
        buttons.addWidget(btn_save)
        
        btn_cancel = QPushButton(t('cancel'))
        btn_cancel.clicked.connect(self.reject)
        buttons.addWidget(btn_cancel)
        
        layout.addLayout(buttons)
        self.setLayout(layout)
        
    def load_invoices(self):
        """تحميل الفواتير"""
        session = Session()
        try:
            invoices = session.query(Invoice).filter(
                Invoice.status.in_(['unpaid', 'partial'])
            ).all()
            self.invoice_combo.addItem("-- اختر فاتورة --", None)
            for invoice in invoices:
                remaining = invoice.total - invoice.paid_amount
                self.invoice_combo.addItem(
                    f"{invoice.number} - المتبقي: {remaining:.2f}",
                    invoice.id
                )
            
            if self.invoice_id:
                index = self.invoice_combo.findData(self.invoice_id)
                if index >= 0:
                    self.invoice_combo.setCurrentIndex(index)
        finally:
            session.close()
            
    def load_payment_data(self):
        """تحميل بيانات الدفعة"""
        if not self.payment:
            return
            
        self.date_input.setDate(QDate.fromString(
            self.payment.date.strftime("%Y-%m-%d"), "yyyy-MM-dd"
        ))
        self.amount_input.setValue(self.payment.amount)
        
        method_index = self.method_combo.findText(self.payment.method or "")
        if method_index >= 0:
            self.method_combo.setCurrentIndex(method_index)
            
        self.reference_input.setText(self.payment.reference or "")
        self.notes_input.setText(self.payment.notes or "")
        
        if self.payment.invoice_id:
            index = self.invoice_combo.findData(self.payment.invoice_id)
            if index >= 0:
                self.invoice_combo.setCurrentIndex(index)
                
    def save_payment(self):
        """حفظ الدفعة"""
        invoice_id = self.invoice_combo.currentData()
        if not invoice_id:
            QMessageBox.warning(self, "خطأ", "يرجى اختيار فاتورة")
            return
            
        amount = self.amount_input.value()
        if amount <= 0:
            QMessageBox.warning(self, "خطأ", "المبلغ يجب أن يكون أكبر من الصفر")
            return
            
        session = Session()
        try:
            invoice = session.query(Invoice).filter(Invoice.id == invoice_id).first()
            if not invoice:
                QMessageBox.warning(self, "خطأ", "الفاتورة غير موجودة")
                return
                
            # التحقق من عدم تجاوز المبلغ المتبقي
            remaining = invoice.total - invoice.paid_amount
            if amount > remaining:
                reply = QMessageBox.question(
                    self, "تحذير",
                    f"المبلغ ({amount:.2f}) أكبر من المتبقي ({remaining:.2f}). هل تريد المتابعة؟",
                    QMessageBox.Yes | QMessageBox.No
                )
                if reply == QMessageBox.No:
                    return
                    
            if self.payment:
                # تحديث
                old_amount = self.payment.amount
                invoice.paid_amount = invoice.paid_amount - old_amount + amount
                
                self.payment.date = self.date_input.date().toPyDate()
                self.payment.amount = amount
                self.payment.method = self.method_combo.currentText()
                self.payment.reference = self.reference_input.text().strip() or None
                self.payment.notes = self.notes_input.text().strip() or None
            else:
                # إضافة جديد
                payment = Payment(
                    invoice_id=invoice_id,
                    customer_id=invoice.customer_id,
                    date=self.date_input.date().toPyDate(),
                    amount=amount,
                    method=self.method_combo.currentText(),
                    reference=self.reference_input.text().strip() or None,
                    notes=self.notes_input.text().strip() or None
                )
                session.add(payment)
                invoice.paid_amount += amount
                
            # تحديث حالة الفاتورة
            if invoice.paid_amount >= invoice.total:
                invoice.status = 'paid'
            elif invoice.paid_amount > 0:
                invoice.status = 'partial'
            else:
                invoice.status = 'unpaid'
                
            session.commit()
            QMessageBox.information(self, "نجح", "تم حفظ الدفعة بنجاح")
            self.accept()
        except Exception as e:
            session.rollback()
            QMessageBox.critical(self, "خطأ", f"حدث خطأ أثناء الحفظ: {str(e)}")
        finally:
            session.close()

>>>>>>> 5058b63e17bc5c42e66a4f03a260eae69ba8e457
