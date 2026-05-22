"""
Login dialog
"""
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                            QPushButton, QMessageBox, QCheckBox)
from PyQt5.QtCore import Qt, pyqtSignal
from pos_app.modules.user_manager import UserManager

class LoginDialog(QDialog):
    """Login dialog for user authentication"""
    
    login_successful = pyqtSignal(object)  # Emits user object
    
    def __init__(self, user_manager):
        super().__init__()
        self.user_manager = user_manager
        self.user = None
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI"""
        self.setWindowTitle("AGAMART - Connexion")
        self.setGeometry(100, 100, 400, 250)
        self.setModal(True)
        self.setStyleSheet("QDialog { background-color: #f5f5f5; }")
        
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("AGAMART - Connexion")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title)
        
        # Username
        layout.addWidget(QLabel("Username:"))
        self.username_input = QLineEdit()
        layout.addWidget(self.username_input)
        
        # Password
        layout.addWidget(QLabel("Password:"))
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)
        
        # Remember me
        self.remember_checkbox = QCheckBox("Remember me")
        layout.addWidget(self.remember_checkbox)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        login_btn = QPushButton("Login")
        login_btn.clicked.connect(self.login)
        button_layout.addWidget(login_btn)
        
        exit_btn = QPushButton("Exit")
        exit_btn.clicked.connect(self.reject)
        button_layout.addWidget(exit_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
        
        # Focus on username
        self.username_input.setFocus()
    
    def login(self):
        """Handle login"""
        username = self.username_input.text().strip()
        password = self.password_input.text()
        
        if not username or not password:
            QMessageBox.warning(self, "Error", "Please enter username and password")
            return
        
        user, msg = self.user_manager.authenticate(username, password)
        
        if user:
            # user can be a dict (from DB) or an object; handle both safely
            if isinstance(user, dict):
                is_active = user.get('is_active', 1)
            else:
                is_active = getattr(user, 'is_active', 1)

            if not bool(is_active):
                QMessageBox.warning(self, "Error", "This account is inactive")
                return

            self.user = user
            self.login_successful.emit(user)
            self.accept()
        else:
            QMessageBox.warning(self, "Login Failed", msg)
            self.password_input.clear()
            self.username_input.setFocus()
