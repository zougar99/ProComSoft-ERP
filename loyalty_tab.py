from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QDialog, QFormLayout, QSpinBox, QComboBox,
                             QMessageBox, QHeaderView)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from database.models import Session, Customer
from datetime import datetime


class LoyaltyTab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.load_customers()

    def init_ui(self):
        layout = QVBoxLayout()

        title = QLabel("Loyalty Points Management")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "ID", "Customer", "Code", "Points", "Action"
        ])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.table)

        self.setLayout(layout)

    def load_customers(self):
        session = Session()
        try:
            try:
                from sqlalchemy import inspect, text
                inspector = inspect(session.bind)
                if 'customers' in inspector.get_table_names() and \
                   'loyalty_points' in [c['name'] for c in inspector.get_columns('customers')]:
                    customers = session.execute(
                        text("SELECT id, code, name, loyalty_points FROM customers ORDER BY name")
                    ).fetchall()
                else:
                    customers = []
            except:
                customers = []

            self.table.setRowCount(len(customers))
            for row, c in enumerate(customers):
                self.table.setItem(row, 0, QTableWidgetItem(str(c[0])))
                self.table.setItem(row, 1, QTableWidgetItem(c[2] or ""))
                self.table.setItem(row, 2, QTableWidgetItem(c[1] or ""))
                self.table.setItem(row, 3, QTableWidgetItem(str(c[3] or 0)))
                btn_add = QPushButton("Add Points")
                btn_add.clicked.connect(lambda checked, cid=c[0]: self.add_points(cid))
                self.table.setCellWidget(row, 4, btn_add)
        finally:
            session.close()

    def add_points(self, customer_id):
        dialog = PointsDialog(customer_id)
        if dialog.exec_() == QDialog.Accepted:
            self.load_customers()


class PointsDialog(QDialog):
    def __init__(self, customer_id):
        super().__init__()
        self.customer_id = customer_id
        self.setWindowTitle("Add Loyalty Points")
        self.setModal(True)
        self.init_ui()

    def init_ui(self):
        layout = QFormLayout()
        self.points_spin = QSpinBox()
        self.points_spin.setMaximum(999999)
        self.points_spin.setValue(10)
        layout.addRow("Points:", self.points_spin)

        from PyQt5.QtWidgets import QDialogButtonBox
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.save)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)
        self.setLayout(layout)

    def save(self):
        from sqlalchemy import text
        session = Session()
        try:
            session.execute(
                text("UPDATE customers SET loyalty_points = COALESCE(loyalty_points, 0) + :pts WHERE id = :cid"),
                {'pts': self.points_spin.value(), 'cid': self.customer_id}
            )
            session.execute(
                text("INSERT INTO loyalty_log (customer_id, points, type, description, created_at) "
                     "VALUES (:cid, :pts, 'earned', 'Points added', :now)"),
                {'cid': self.customer_id, 'pts': self.points_spin.value(),
                 'now': datetime.now()}
            )
            session.commit()
            self.accept()
        except Exception as e:
            session.rollback()
            QMessageBox.critical(self, "Error", str(e))
        finally:
            session.close()
