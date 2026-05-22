from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QListWidget, QListWidgetItem,
                             QMessageBox, QFileDialog)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from config.settings import BACKUP_DIR, DATABASE_PATH
from backup import BackupManager
from datetime import datetime
from pathlib import Path


class BackupTab(QWidget):
    def __init__(self):
        super().__init__()
        self.backup_manager = BackupManager(str(DATABASE_PATH), str(BACKUP_DIR))
        self.init_ui()
        self.load_backups()

    def init_ui(self):
        layout = QVBoxLayout()

        title = QLabel("Backup & Restore")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        toolbar = QHBoxLayout()
        btn_backup = QPushButton("Create Backup")
        btn_backup.setStyleSheet("background-color: #4CAF50; color: white; padding: 8px;")
        btn_backup.clicked.connect(self.create_backup)
        toolbar.addWidget(btn_backup)

        btn_restore = QPushButton("Restore Selected")
        btn_restore.setStyleSheet("background-color: #FF9800; color: white; padding: 8px;")
        btn_restore.clicked.connect(self.restore_backup)
        toolbar.addWidget(btn_restore)

        btn_delete = QPushButton("Delete Selected")
        btn_delete.setStyleSheet("background-color: #f44336; color: white; padding: 8px;")
        btn_delete.clicked.connect(self.delete_backup)
        toolbar.addWidget(btn_delete)

        btn_export = QPushButton("Export...")
        btn_export.clicked.connect(self.export_backup)
        toolbar.addWidget(btn_export)
        toolbar.addStretch()
        layout.addLayout(toolbar)

        self.backup_list = QListWidget()
        layout.addWidget(self.backup_list)

        self.setLayout(layout)

    def load_backups(self):
        self.backup_list.clear()
        backups = sorted(BACKUP_DIR.glob("*.backup.db"), key=lambda f: f.stat().st_mtime, reverse=True)
        for backup in backups:
            size = backup.stat().st_size
            mtime = datetime.fromtimestamp(backup.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
            item = QListWidgetItem(f"{backup.name} ({size/1024:.1f} KB) - {mtime}")
            item.setData(Qt.UserRole, str(backup))
            self.backup_list.addItem(item)

    def create_backup(self):
        try:
            path = self.backup_manager.create_backup()
            QMessageBox.information(self, "Success", f"Backup created:\n{path}")
            self.load_backups()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def restore_backup(self):
        item = self.backup_list.currentItem()
        if not item:
            QMessageBox.warning(self, "Warning", "Please select a backup")
            return
        path = item.data(Qt.UserRole)
        reply = QMessageBox.question(self, "Confirm",
                                   "Restore will replace current database. Continue?",
                                   QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                self.backup_manager.restore(path)
                QMessageBox.information(self, "Success", "Database restored. Please restart the application.")
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def delete_backup(self):
        item = self.backup_list.currentItem()
        if not item:
            return
        path = item.data(Qt.UserRole)
        reply = QMessageBox.question(self, "Confirm", "Delete this backup?",
                                   QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            Path(path).unlink()
            self.load_backups()

    def export_backup(self):
        item = self.backup_list.currentItem()
        if not item:
            return
        src = item.data(Qt.UserRole)
        dst, _ = QFileDialog.getSaveFileName(self, "Save Backup", "", "Backup Files (*.backup.db)")
        if dst:
            import shutil
            shutil.copy2(src, dst)
            QMessageBox.information(self, "Success", "Backup exported")
