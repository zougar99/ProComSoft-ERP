"""
Point of Sale (POS) Page - LaserFlow
Professional POS system for laser workshop sales
Inspired by LOGEC commercial management software
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QTableWidget, QTableWidgetItem, QDoubleSpinBox,
    QComboBox, QGroupBox, QFormLayout, QSizePolicy, QSpacerItem,
    QFrame, QMessageBox
)
from PySide6.QtGui import QFont
from datetime import datetime
from typing import List, Dict


class PointOfSalePage(QWidget):
    """Point of Sale - Professional POS interface"""
    
    action_requested = Signal(str)
    
    def __init__(self, repository=None):
        super().__init__()
        self.repository = repository
        self.cart_items: List[Dict] = []
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup POS UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        
        # Header
        header = self._create_header()
        layout.addWidget(header)
        
        # Main content area
        content_layout = QHBoxLayout()
        content_layout.setSpacing(16)
        
        # Left panel - Product selection
        left_panel = self._create_product_panel()
        content_layout.addWidget(left_panel, 2)
        
        # Right panel - Cart and payment
        right_panel = self._create_cart_panel()
        content_layout.addWidget(right_panel, 3)
        
        layout.addLayout(content_layout)
    
    def _create_header(self) -> QWidget:
        """Create POS header"""
        header = QFrame()
        header.setObjectName("Panel")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(16, 12, 16, 12)
        
        home_btn = QPushButton("🏠 Home")
        home_btn.setObjectName("HomeButton")
        home_btn.setFixedHeight(36)
        home_btn.clicked.connect(lambda: self.action_requested.emit("dashboard"))
        header_layout.addWidget(home_btn)
        
        header_layout.addItem(QSpacerItem(20, 10, QSizePolicy.Expanding, QSizePolicy.Minimum))
        
        title = QLabel("Point of Sale — نقطة البيع")
        title.setObjectName("PageTitle")
        header_layout.addWidget(title)
        
        header_layout.addItem(QSpacerItem(20, 10, QSizePolicy.Expanding, QSizePolicy.Minimum))
        
        # Transaction info
        info_layout = QHBoxLayout()
        info_layout.setSpacing(12)
        
        date_label = QLabel(f"Date: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        info_layout.addWidget(date_label)
        
        self.transaction_num = QLabel("Transaction #: --")
        info_layout.addWidget(self.transaction_num)
        
        header_layout.addLayout(info_layout)
        
        return header
    
    def _create_product_panel(self) -> QWidget:
        """Create product selection panel"""
        panel = QGroupBox("Product Selection — اختيار المنتج")
        panel_layout = QVBoxLayout(panel)
        
        # Search section
        search_group = QGroupBox("Search — البحث")
        search_layout = QFormLayout()
        
        self.barcode_input = QLineEdit()
        self.barcode_input.setPlaceholderText("Scan barcode or enter code")
        search_layout.addRow("Barcode/Code:", self.barcode_input)
        
        self.product_name_input = QLineEdit()
        self.product_name_input.setPlaceholderText("Product name")
        search_layout.addRow("Product Name:", self.product_name_input)
        
        self.category_combo = QComboBox()
        self.category_combo.addItems(["All", "Laser Cutting", "Engraving", "Materials", "Services"])
        search_layout.addRow("Category:", self.category_combo)
        
        search_btn = QPushButton("🔍 Search")
        search_btn.setObjectName("Primary")
        search_layout.addRow("", search_btn)
        
        search_group.setLayout(search_layout)
        panel_layout.addWidget(search_group)
        
        # Products grid
        products_group = QGroupBox("Available Products — المنتجات المتاحة")
        products_layout = QVBoxLayout()
        
        self.products_table = QTableWidget()
        self.products_table.setColumnCount(5)
        self.products_table.setHorizontalHeaderLabels([
            "Code", "Product Name", "Category", "Price (MAD)", "Action"
        ])
        self.products_table.horizontalHeader().setStretchLastSection(True)
        self.products_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.products_table.setAlternatingRowColors(True)
        products_layout.addWidget(self.products_table)
        
        products_group.setLayout(products_layout)
        panel_layout.addWidget(products_group)
        
        # Load sample products
        self._load_sample_products()
        
        return panel
    
    def _create_cart_panel(self) -> QWidget:
        """Create cart and payment panel"""
        panel = QGroupBox("Shopping Cart & Payment — سلة التسوق والدفع")
        panel_layout = QVBoxLayout(panel)
        
        # Cart table
        cart_group = QGroupBox("Cart Items — عناصر السلة")
        cart_layout = QVBoxLayout()
        
        self.cart_table = QTableWidget()
        self.cart_table.setColumnCount(6)
        self.cart_table.setHorizontalHeaderLabels([
            "Qty", "Product", "Unit Price", "Discount %", "Total", "Action"
        ])
        self.cart_table.horizontalHeader().setStretchLastSection(True)
        self.cart_table.setAlternatingRowColors(True)
        cart_layout.addWidget(self.cart_table)
        
        cart_group.setLayout(cart_layout)
        panel_layout.addWidget(cart_group)
        
        # Payment section
        payment_group = QGroupBox("Payment — الدفع")
        payment_layout = QFormLayout()
        
        # Quick payment buttons
        quick_payment_layout = QHBoxLayout()
        for amount in [5, 10, 20, 50, 100, 200]:
            btn = QPushButton(f"{amount} Dhs")
            btn.setFixedSize(60, 40)
            btn.clicked.connect(lambda checked, a=amount: self._quick_payment(a))
            quick_payment_layout.addWidget(btn)
        payment_layout.addRow("Quick Amounts:", quick_payment_layout)
        
        # Discount
        self.discount_input = QDoubleSpinBox()
        self.discount_input.setRange(0, 100)
        self.discount_input.setSuffix(" %")
        self.discount_input.setValue(0)
        self.discount_input.valueChanged.connect(self._update_totals)
        payment_layout.addRow("Discount on Total:", self.discount_input)
        
        # Payment method
        self.payment_method = QComboBox()
        self.payment_method.addItems(["Cash", "Card", "Bank Transfer", "Check"])
        payment_layout.addRow("Payment Method:", self.payment_method)
        
        # Totals
        totals_group = QGroupBox("Totals — الإجماليات")
        totals_layout = QVBoxLayout()
        
        self.subtotal_label = QLabel("Subtotal: 0.00 MAD")
        self.subtotal_label.setObjectName("MetricValue")
        totals_layout.addWidget(self.subtotal_label)
        
        self.discount_label = QLabel("Discount: 0.00 MAD")
        totals_layout.addWidget(self.discount_label)
        
        self.total_label = QLabel("Total: 0.00 MAD")
        self.total_label.setObjectName("MetricValue")
        font = QFont()
        # Fix: Ensure font has valid point size before setting it
        # If pointSize is -1, it means font uses pixel size, so we need to set a valid point size first
        if font.pointSize() <= 0 or font.pointSizeF() <= 0:
            # If font uses pixel size, convert it to point size first
            if font.pixelSize() > 0:
                # Convert pixel size to point size (approximate: 1pt ≈ 1.33px at 96 DPI)
                point_size = max(9, int(font.pixelSize() / 1.33))
                font.setPointSize(point_size)
            else:
                # Set a default point size (12pt is standard)
                font.setPointSize(12)
        # Now set the desired point size (16pt)
        font.setPointSize(16)
        font.setBold(True)
        # Double-check pointSize after setBold (sometimes setBold can affect pointSize)
        if font.pointSize() <= 0 or font.pointSizeF() <= 0:
            if font.pixelSize() > 0:
                point_size = max(9, int(font.pixelSize() / 1.33))
                font.setPointSize(point_size)
            else:
                font.setPointSize(12)
        self.total_label.setFont(font)
        self.total_label.setStyleSheet("color: #e74c3c; background-color: #ffffff; padding: 12px; border: 2px solid #e74c3c; border-radius: 6px;")
        totals_layout.addWidget(self.total_label)
        
        self.received_input = QDoubleSpinBox()
        self.received_input.setRange(0, 999999)
        self.received_input.setSuffix(" MAD")
        self.received_input.setPrefix("Received: ")
        self.received_input.valueChanged.connect(self._calculate_change)
        totals_layout.addWidget(self.received_input)
        
        self.change_label = QLabel("Change: 0.00 MAD")
        self.change_label.setObjectName("MetricValue")
        totals_layout.addWidget(self.change_label)
        
        totals_group.setLayout(totals_layout)
        payment_layout.addRow("", totals_group)
        
        # Action buttons
        actions_layout = QHBoxLayout()
        
        validate_btn = QPushButton("✅ Validate Transaction")
        validate_btn.setObjectName("Primary")
        validate_btn.setFixedHeight(50)
        validate_btn.clicked.connect(self._validate_transaction)
        actions_layout.addWidget(validate_btn)
        
        cancel_btn = QPushButton("❌ Cancel")
        cancel_btn.setObjectName("Danger")
        cancel_btn.setFixedHeight(50)
        cancel_btn.clicked.connect(self._cancel_transaction)
        actions_layout.addWidget(cancel_btn)
        
        payment_layout.addRow("", actions_layout)
        
        payment_group.setLayout(payment_layout)
        panel_layout.addWidget(payment_group)
        
        return panel
    
    def _load_sample_products(self):
        """Load sample products"""
        products = [
            {"code": "LAS001", "name": "Laser Cutting - Small", "category": "Laser Cutting", "price": 50.00},
            {"code": "LAS002", "name": "Laser Cutting - Medium", "category": "Laser Cutting", "price": 100.00},
            {"code": "LAS003", "name": "Laser Cutting - Large", "category": "Laser Cutting", "price": 200.00},
            {"code": "ENG001", "name": "Engraving - Text", "category": "Engraving", "price": 30.00},
            {"code": "ENG002", "name": "Engraving - Logo", "category": "Engraving", "price": 80.00},
            {"code": "MAT001", "name": "Acrylic Sheet", "category": "Materials", "price": 25.00},
            {"code": "MAT002", "name": "Wood Panel", "category": "Materials", "price": 40.00},
            {"code": "SVC001", "name": "Design Service", "category": "Services", "price": 150.00},
        ]
        
        self.products_table.setRowCount(len(products))
        
        for row, product in enumerate(products):
            self.products_table.setItem(row, 0, QTableWidgetItem(product["code"]))
            self.products_table.setItem(row, 1, QTableWidgetItem(product["name"]))
            self.products_table.setItem(row, 2, QTableWidgetItem(product["category"]))
            self.products_table.setItem(row, 3, QTableWidgetItem(f"{product['price']:.2f}"))
            
            add_btn = QPushButton("➕ Add")
            add_btn.clicked.connect(lambda checked, p=product: self._add_to_cart(p))
            self.products_table.setCellWidget(row, 4, add_btn)
    
    def _add_to_cart(self, product: Dict):
        """Add product to cart"""
        # Check if already in cart
        for item in self.cart_items:
            if item["code"] == product["code"]:
                item["quantity"] += 1
                self._update_cart_display()
                self._update_totals()
                return
        
        # Add new item
        self.cart_items.append({
            "code": product["code"],
            "name": product["name"],
            "unit_price": product["price"],
            "quantity": 1,
            "discount": 0
        })
        
        self._update_cart_display()
        self._update_totals()
    
    def _update_cart_display(self):
        """Update cart table display"""
        self.cart_table.setRowCount(len(self.cart_items))
        
        for row, item in enumerate(self.cart_items):
            # Quantity
            qty_item = QTableWidgetItem(str(item["quantity"]))
            self.cart_table.setItem(row, 0, qty_item)
            
            # Product name
            self.cart_table.setItem(row, 1, QTableWidgetItem(item["name"]))
            
            # Unit price
            self.cart_table.setItem(row, 2, QTableWidgetItem(f"{item['unit_price']:.2f}"))
            
            # Discount
            discount_item = QTableWidgetItem(f"{item['discount']:.1f}")
            self.cart_table.setItem(row, 3, discount_item)
            
            # Total
            total = item["quantity"] * item["unit_price"] * (1 - item["discount"] / 100)
            self.cart_table.setItem(row, 4, QTableWidgetItem(f"{total:.2f}"))
            
            # Remove button
            remove_btn = QPushButton("❌")
            remove_btn.clicked.connect(lambda checked, r=row: self._remove_from_cart(r))
            self.cart_table.setCellWidget(row, 5, remove_btn)
    
    def _remove_from_cart(self, row: int):
        """Remove item from cart"""
        if 0 <= row < len(self.cart_items):
            self.cart_items.pop(row)
            self._update_cart_display()
            self._update_totals()
    
    def _update_totals(self):
        """Update total calculations"""
        subtotal = sum(
            item["quantity"] * item["unit_price"] * (1 - item["discount"] / 100)
            for item in self.cart_items
        )
        
        discount_percent = self.discount_input.value()
        discount_amount = subtotal * (discount_percent / 100)
        total = subtotal - discount_amount
        
        self.subtotal_label.setText(f"Subtotal: {subtotal:.2f} MAD")
        self.discount_label.setText(f"Discount: {discount_amount:.2f} MAD")
        self.total_label.setText(f"Total: {total:.2f} MAD")
        
        self._calculate_change()
    
    def _calculate_change(self):
        """Calculate change"""
        total_text = self.total_label.text()
        total = float(total_text.split(":")[1].split("MAD")[0].strip())
        received = self.received_input.value()
        change = received - total
        
        if change >= 0:
            self.change_label.setText(f"Change: {change:.2f} MAD")
            self.change_label.setStyleSheet("color: #27ae60; font-weight: bold;")
        else:
            self.change_label.setText(f"Remaining: {abs(change):.2f} MAD")
            self.change_label.setStyleSheet("color: #e74c3c; font-weight: bold;")
    
    def _quick_payment(self, amount: float):
        """Quick payment amount"""
        total_text = self.total_label.text()
        total = float(total_text.split(":")[1].split("MAD")[0].strip())
        self.received_input.setValue(total + amount)
    
    def _validate_transaction(self):
        """Validate and complete transaction"""
        if not self.cart_items:
            QMessageBox.warning(self, "Empty Cart", "Please add items to cart first.")
            return
        
        total_text = self.total_label.text()
        total = float(total_text.split(":")[1].split("MAD")[0].strip())
        received = self.received_input.value()
        
        if received < total:
            QMessageBox.warning(self, "Insufficient Payment", f"Received amount ({received:.2f} MAD) is less than total ({total:.2f} MAD).")
            return
        
        # Transaction successful
        QMessageBox.information(
            self,
            "Transaction Complete",
            f"Transaction completed successfully!\n\n"
            f"Total: {total:.2f} MAD\n"
            f"Received: {received:.2f} MAD\n"
            f"Change: {received - total:.2f} MAD"
        )
        
        # Clear cart
        self._cancel_transaction()
    
    def _cancel_transaction(self):
        """Cancel current transaction"""
        self.cart_items.clear()
        self.discount_input.setValue(0)
        self.received_input.setValue(0)
        self._update_cart_display()
        self._update_totals()
