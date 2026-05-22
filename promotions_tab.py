from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QDialog, QFormLayout, QLineEdit, QDoubleSpinBox,
                             QDateEdit, QMessageBox, QHeaderView)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont
from database.models import Session
import json


class PromotionsTab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.load_promotions()

    def init_ui(self):
        layout = QVBoxLayout()

        title = QLabel("Promotions Management")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        toolbar = QHBoxLayout()
        btn_add = QPushButton("New Promotion")
        btn_add.clicked.connect(self.add_promotion)
        toolbar.addWidget(btn_add)
        btn_delete = QPushButton("Delete")
        btn_delete.clicked.connect(self.delete_promotion)
        toolbar.addWidget(btn_delete)
        toolbar.addStretch()
        layout.addLayout(toolbar)

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "ID", "Name", "Discount %", "Start", "End", "Min Total", "Active"
        ])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.table)
        self.setLayout(layout)

    def load_promotions(self):
        session = Session()
        try:
            promotions = []
            try:
                from sqlalchemy import inspect
                inspector = inspect(session.bind)
                if 'promotions' in inspector.get_table_names():
                    from sqlalchemy import text
                    rows = session.execute(text("SELECT * FROM promotions ORDER BY id DESC")).fetchall()
                    for row in rows:
                        promotions.append(row._mapping)
            except:
                pass

            self.table.setRowCount(len(promotions))
            for row, p in enumerate(promotions):
                self.table.setItem(row, 0, QTableWidgetItem(str(p['id'])))
                self.table.setItem(row, 1, QTableWidgetItem(p.get('name', '')))
                self.table.setItem(row, 2, QTableWidgetItem(f"{p.get('discount_percent', 0)}%"))
                self.table.setItem(row, 3, QTableWidgetItem(str(p.get('start_date', ''))))
                self.table.setItem(row, 4, QTableWidgetItem(str(p.get('end_date', ''))))
                self.table.setItem(row, 5, QTableWidgetItem(f"{p.get('min_total', 0):.2f}"))
                self.table.setItem(row, 6, QTableWidgetItem("Yes" if p.get('active') else "No"))
        finally:
            session.close()

    def add_promotion(self):
        dialog = PromotionDialog()
        if dialog.exec_() == QDialog.Accepted:
            self.load_promotions()

    def delete_promotion(self):
        row = self.table.currentRow()
        if row < 0:
            return
        promo_id = int(self.table.item(row, 0).text())
        reply = QMessageBox.question(self, "Confirm", "Delete this promotion?",
                                   QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            from sqlalchemy import text
            session = Session()
            try:
                session.execute(text("DELETE FROM promotions WHERE id = ?"), (promo_id,))
                session.commit()
                self.load_promotions()
            except Exception as e:
                session.rollback()
                QMessageBox.critical(self, "Error", str(e))
            finally:
                session.close()


class PromotionDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("New Promotion")
        self.setModal(True)
        self.init_ui()

    def init_ui(self):
        layout = QFormLayout()

        self.name_input = QLineEdit()
        layout.addRow("Name:", self.name_input)

        self.discount_spin = QDoubleSpinBox()
        self.discount_spin.setMaximum(100)
        self.discount_spin.setSuffix(" %")
        layout.addRow("Discount:", self.discount_spin)

        self.start_date = QDateEdit()
        self.start_date.setDate(QDate.currentDate())
        self.start_date.setCalendarPopup(True)
        layout.addRow("Start Date:", self.start_date)

        self.end_date = QDateEdit()
        self.end_date.setDate(QDate.currentDate().addDays(30))
        self.end_date.setCalendarPopup(True)
        layout.addRow("End Date:", self.end_date)

        self.min_total = QDoubleSpinBox()
        self.min_total.setMaximum(99999999)
        self.min_total.setDecimals(2)
        layout.addRow("Min Total:", self.min_total)

        from PyQt5.QtWidgets import QDialogButtonBox
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.save)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

        self.setLayout(layout)

    def save(self):
        if not self.name_input.text().strip():
            QMessageBox.warning(self, "Error", "Name is required")
            return

        session = Session()
        try:
            session.execute(
                "INSERT INTO promotions (name, discount_percent, start_date, end_date, min_total, active) VALUES (?, ?, ?, ?, ?, 1)",
                (self.name_input.text(), self.discount_spin.value(),
                 self.start_date.date().toString("yyyy-MM-dd"),
                 self.end_date.date().toString("yyyy-MM-dd"),
                 self.min_total.value()))
            session.commit()
            self.accept()
        except Exception as e:
            session.rollback()
            QMessageBox.critical(self, "Error", str(e))
        finally:
            session.close()
