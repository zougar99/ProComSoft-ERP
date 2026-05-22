<<<<<<< HEAD
"""Minimal placeholder tabs"""
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel

class SalesTab(QWidget):
    def __init__(self, db):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("🛒 Sales & POS\n\nFeatures:\n- Shopping cart\n- Discounts\n- Payment methods\n- Receipt printing"))
        self.setLayout(layout)

class ProductsTab(QWidget):
    def __init__(self, db):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("📦 Products Management\n\nFeatures:\n- Add/Edit products\n- Stock tracking\n- SKU/Barcode management"))
        self.setLayout(layout)

class CustomersTab(QWidget):
    def __init__(self, db):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("👥 Customers & Suppliers\n\nFeatures:\n- Customer database\n- Contact info\n- Purchase history"))
        self.setLayout(layout)

class InvoicesTab(QWidget):
    def __init__(self, db):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("🧾 Invoices & Orders\n\nFeatures:\n- Invoice generation\n- PDF printing\n- Payment tracking"))
        self.setLayout(layout)

class ReportsTab(QWidget):
    def __init__(self, db):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("📊 Reports & Analytics\n\nFeatures:\n- Daily sales\n- Top products\n- Profit analysis"))
        self.setLayout(layout)

class UsersTab(QWidget):
    def __init__(self, db, user_manager):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("🔐 User Management (Admin)\n\nFeatures:\n- User accounts\n- Role management\n- Permissions"))
        self.setLayout(layout)

class BackupTab(QWidget):
    def __init__(self, db):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("💾 Backup & Restore (Admin)\n\nFeatures:\n- Daily backups\n- Restore functionality\n- Backup history"))
        self.setLayout(layout)
=======
"""Minimal placeholder tabs"""
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel

class SalesTab(QWidget):
    def __init__(self, db):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("🛒 Sales & POS\n\nFeatures:\n- Shopping cart\n- Discounts\n- Payment methods\n- Receipt printing"))
        self.setLayout(layout)

class ProductsTab(QWidget):
    def __init__(self, db):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("📦 Products Management\n\nFeatures:\n- Add/Edit products\n- Stock tracking\n- SKU/Barcode management"))
        self.setLayout(layout)

class CustomersTab(QWidget):
    def __init__(self, db):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("👥 Customers & Suppliers\n\nFeatures:\n- Customer database\n- Contact info\n- Purchase history"))
        self.setLayout(layout)

class InvoicesTab(QWidget):
    def __init__(self, db):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("🧾 Invoices & Orders\n\nFeatures:\n- Invoice generation\n- PDF printing\n- Payment tracking"))
        self.setLayout(layout)

class ReportsTab(QWidget):
    def __init__(self, db):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("📊 Reports & Analytics\n\nFeatures:\n- Daily sales\n- Top products\n- Profit analysis"))
        self.setLayout(layout)

class UsersTab(QWidget):
    def __init__(self, db, user_manager):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("🔐 User Management (Admin)\n\nFeatures:\n- User accounts\n- Role management\n- Permissions"))
        self.setLayout(layout)

class BackupTab(QWidget):
    def __init__(self, db):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("💾 Backup & Restore (Admin)\n\nFeatures:\n- Daily backups\n- Restore functionality\n- Backup history"))
        self.setLayout(layout)
>>>>>>> 5058b63e17bc5c42e66a4f03a260eae69ba8e457
