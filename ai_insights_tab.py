from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QGroupBox, QGridLayout, QHeaderView, QFrame)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont
from ai_module import (SalesForecaster, ProductRecommender,
                       StockPredictor, CustomerInsights)


class AIInsightsTab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.refresh_data()

    def init_ui(self):
        layout = QVBoxLayout()

        title = QLabel("AI Insights & Analytics")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        btn_refresh = QPushButton("Refresh Insights")
        btn_refresh.clicked.connect(self.refresh_data)
        layout.addWidget(btn_refresh)

        forecast_group = QGroupBox("Sales Forecast")
        f_layout = QGridLayout()
        self.lbl_prediction = QLabel("-")
        self.lbl_prediction.setFont(QFont("Arial", 14, QFont.Bold))
        self.lbl_trend = QLabel("-")
        self.lbl_confidence = QLabel("-")
        self.lbl_daily_avg = QLabel("-")

        f_layout.addWidget(QLabel("Next 30 days:"), 0, 0)
        f_layout.addWidget(self.lbl_prediction, 0, 1)
        f_layout.addWidget(QLabel("Daily avg:"), 0, 2)
        f_layout.addWidget(self.lbl_daily_avg, 0, 3)
        f_layout.addWidget(QLabel("Trend:"), 1, 0)
        f_layout.addWidget(self.lbl_trend, 1, 1)
        f_layout.addWidget(QLabel("Confidence:"), 1, 2)
        f_layout.addWidget(self.lbl_confidence, 1, 3)
        forecast_group.setLayout(f_layout)
        layout.addWidget(forecast_group)

        stock_group = QGroupBox("Stock Alerts (AI)")
        s_layout = QVBoxLayout()
        self.stock_table = QTableWidget()
        self.stock_table.setColumnCount(6)
        self.stock_table.setHorizontalHeaderLabels([
            "Product", "Code", "Stock", "Daily Sales", "Days Left", "Min Stock"
        ])
        self.stock_table.horizontalHeader().setStretchLastSection(True)
        self.stock_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.stock_table.setEditTriggers(QTableWidget.NoEditTriggers)
        s_layout.addWidget(self.stock_table)
        stock_group.setLayout(s_layout)
        layout.addWidget(stock_group)

        top_group = QGroupBox("Top Selling Products")
        t_layout = QVBoxLayout()
        self.top_table = QTableWidget()
        self.top_table.setColumnCount(4)
        self.top_table.setHorizontalHeaderLabels(["Product", "Code", "Qty Sold", "Revenue"])
        self.top_table.horizontalHeader().setStretchLastSection(True)
        self.top_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.top_table.setEditTriggers(QTableWidget.NoEditTriggers)
        t_layout.addWidget(self.top_table)
        top_group.setLayout(t_layout)
        layout.addWidget(top_group)

        customers_group = QGroupBox("Top Customers")
        c_layout = QVBoxLayout()
        self.customers_table = QTableWidget()
        self.customers_table.setColumnCount(5)
        self.customers_table.setHorizontalHeaderLabels([
            "Customer", "Code", "Orders", "Total Spent", "Avg Order"
        ])
        self.customers_table.horizontalHeader().setStretchLastSection(True)
        self.customers_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.customers_table.setEditTriggers(QTableWidget.NoEditTriggers)
        c_layout.addWidget(self.customers_table)
        customers_group.setLayout(c_layout)
        layout.addWidget(customers_group)

        self.setLayout(layout)

    def refresh_data(self):
        forecast = SalesForecaster.predict_next_period()
        if forecast.get('prediction'):
            self.lbl_prediction.setText(f"{forecast['prediction']:,.2f} DZD")
        else:
            self.lbl_prediction.setText("Insufficient data")
        self.lbl_trend.setText(forecast.get('trend', '-').upper())
        self.lbl_confidence.setText(forecast.get('confidence', '-').title())
        self.lbl_daily_avg.setText(f"{forecast.get('daily_avg', 0):,.2f} DZD")

        self.load_stock_alerts()
        self.load_top_products()
        self.load_top_customers()

    def load_stock_alerts(self):
        alerts = StockPredictor.get_low_stock_alerts()
        self.stock_table.setRowCount(len(alerts))
        for row, a in enumerate(alerts):
            self.stock_table.setItem(row, 0, QTableWidgetItem(a['name']))
            self.stock_table.setItem(row, 1, QTableWidgetItem(a['code']))
            self.stock_table.setItem(row, 2, QTableWidgetItem(str(int(a['current_stock']))))
            self.stock_table.setItem(row, 3, QTableWidgetItem(str(a['daily_sales'])))
            self.stock_table.setItem(row, 4, QTableWidgetItem(str(a['days_remaining'])))
            self.stock_table.setItem(row, 5, QTableWidgetItem(str(int(a['min_stock']))))

    def load_top_products(self):
        products = ProductRecommender.get_top_selling_products()
        self.top_table.setRowCount(len(products))
        for row, p in enumerate(products):
            self.top_table.setItem(row, 0, QTableWidgetItem(p['name']))
            self.top_table.setItem(row, 1, QTableWidgetItem(p['code']))
            self.top_table.setItem(row, 2, QTableWidgetItem(str(p['quantity'])))
            self.top_table.setItem(row, 3, QTableWidgetItem(f"{p['revenue']:,.2f}"))

    def load_top_customers(self):
        customers = CustomerInsights.get_top_customers()
        self.customers_table.setRowCount(len(customers))
        for row, c in enumerate(customers):
            self.customers_table.setItem(row, 0, QTableWidgetItem(c['name']))
            self.customers_table.setItem(row, 1, QTableWidgetItem(c['code']))
            self.customers_table.setItem(row, 2, QTableWidgetItem(str(c['orders'])))
            self.customers_table.setItem(row, 3, QTableWidgetItem(f"{c['total_spent']:,.2f}"))
            self.customers_table.setItem(row, 4, QTableWidgetItem(f"{c['avg_order']:,.2f}"))
