from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QComboBox, QDateEdit, QHeaderView, QGroupBox,
                             QGridLayout, QFrame)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont
from utils.i18n import t
from database.models import Sale, SaleItem, Customer, Product, Session
from sqlalchemy import func
from datetime import datetime, timedelta


class ReportsTab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.load_data()

    def init_ui(self):
        layout = QVBoxLayout()

        title = QLabel(t('reports'))
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        controls = QHBoxLayout()
        controls.addWidget(QLabel("Period:"))
        self.period_combo = QComboBox()
        self.period_combo.addItems(["Today", "This Week", "This Month", "This Year"])
        self.period_combo.currentTextChanged.connect(self.load_data)
        controls.addWidget(self.period_combo)
        controls.addStretch()

        btn_refresh = QPushButton("Refresh")
        btn_refresh.clicked.connect(self.load_data)
        controls.addWidget(btn_refresh)
        layout.addLayout(controls)

        stats_group = QGroupBox("Summary")
        stats_grid = QGridLayout()
        self.lbl_total_sales = QLabel("0.00")
        self.lbl_total_sales.setFont(QFont("Arial", 14, QFont.Bold))
        self.lbl_invoice_count = QLabel("0")
        self.lbl_avg_sale = QLabel("0.00")
        self.lbl_top_product = QLabel("-")

        stats_grid.addWidget(QLabel("Total Sales:"), 0, 0)
        stats_grid.addWidget(self.lbl_total_sales, 0, 1)
        stats_grid.addWidget(QLabel("Invoices:"), 0, 2)
        stats_grid.addWidget(self.lbl_invoice_count, 0, 3)
        stats_grid.addWidget(QLabel("Avg/Sale:"), 1, 0)
        stats_grid.addWidget(self.lbl_avg_sale, 1, 1)
        stats_grid.addWidget(QLabel("Top Product:"), 1, 2)
        stats_grid.addWidget(self.lbl_top_product, 1, 3)
        stats_group.setLayout(stats_grid)
        layout.addWidget(stats_group)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Date", "Number", "Customer", "Items", "Total", "Status"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.table)

        self.setLayout(layout)

    def load_data(self):
        session = Session()
        try:
            period = self.period_combo.currentText()
            now = datetime.now()
            if period == "Today":
                start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            elif period == "This Week":
                start = now - timedelta(days=now.weekday())
                start = start.replace(hour=0, minute=0, second=0, microsecond=0)
            elif period == "This Month":
                start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            else:
                start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)

            sales = session.query(Sale).filter(Sale.date >= start).order_by(Sale.date.desc()).all()

            total = sum(s.total for s in sales)
            count = len(sales)
            avg = total / count if count else 0

            self.lbl_total_sales.setText(f"{total:.2f} DZD")
            self.lbl_invoice_count.setText(str(count))
            self.lbl_avg_sale.setText(f"{avg:.2f} DZD")

            top_product = session.query(
                Product.name, func.sum(SaleItem.quantity).label('qty')
            ).join(SaleItem, Product.id == SaleItem.product_id)\
             .join(Sale, SaleItem.sale_id == Sale.id)\
             .filter(Sale.date >= start)\
             .group_by(Product.id)\
             .order_by(func.sum(SaleItem.quantity).desc()).first()
            self.lbl_top_product.setText(f"{top_product[0]} ({int(top_product[1])})" if top_product else "-")

            self.table.setRowCount(len(sales))
            for row, sale in enumerate(sales):
                self.table.setItem(row, 0, QTableWidgetItem(sale.date.strftime("%Y-%m-%d %H:%M")))
                self.table.setItem(row, 1, QTableWidgetItem(sale.number))
                self.table.setItem(row, 2, QTableWidgetItem(sale.customer.name if sale.customer else "Walk-in"))
                self.table.setItem(row, 3, QTableWidgetItem(str(len(sale.items))))
                self.table.setItem(row, 4, QTableWidgetItem(f"{sale.total:.2f}"))
                self.table.setItem(row, 5, QTableWidgetItem(sale.status))
        finally:
            session.close()
