from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QFormLayout, QLineEdit, QComboBox,
                             QDoubleSpinBox, QMessageBox, QGroupBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from config.settings import (APP_NAME, APP_LANGUAGE, DEFAULT_CURRENCY,
                             DEFAULT_TAX_RATE, THEME, APP_VERSION)
from utils.i18n import set_language, t


class SettingsTab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        title = QLabel("Settings")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        general_group = QGroupBox("General")
        general_layout = QFormLayout()

        self.app_name_input = QLineEdit(APP_NAME)
        general_layout.addRow("App Name:", self.app_name_input)

        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["ar", "fr", "en"])
        self.lang_combo.setCurrentText(APP_LANGUAGE)
        general_layout.addRow("Language:", self.lang_combo)

        self.currency_input = QLineEdit(DEFAULT_CURRENCY)
        general_layout.addRow("Currency:", self.currency_input)

        self.tax_spin = QDoubleSpinBox()
        self.tax_spin.setMaximum(100)
        self.tax_spin.setValue(DEFAULT_TAX_RATE)
        self.tax_spin.setSuffix(" %")
        general_layout.addRow("Default Tax:", self.tax_spin)

        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["light", "dark"])
        self.theme_combo.setCurrentText(THEME)
        general_layout.addRow("Theme:", self.theme_combo)

        general_group.setLayout(general_layout)
        layout.addWidget(general_group)

        info_group = QGroupBox("About")
        info_layout = QFormLayout()
        info_layout.addRow("Version:", QLabel(APP_VERSION))
        info_layout.addRow("Database:", QLabel("SQLite"))
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)

        btn_save = QPushButton("Save Settings")
        btn_save.clicked.connect(self.save_settings)
        layout.addWidget(btn_save)

        layout.addStretch()
        self.setLayout(layout)

    def save_settings(self):
        set_language(self.lang_combo.currentText())
        QMessageBox.information(self, "Success",
            "Settings saved. Some changes require restart.")
