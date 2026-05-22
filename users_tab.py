from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QDialog, QFormLayout, QLineEdit, QComboBox,
                             QMessageBox, QHeaderView, QCheckBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from utils.i18n import t
from utils.security import hash_password, create_user
from database.models import User, Session


class UsersTab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.load_users()

    def init_ui(self):
        layout = QVBoxLayout()

        title = QLabel("User Management")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        toolbar = QHBoxLayout()
        btn_add = QPushButton("Add User")
        btn_add.clicked.connect(self.add_user)
        toolbar.addWidget(btn_add)
        btn_edit = QPushButton("Edit")
        btn_edit.clicked.connect(self.edit_user)
        toolbar.addWidget(btn_edit)
        btn_delete = QPushButton("Delete")
        btn_delete.clicked.connect(self.delete_user)
        toolbar.addWidget(btn_delete)
        toolbar.addStretch()
        layout.addLayout(toolbar)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "Username", "Full Name", "Email", "Role", "Active"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.doubleClicked.connect(self.edit_user)
        layout.addWidget(self.table)

        self.setLayout(layout)

    def load_users(self):
        session = Session()
        try:
            users = session.query(User).all()
            self.table.setRowCount(len(users))
            for row, user in enumerate(users):
                self.table.setItem(row, 0, QTableWidgetItem(str(user.id)))
                self.table.setItem(row, 1, QTableWidgetItem(user.username))
                self.table.setItem(row, 2, QTableWidgetItem(user.full_name or ""))
                self.table.setItem(row, 3, QTableWidgetItem(user.email or ""))
                self.table.setItem(row, 4, QTableWidgetItem(user.role))
                self.table.setItem(row, 5, QTableWidgetItem("Yes" if user.is_active else "No"))
        finally:
            session.close()

    def add_user(self):
        dialog = UserDialog()
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            try:
                create_user(
                    username=data['username'],
                    password=data['password'],
                    email=data.get('email'),
                    full_name=data.get('full_name'),
                    role=data.get('role', 'user')
                )
                self.load_users()
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def edit_user(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Warning", "Please select a user")
            return
        user_id = int(self.table.item(row, 0).text())
        session = Session()
        try:
            user = session.query(User).filter(User.id == user_id).first()
            if user:
                dialog = UserDialog(user)
                if dialog.exec_() == QDialog.Accepted:
                    data = dialog.get_data()
                    user.username = data['username']
                    user.full_name = data.get('full_name')
                    user.email = data.get('email')
                    user.role = data.get('role', 'user')
                    if data.get('password'):
                        user.password_hash = hash_password(data['password'])
                    session.commit()
                    self.load_users()
        except Exception as e:
            session.rollback()
            QMessageBox.critical(self, "Error", str(e))
        finally:
            session.close()

    def delete_user(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Warning", "Please select a user")
            return
        reply = QMessageBox.question(self, "Confirm", "Delete this user?",
                                   QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            user_id = int(self.table.item(row, 0).text())
            session = Session()
            try:
                user = session.query(User).filter(User.id == user_id).first()
                if user:
                    session.delete(user)
                    session.commit()
                    self.load_users()
            except Exception as e:
                session.rollback()
                QMessageBox.critical(self, "Error", str(e))
            finally:
                session.close()


class UserDialog(QDialog):
    def __init__(self, user=None):
        super().__init__()
        self.user = user
        self.setWindowTitle("Add User" if not user else "Edit User")
        self.setModal(True)
        self.init_ui()
        if user:
            self.load_data(user)

    def init_ui(self):
        layout = QFormLayout()

        self.username_input = QLineEdit()
        layout.addRow("Username:", self.username_input)

        self.fullname_input = QLineEdit()
        layout.addRow("Full Name:", self.fullname_input)

        self.email_input = QLineEdit()
        layout.addRow("Email:", self.email_input)

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Leave empty to keep current")
        layout.addRow("Password:", self.password_input)

        self.role_combo = QComboBox()
        self.role_combo.addItems(["admin", "manager", "user", "cashier"])
        layout.addRow("Role:", self.role_combo)

        from PyQt5.QtWidgets import QDialogButtonBox
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.validate)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

        self.setLayout(layout)

    def load_data(self, user):
        self.username_input.setText(user.username)
        self.fullname_input.setText(user.full_name or "")
        self.email_input.setText(user.email or "")
        idx = self.role_combo.findText(user.role)
        if idx >= 0:
            self.role_combo.setCurrentIndex(idx)

    def validate(self):
        if not self.username_input.text().strip():
            QMessageBox.warning(self, "Error", "Username is required")
            return
        if not self.user and not self.password_input.text():
            QMessageBox.warning(self, "Error", "Password is required for new users")
            return
        self.accept()

    def get_data(self):
        return {
            'username': self.username_input.text().strip(),
            'full_name': self.fullname_input.text().strip(),
            'email': self.email_input.text().strip(),
            'password': self.password_input.text(),
            'role': self.role_combo.currentText(),
        }
