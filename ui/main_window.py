# -*- coding: utf-8 -*-
"""
النافذة الرئيسية للتطبيق
"""
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QStackedWidget, QMenuBar,
                             QMenu, QStatusBar, QToolBar, QAction, QMessageBox,
                             QFrame, QGridLayout)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QFont
from utils.i18n import t, get_language
from database.models import Sale, Customer, Product, InventoryItem, Session
from sqlalchemy import func
from datetime import datetime, timedelta


class MainWindow(QMainWindow):
    """النافذة الرئيسية"""
    
    def __init__(self, current_user=None):
        super().__init__()
        self.current_user = current_user
        self.setWindowTitle(t('app_name'))
        self.setGeometry(100, 100, 1200, 800)

        if get_language() == 'ar':
            self.setLayoutDirection(Qt.RightToLeft)
        
        self.page_widgets = {}
        self.init_ui()
        self.setup_menu()
        self.setup_toolbar()
        self.setup_statusbar()
        
    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.content_stack = QStackedWidget()
        layout.addWidget(self.content_stack)
        
        self.dashboard_widget = self.create_dashboard()
        self.content_stack.addWidget(self.dashboard_widget)
        self.page_widgets['dashboard'] = self.dashboard_widget
        
    def create_dashboard(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(20)

        title = QLabel(t('dashboard'))
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        stats_layout = QHBoxLayout()
        stats_data = self._load_stats()
        
        cards = [
            (t('sales'), f"{stats_data['today_sales']:.2f}", "DZD", "#4CAF50"),
            (t('customers'), str(stats_data['total_customers']), "", "#2196F3"),
            (t('products'), str(stats_data['total_products']), "", "#FF9800"),
            (t('inventory'), str(stats_data['low_stock']), t('products'), "#f44336"),
        ]
        
        for title_text, value, unit, color in cards:
            card = self.create_stat_card(title_text, value, unit, color)
            stats_layout.addWidget(card)
        
        layout.addLayout(stats_layout)

        quick_layout = QHBoxLayout()
        quick_layout.setSpacing(15)
        
        buttons = [
            (t('sales') + " - " + t('add'), self.show_sales, "#4CAF50"),
            (t('customers') + " - " + t('add'), self.show_customers, "#2196F3"),
            (t('products') + " - " + t('add'), self.show_products, "#FF9800"),
            ("Point of Sale", self.show_pos, "#9C27B0"),
            (t('purchases'), self.show_purchases, "#607D8B"),
        ]
        
        for btn_text, callback, color in buttons:
            btn = QPushButton(btn_text)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    color: white;
                    border: none;
                    padding: 15px 25px;
                    border-radius: 8px;
                    font-size: 14px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    opacity: 0.8;
                }}
            """)
            btn.clicked.connect(callback)
            quick_layout.addWidget(btn)
        
        layout.addLayout(quick_layout)
        layout.addStretch()
        return widget
    
    def _load_stats(self):
        session = Session()
        try:
            today = datetime.now().date()
            today_sales = session.query(func.coalesce(func.sum(Sale.total), 0))\
                .filter(func.date(Sale.date) == today).scalar()
            total_customers = session.query(func.count(Customer.id)).scalar()
            total_products = session.query(func.count(Product.id)).scalar()
            low_stock = session.query(func.count(InventoryItem.id))\
                .join(Product).filter(InventoryItem.quantity <= Product.min_stock).scalar()
            return {
                'today_sales': float(today_sales or 0),
                'total_customers': total_customers or 0,
                'total_products': total_products or 0,
                'low_stock': low_stock or 0,
            }
        finally:
            session.close()
    
    def create_stat_card(self, title, value, unit, color):
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {color};
                border-radius: 10px;
                padding: 20px;
                color: white;
            }}
        """)
        layout = QVBoxLayout(card)
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 11))
        title_label.setStyleSheet("color: rgba(255,255,255,0.8);")
        layout.addWidget(title_label)
        value_label = QLabel(f"{value} {unit}")
        value_label.setFont(QFont("Arial", 20, QFont.Bold))
        value_label.setStyleSheet("color: white;")
        layout.addWidget(value_label)
        return card
    
    def setup_menu(self):
        menubar = self.menuBar()
        
        file_menu = menubar.addMenu('&' + t('settings'))
        logout_action = QAction(t('logout'), self)
        logout_action.triggered.connect(self.logout)
        file_menu.addAction(logout_action)
        
        data_menu = menubar.addMenu(t('customers'))
        customers_action = QAction(t('customers'), self)
        customers_action.triggered.connect(self.show_customers)
        data_menu.addAction(customers_action)
        products_action = QAction(t('products'), self)
        products_action.triggered.connect(self.show_products)
        data_menu.addAction(products_action)
        
        operations_menu = menubar.addMenu(t('sales'))
        sales_action = QAction(t('sales'), self)
        sales_action.triggered.connect(self.show_sales)
        operations_menu.addAction(sales_action)
        purchases_action = QAction(t('purchases'), self)
        purchases_action.triggered.connect(self.show_purchases)
        operations_menu.addAction(purchases_action)
        pos_action = QAction("Point of Sale", self)
        pos_action.triggered.connect(self.show_pos)
        operations_menu.addAction(pos_action)
        
        reports_menu = menubar.addMenu(t('reports'))
        sales_report_action = QAction(t('sales'), self)
        sales_report_action.triggered.connect(self.show_reports)
        reports_menu.addAction(sales_report_action)
        ai_action = QAction("AI Insights", self)
        ai_action.triggered.connect(self.show_ai_insights)
        reports_menu.addAction(ai_action)
        
        tools_menu = menubar.addMenu("Tools")
        users_action = QAction("Users", self)
        users_action.triggered.connect(self.show_users)
        tools_menu.addAction(users_action)
        promotions_action = QAction("Promotions", self)
        promotions_action.triggered.connect(self.show_promotions)
        tools_menu.addAction(promotions_action)
        loyalty_action = QAction("Loyalty Points", self)
        loyalty_action.triggered.connect(self.show_loyalty)
        tools_menu.addAction(loyalty_action)
        backup_action = QAction("Backup & Restore", self)
        backup_action.triggered.connect(self.show_backup)
        tools_menu.addAction(backup_action)
        settings_action = QAction("Settings", self)
        settings_action.triggered.connect(self.show_settings)
        tools_menu.addAction(settings_action)
        
    def setup_toolbar(self):
        toolbar = QToolBar()
        toolbar.setIconSize(QSize(24, 24))
        toolbar.setStyleSheet("""
            QToolBar { background-color: #f5f5f5; border-bottom: 1px solid #ddd; padding: 5px; }
            QToolButton { padding: 8px 15px; margin: 2px; border-radius: 4px; }
            QToolButton:hover { background-color: #e0e0e0; }
        """)
        self.addToolBar(toolbar)
        
        dashboard_action = QAction("Dashboard", self)
        dashboard_action.triggered.connect(self.show_dashboard)
        toolbar.addAction(dashboard_action)
        
        sales_action = QAction(t('sales'), self)
        sales_action.triggered.connect(self.show_sales)
        toolbar.addAction(sales_action)
        
        customers_action = QAction(t('customers'), self)
        customers_action.triggered.connect(self.show_customers)
        toolbar.addAction(customers_action)
        
        products_action = QAction(t('products'), self)
        products_action.triggered.connect(self.show_products)
        toolbar.addAction(products_action)
        
        pos_action = QAction("POS", self)
        pos_action.triggered.connect(self.show_pos)
        toolbar.addAction(pos_action)
        
    def setup_statusbar(self):
        user_text = f"{self.current_user.get('username', '')}" if self.current_user else t('unknown')
        self.statusBar().showMessage(f"{t('user')}: {user_text}")
    
    def _show_page(self, page_name, widget_class, *args, **kwargs):
        if page_name in self.page_widgets:
            widget = self.page_widgets[page_name]
        else:
            widget = widget_class(*args, **kwargs)
            self.content_stack.addWidget(widget)
            self.page_widgets[page_name] = widget
        self.content_stack.setCurrentWidget(widget)
    
    def show_dashboard(self):
        self._load_stats_dynamic()
        self.content_stack.setCurrentWidget(self.dashboard_widget)
    
    def _load_stats_dynamic(self):
        stats = self._load_stats()
        layout = self.dashboard_widget.layout()
        stats_layout = layout.itemAt(1).layout()
        for i in range(4):
            card = stats_layout.itemAt(i).widget()
            if card:
                vlayout = card.layout()
                value_label = vlayout.itemAt(1).widget()
                if value_label:
                    values = [f"{stats['today_sales']:.2f} DZD", str(stats['total_customers']), str(stats['total_products']), str(stats['low_stock'])]
                    value_label.setText(values[i])
    
    def show_sales(self):
        from modules.sales.invoices import SalesWidget
        self._show_page('sales', SalesWidget, current_user=self.current_user)
    
    def show_customers(self):
        from modules.crm.customers import CustomersWidget
        self._show_page('customers', CustomersWidget)
    
    def show_products(self):
        from modules.inventory.products import ProductsWidget
        self._show_page('products', ProductsWidget)
    
    def show_pos(self):
        from pos_window import POSWindow
        self._show_page('pos', POSWindow, user=self.current_user)
    
    def show_purchases(self):
        from purchases_tab import PurchasesWidget
        self._show_page('purchases', PurchasesWidget, current_user=self.current_user)
    
    def show_reports(self):
        from reports_tab import ReportsTab
        self._show_page('reports', ReportsTab)
    
    def show_users(self):
        from users_tab import UsersTab
        self._show_page('users', UsersTab)
    
    def show_backup(self):
        from backup_tab import BackupTab
        self._show_page('backup', BackupTab)
    
    def show_promotions(self):
        from promotions_tab import PromotionsTab
        self._show_page('promotions', PromotionsTab)
    
    def show_loyalty(self):
        from loyalty_tab import LoyaltyTab
        self._show_page('loyalty', LoyaltyTab)
    
    def show_settings(self):
        from settings_tab import SettingsTab
        self._show_page('settings', SettingsTab)

    def show_ai_insights(self):
        from ai_insights_tab import AIInsightsTab
        self._show_page('ai_insights', AIInsightsTab)

    def logout(self):
        reply = QMessageBox.question(self, t('logout'),
                                   "Are you sure you want to logout?",
                                   QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.close()
            from ui.login_window import LoginWindow
            self.login_window = LoginWindow()
            self.login_window.show()

