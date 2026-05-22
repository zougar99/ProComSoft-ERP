from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                             QTableWidgetItem, QPushButton, QLineEdit, QDialog,
                             QFormLayout, QMessageBox, QComboBox, QDoubleSpinBox,
                             QDateEdit, QLabel, QHeaderView, QSpinBox)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont
from utils.i18n import t
from utils.helpers import generate_code
from database.models import (Purchase, PurchaseItem, Supplier, Product,
                             InventoryItem, Warehouse, Session)
from datetime import datetime
from sqlalchemy import func


class PurchasesWidget(QWidget):
    def __init__(self, current_user=None):
        super().__init__()
        self.current_user = current_user
        self.init_ui()
        self.load_purchases()

    def init_ui(self):
        layout = QVBoxLayout()

        toolbar = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search...")
        self.search_input.textChanged.connect(self.filter_purchases)
        toolbar.addWidget(self.search_input)

        btn_new = QPushButton("New Purchase")
        btn_new.clicked.connect(self.new_purchase)
        toolbar.addWidget(btn_new)

        btn_view = QPushButton("View")
        btn_view.clicked.connect(self.view_purchase)
        toolbar.addWidget(btn_view)

        layout.addLayout(toolbar)

        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "ID", "Number", "Date", "Supplier", "Status", "Subtotal", "Total", "Paid"
        ])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.doubleClicked.connect(self.view_purchase)
        layout.addWidget(self.table)

        self.setLayout(layout)

    def load_purchases(self):
        session = Session()
        try:
            purchases = session.query(Purchase).order_by(Purchase.date.desc()).limit(100).all()
            self.table.setRowCount(len(purchases))
            for row, p in enumerate(purchases):
                self.table.setItem(row, 0, QTableWidgetItem(str(p.id)))
                self.table.setItem(row, 1, QTableWidgetItem(p.number))
                self.table.setItem(row, 2, QTableWidgetItem(p.date.strftime("%Y-%m-%d")))
                self.table.setItem(row, 3, QTableWidgetItem(
                    p.supplier.name if p.supplier else ""))
                self.table.setItem(row, 4, QTableWidgetItem(p.status))
                self.table.setItem(row, 5, QTableWidgetItem(f"{p.subtotal:.2f}"))
                self.table.setItem(row, 6, QTableWidgetItem(f"{p.total:.2f}"))
                self.table.setItem(row, 7, QTableWidgetItem(f"{p.paid_amount:.2f}"))
        finally:
            session.close()

    def filter_purchases(self, text):
        for row in range(self.table.rowCount()):
            match = False
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                if item and text.lower() in item.text().lower():
                    match = True
                    break
            self.table.setRowHidden(row, not match)

    def new_purchase(self):
        dialog = PurchaseDialog(current_user=self.current_user)
        if dialog.exec_() == QDialog.Accepted:
            self.load_purchases()

    def view_purchase(self):
        row = self.table.currentRow()
        if row < 0:
            return
        purchase_id = int(self.table.item(row, 0).text())
        dialog = PurchaseDialog(purchase_id=purchase_id, current_user=self.current_user)
        dialog.exec_()


class PurchaseDialog(QDialog):
    def __init__(self, purchase_id=None, current_user=None):
        super().__init__()
        self.purchase_id = purchase_id
        self.current_user = current_user
        self.items = []
        self.setWindowTitle("Edit Purchase" if purchase_id else "New Purchase")
        self.setModal(True)
        self.resize(700, 500)
        self.init_ui()
        if purchase_id:
            self.load_purchase()

    def init_ui(self):
        layout = QVBoxLayout()
        form = QFormLayout()

        self.supplier_combo = QComboBox()
        self.supplier_combo.addItem("Select Supplier", None)
        session = Session()
        try:
            suppliers = session.query(Supplier).filter(Supplier.is_active == True).all()
            for s in suppliers:
                self.supplier_combo.addItem(f"{s.code} - {s.name}", s.id)
        finally:
            session.close()
        form.addRow("Supplier:", self.supplier_combo)

        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        form.addRow("Date:", self.date_edit)

        self.status_combo = QComboBox()
        self.status_combo.addItems(["draft", "confirmed", "received", "cancelled"])
        form.addRow("Status:", self.status_combo)

        layout.addLayout(form)

        items_header = QHBoxLayout()
        items_header.addWidget(QLabel("<b>Items</b>"))
        btn_add_item = QPushButton("Add Product")
        btn_add_item.clicked.connect(self.add_item)
        items_header.addWidget(btn_add_item)
        layout.addLayout(items_header)

        self.items_table = QTableWidget()
        self.items_table.setColumnCount(6)
        self.items_table.setHorizontalHeaderLabels(["Product", "Qty", "Unit Price", "Discount", "Subtotal", ""])
        self.items_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.items_table)

        totals_layout = QHBoxLayout()
        totals_layout.addStretch()
        self.total_label = QLabel("Total: 0.00")
        self.total_label.setFont(QFont("Arial", 12, QFont.Bold))
        totals_layout.addWidget(self.total_label)
        layout.addLayout(totals_layout)

        btn_layout = QHBoxLayout()
        btn_save = QPushButton("Save")
        btn_save.clicked.connect(self.save)
        btn_layout.addWidget(btn_save)
        btn_cancel = QPushButton("Cancel")
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancel)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def add_item(self):
        dialog = PurchaseItemDialog()
        if dialog.exec_() == QDialog.Accepted:
            item = dialog.get_item()
            self.items.append(item)
            self.update_items_table()

    def remove_item(self, row):
        if 0 <= row < len(self.items):
            self.items.pop(row)
            self.update_items_table()

    def update_items_table(self):
        self.items_table.setRowCount(len(self.items))
        total = 0
        for row, item in enumerate(self.items):
            self.items_table.setItem(row, 0, QTableWidgetItem(item['product_name']))
            self.items_table.setItem(row, 1, QTableWidgetItem(str(item['quantity'])))
            self.items_table.setItem(row, 2, QTableWidgetItem(f"{item['unit_price']:.2f}"))
            self.items_table.setItem(row, 3, QTableWidgetItem(f"{item['discount']:.2f}"))
            self.items_table.setItem(row, 4, QTableWidgetItem(f"{item['subtotal']:.2f}"))
            btn_remove = QPushButton("X")
            btn_remove.clicked.connect(lambda checked, r=row: self.remove_item(r))
            self.items_table.setCellWidget(row, 5, btn_remove)
            total += item['subtotal']
        self.total_label.setText(f"Total: {total:.2f}")

    def load_purchase(self):
        session = Session()
        try:
            purchase = session.query(Purchase).filter(Purchase.id == self.purchase_id).first()
            if not purchase:
                return
            idx = self.supplier_combo.findData(purchase.supplier_id)
            if idx >= 0:
                self.supplier_combo.setCurrentIndex(idx)
            self.date_edit.setDate(QDate(
                purchase.date.year, purchase.date.month, purchase.date.day))
            idx = self.status_combo.findText(purchase.status)
            if idx >= 0:
                self.status_combo.setCurrentIndex(idx)

            for item in purchase.items:
                self.items.append({
                    'product_id': item.product_id,
                    'product_name': item.product.name if item.product else "Unknown",
                    'quantity': item.quantity,
                    'unit_price': item.unit_price,
                    'discount': item.discount,
                    'subtotal': item.total,
                })
            self.update_items_table()
        finally:
            session.close()

    def save(self):
        if self.supplier_combo.currentData() is None:
            QMessageBox.warning(self, "Error", "Please select a supplier")
            return
        if not self.items:
            QMessageBox.warning(self, "Error", "Please add at least one item")
            return

        session = Session()
        try:
            if self.purchase_id:
                purchase = session.query(Purchase).filter(Purchase.id == self.purchase_id).first()
                purchase.items = []
            else:
                next_num = (session.query(func.max(Purchase.id)).scalar() or 0) + 1
                purchase = Purchase(
                    number=f"PUR-{next_num:05d}",
                    user_id=self.current_user.get('id', 1) if self.current_user else 1,
                )
                session.add(purchase)

            purchase.supplier_id = self.supplier_combo.currentData()
            purchase.date = datetime(
                self.date_edit.date().year(), self.date_edit.date().month(),
                self.date_edit.date().day())
            purchase.status = self.status_combo.currentText()
            purchase.type = 'order'

            subtotal = sum(i['subtotal'] for i in self.items)
            purchase.subtotal = subtotal
            purchase.tax_amount = 0
            purchase.discount_amount = 0
            purchase.total = subtotal
            purchase.paid_amount = 0

            session.flush()

            for item_data in self.items:
                item = PurchaseItem(
                    purchase_id=purchase.id,
                    product_id=item_data['product_id'],
                    quantity=item_data['quantity'],
                    unit_price=item_data['unit_price'],
                    discount=item_data['discount'],
                    tax_rate=0,
                    tax_amount=0,
                    subtotal=item_data['subtotal'],
                    total=item_data['subtotal'],
                )
                session.add(item)

                if purchase.status == 'received':
                    warehouse = session.query(Warehouse).filter(Warehouse.is_default == True).first()
                    if warehouse:
                        inv = session.query(InventoryItem).filter_by(
                            product_id=item_data['product_id'],
                            warehouse_id=warehouse.id
                        ).first()
                        if inv:
                            inv.quantity += item_data['quantity']
                        else:
                            inv = InventoryItem(
                                product_id=item_data['product_id'],
                                warehouse_id=warehouse.id,
                                quantity=item_data['quantity']
                            )
                            session.add(inv)

            session.commit()
            QMessageBox.information(self, "Success", f"Purchase saved: {purchase.number}")
            self.accept()
        except Exception as e:
            session.rollback()
            QMessageBox.critical(self, "Error", str(e))
        finally:
            session.close()


class PurchaseItemDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Add Product")
        self.setModal(True)
        self.init_ui()

    def init_ui(self):
        layout = QFormLayout()

        self.product_combo = QComboBox()
        self.product_combo.addItem("Select Product", None)
        session = Session()
        try:
            products = session.query(Product).filter(Product.is_active == True).all()
            for p in products:
                self.product_combo.addItem(f"{p.code} - {p.name}", p.id)
        finally:
            session.close()
        layout.addRow("Product:", self.product_combo)

        self.qty_spin = QDoubleSpinBox()
        self.qty_spin.setMinimum(0.01)
        self.qty_spin.setMaximum(999999)
        self.qty_spin.setValue(1)
        layout.addRow("Quantity:", self.qty_spin)

        self.price_spin = QDoubleSpinBox()
        self.price_spin.setMinimum(0)
        self.price_spin.setMaximum(99999999)
        self.price_spin.setDecimals(2)
        layout.addRow("Unit Price:", self.price_spin)

        self.discount_spin = QDoubleSpinBox()
        self.discount_spin.setMinimum(0)
        self.discount_spin.setMaximum(100)
        self.discount_spin.setDecimals(2)
        self.discount_spin.setSuffix(" %")
        layout.addRow("Discount:", self.discount_spin)

        from PyQt5.QtWidgets import QDialogButtonBox
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.validate)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

        self.setLayout(layout)

    def validate(self):
        if self.product_combo.currentData() is None:
            QMessageBox.warning(self, "Error", "Please select a product")
            return
        self.accept()

    def get_item(self):
        qty = self.qty_spin.value()
        price = self.price_spin.value()
        disc = self.discount_spin.value()
        subtotal = (qty * price) * (1 - disc / 100)

        session = Session()
        try:
            product = session.query(Product).filter(
                Product.id == self.product_combo.currentData()).first()
            name = product.name if product else "Unknown"
        finally:
            session.close()

        return {
            'product_id': self.product_combo.currentData(),
            'product_name': name,
            'quantity': qty,
            'unit_price': price,
            'discount': disc,
            'subtotal': subtotal,
        }
