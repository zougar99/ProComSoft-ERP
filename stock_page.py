"""
Stock Page - صفحة المخزون
Standalone page for stock/inventory management
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QMessageBox, QAbstractItemView,
    QSizePolicy, QSpacerItem, QGroupBox
)
import sqlite3


class StockPage(QWidget):
    """Standalone Stock Management Page"""
    
    action_requested = Signal(str)
    
    def __init__(self, repository=None):
        super().__init__()
        self.repository = repository
        self.db_path = "laser_app.db"
        self._setup_ui()
        self._load_stock()
    
    def _setup_ui(self):
        """Setup Stock UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)
        
        # Header
        header_layout = QHBoxLayout()
        
        home_btn = QPushButton("🏠 Home")
        home_btn.setObjectName("Secondary")
        home_btn.setFixedHeight(40)
        home_btn.setFixedWidth(100)
        home_btn.clicked.connect(lambda: self.action_requested.emit("dashboard"))
        header_layout.addWidget(home_btn)
        
        header_layout.addItem(QSpacerItem(20, 10, QSizePolicy.Expanding, QSizePolicy.Minimum))
        
        title = QLabel("📦 Stock Management — إدارة المخزون")
        title.setObjectName("PageTitle")
        title.setStyleSheet("font-size: 22px; font-weight: 600; color: #1F2937; padding: 0;")
        header_layout.addWidget(title)
        
        header_layout.addItem(QSpacerItem(20, 10, QSizePolicy.Expanding, QSizePolicy.Minimum))
        
        layout.addLayout(header_layout)
        
        # Info
        info = QLabel("Track inventory, stock levels, and movements — تتبع المخزون والمستويات والحركات")
        info.setObjectName("InfoLabel")
        info.setWordWrap(True)
        layout.addWidget(info)
        
        # Actions
        actions_layout = QHBoxLayout()
        
        add_btn = QPushButton("➕ Add Stock Entry — إضافة حركة مخزون")
        add_btn.setObjectName("Primary")
        add_btn.clicked.connect(self._add_stock_entry)
        actions_layout.addWidget(add_btn)
        
        calculate_btn = QPushButton("🔄 Calculate Stock — حساب المخزون")
        calculate_btn.setObjectName("Secondary")
        calculate_btn.clicked.connect(self._calculate_stock)
        actions_layout.addWidget(calculate_btn)
        
        refresh_btn = QPushButton("🔄 Refresh — تحديث")
        refresh_btn.setObjectName("Secondary")
        refresh_btn.clicked.connect(self._load_stock)
        actions_layout.addWidget(refresh_btn)
        
        actions_layout.addStretch()
        layout.addLayout(actions_layout)
        
        # Stock Table
        self.stock_table = QTableWidget()
        self.stock_table.setColumnCount(8)
        self.stock_table.setHorizontalHeaderLabels([
            "Article", "Initial Stock", "Entries", "Exits", "Final Stock", "Unit Price", "Total Value", "Actions"
        ])
        self.stock_table.horizontalHeader().setStretchLastSection(True)
        self.stock_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        layout.addWidget(self.stock_table)
        
        # Summary
        summary_group = QGroupBox("Stock Summary — ملخص المخزون")
        summary_layout = QHBoxLayout()
        
        self.stock_total_label = QLabel("Total Items: 0")
        self.stock_value_label = QLabel("Total Value: 0 MAD")
        self.stock_alerts_label = QLabel("Low Stock Alerts: 0")
        
        summary_layout.addWidget(self.stock_total_label)
        summary_layout.addWidget(self.stock_value_label)
        summary_layout.addWidget(self.stock_alerts_label)
        summary_layout.addStretch()
        
        summary_group.setLayout(summary_layout)
        layout.addWidget(summary_group)
        
        layout.addStretch()
    
    def _load_stock(self):
        """Load stock from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS enterprise_articles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    article_code TEXT UNIQUE,
                    article_name TEXT NOT NULL,
                    category TEXT,
                    unit TEXT DEFAULT 'pcs',
                    price REAL DEFAULT 0,
                    stock_quantity REAL DEFAULT 0,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS enterprise_stock_movements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    article_id INTEGER,
                    article_name TEXT,
                    movement_type TEXT,
                    quantity REAL,
                    movement_date TEXT,
                    notes TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cursor.execute("""
                SELECT a.id, a.article_name, a.stock_quantity, a.price,
                       COALESCE(SUM(CASE WHEN sm.movement_type = 'entry' THEN sm.quantity ELSE 0 END), 0) as entries,
                       COALESCE(SUM(CASE WHEN sm.movement_type = 'exit' THEN sm.quantity ELSE 0 END), 0) as exits,
                       a.stock_quantity as initial
                FROM enterprise_articles a
                LEFT JOIN enterprise_stock_movements sm ON a.id = sm.article_id
                GROUP BY a.id, a.article_name, a.stock_quantity, a.price
                ORDER BY a.id DESC
            """)
            
            stock_data = cursor.fetchall()
            conn.close()
            
            self.stock_table.setRowCount(len(stock_data))
            for row, data in enumerate(stock_data):
                article_name = data[1] or ""
                initial = data[5] or 0
                entries = data[4] or 0
                exits = data[5] or 0
                final = initial + entries - exits
                price = data[3] or 0
                total_value = final * price
                
                self.stock_table.setItem(row, 0, QTableWidgetItem(article_name))
                self.stock_table.setItem(row, 1, QTableWidgetItem(f"{initial:.2f}"))
                self.stock_table.setItem(row, 2, QTableWidgetItem(f"{entries:.2f}"))
                self.stock_table.setItem(row, 3, QTableWidgetItem(f"{exits:.2f}"))
                self.stock_table.setItem(row, 4, QTableWidgetItem(f"{final:.2f}"))
                self.stock_table.setItem(row, 5, QTableWidgetItem(f"{price:.2f}"))
                self.stock_table.setItem(row, 6, QTableWidgetItem(f"{total_value:.2f}"))
                
                # Actions button
                actions_btn = QPushButton("View")
                actions_btn.clicked.connect(lambda checked, a_id=data[0]: self._view_stock_details(a_id))
                self.stock_table.setCellWidget(row, 7, actions_btn)
            
            # Update summary
            total_items = len(stock_data)
            total_value = sum((data[5] or 0) * (data[3] or 0) for data in stock_data)
            low_stock = sum(1 for data in stock_data if (data[5] or 0) < 10)
            
            self.stock_total_label.setText(f"Total Items: {total_items}")
            self.stock_value_label.setText(f"Total Value: {total_value:.2f} MAD")
            self.stock_alerts_label.setText(f"Low Stock Alerts: {low_stock}")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error loading stock: {str(e)}")
    
    def _add_stock_entry(self):
        """Add stock entry"""
        QMessageBox.information(self, "Add Stock Entry", "Stock entry feature will be implemented soon.")
    
    def _calculate_stock(self):
        """Calculate stock"""
        self._load_stock()
        QMessageBox.information(self, "Stock Calculated", "Stock has been recalculated.")
    
    def _view_stock_details(self, article_id: int):
        """View stock details"""
        QMessageBox.information(self, "Stock Details", f"Stock details for article #{article_id} will be shown here.")
