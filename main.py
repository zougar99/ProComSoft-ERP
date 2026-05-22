#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main entry point for ProComSoft POS application
"""
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from PyQt5.QtWidgets import QApplication
from database.models import init_database
from ui.login_window import LoginWindow


def setup_extra_tables():
    """Create additional tables (promotions, loyalty_log, stock_movements)"""
    from sqlalchemy import text, inspect
    from database.models import engine, Session
    inspector = inspect(engine)
    existing = inspector.get_table_names()

    statements = []
    if 'promotions' not in existing:
        statements.append("""
            CREATE TABLE IF NOT EXISTS promotions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                discount_percent REAL DEFAULT 0,
                start_date TEXT, end_date TEXT,
                min_total REAL DEFAULT 0,
                active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
    if 'promotion_products' not in existing:
        statements.append("""
            CREATE TABLE IF NOT EXISTS promotion_products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                promotion_id INTEGER, product_id INTEGER,
                FOREIGN KEY (promotion_id) REFERENCES promotions(id),
                FOREIGN KEY (product_id) REFERENCES products(id)
            )
        """)
    if 'coupons' not in existing:
        statements.append("""
            CREATE TABLE IF NOT EXISTS coupons (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT UNIQUE, discount_percent REAL DEFAULT 0,
                max_uses INTEGER DEFAULT 1, used_count INTEGER DEFAULT 0,
                expires_at TEXT, is_active INTEGER DEFAULT 1
            )
        """)
    if 'loyalty_log' not in existing:
        statements.append("""
            CREATE TABLE IF NOT EXISTS loyalty_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER, points INTEGER, type TEXT,
                description TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (customer_id) REFERENCES customers(id)
            )
        """)
    if 'stock_movements' not in existing:
        statements.append("""
            CREATE TABLE IF NOT EXISTS stock_movements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER, warehouse_id INTEGER,
                quantity REAL, type TEXT, reference TEXT, notes TEXT,
                created_by INTEGER, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (product_id) REFERENCES products(id),
                FOREIGN KEY (warehouse_id) REFERENCES warehouses(id)
            )
        """)
    if 'pricing_tariffs' not in existing:
        statements.append("""
            CREATE TABLE IF NOT EXISTS pricing_tariffs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT, customer_id INTEGER,
                start_date TEXT, end_date TEXT, is_active INTEGER DEFAULT 1
            )
        """)
    if 'pricing_tariff_items' not in existing:
        statements.append("""
            CREATE TABLE IF NOT EXISTS pricing_tariff_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tariff_id INTEGER, product_id INTEGER,
                price REAL, discount_percent REAL DEFAULT 0
            )
        """)

    with engine.connect() as conn:
        for stmt in statements:
            conn.execute(text(stmt))
        conn.commit()


def seed_sample_data():
    """Add sample data if DB is empty"""
    from database.models import Session, User, Customer
    session = Session()
    try:
        if session.query(User).count() == 0:
            from init_sample_data import create_sample_data
            create_sample_data()
    finally:
        session.close()


def main():
    init_database()
    setup_extra_tables()
    seed_sample_data()

    app = QApplication(sys.argv)
    app.setApplicationName("ProComSoft ERP")

    login = LoginWindow()
    login.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
