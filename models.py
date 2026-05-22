# -*- coding: utf-8 -*-
"""
نماذج قاعدة البيانات باستخدام SQLAlchemy
"""
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text, Date
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime
from config.settings import DATABASE_PATH

Base = declarative_base()

# إنشاء محرك قاعدة البيانات
engine = create_engine(f'sqlite:///{DATABASE_PATH}', echo=False)
Session = sessionmaker(bind=engine)


# جدول المستخدمين
class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100))
    role = Column(String(50), default='user')  # admin, manager, user, cashier
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    last_login = Column(DateTime)
    
    # علاقات
    sales = relationship("Sale", back_populates="user")
    purchases = relationship("Purchase", back_populates="user")


# جدول العناوين
class Address(Base):
    __tablename__ = 'addresses'
    
    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey('customers.id'))
    type = Column(String(20))  # billing, delivery, site
    name = Column(String(100))  # اسم العنوان
    street = Column(String(200))
    city = Column(String(50))
    postal_code = Column(String(20))
    country = Column(String(50), default='Algeria')
    phone = Column(String(20))
    is_default = Column(Boolean, default=False)
    
    # علاقات
    customer = relationship("Customer", back_populates="addresses")


# جدول العملاء
class Customer(Base):
    __tablename__ = 'customers'
    
    id = Column(Integer, primary_key=True)
    code = Column(String(20), unique=True)
    name = Column(String(100), nullable=False)
    name_ar = Column(String(100))
    name_fr = Column(String(100))
    phone = Column(String(20))
    email = Column(String(100))
    address = Column(Text)  # العنوان الرئيسي (للتوافق مع الإصدار القديم)
    city = Column(String(50))
    country = Column(String(50), default='Algeria')
    tax_id = Column(String(50))  # Numéro d'identification fiscale
    credit_limit = Column(Float, default=0.0)
    balance = Column(Float, default=0.0)
    payment_terms = Column(String(50))  # شروط الدفع (30 jours, à réception, etc.)
    is_active = Column(Boolean, default=True)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    
    # علاقات
    addresses = relationship("Address", back_populates="customer", cascade="all, delete-orphan")
    sales = relationship("Sale", back_populates="customer")
    invoices = relationship("Invoice", back_populates="customer")
    payments = relationship("Payment", back_populates="customer")


# جدول الموردين
class Supplier(Base):
    __tablename__ = 'suppliers'
    
    id = Column(Integer, primary_key=True)
    code = Column(String(20), unique=True)
    name = Column(String(100), nullable=False)
    name_ar = Column(String(100))
    name_fr = Column(String(100))
    phone = Column(String(20))
    email = Column(String(100))
    address = Column(Text)
    city = Column(String(50))
    country = Column(String(50), default='Algeria')
    tax_id = Column(String(50))
    balance = Column(Float, default=0.0)
    is_active = Column(Boolean, default=True)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    
    # علاقات
    purchases = relationship("Purchase", back_populates="supplier")


# جدول الفئات
class Category(Base):
    __tablename__ = 'categories'
    
    id = Column(Integer, primary_key=True)
    code = Column(String(20), unique=True)
    name = Column(String(100), nullable=False)
    name_ar = Column(String(100))
    name_fr = Column(String(100))
    parent_id = Column(Integer, ForeignKey('categories.id'), nullable=True)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    
    # علاقات
    products = relationship("Product", back_populates="category")
    children = relationship("Category")


# جدول المنتجات
class Product(Base):
    __tablename__ = 'products'
    
    id = Column(Integer, primary_key=True)
    code = Column(String(50), unique=True, nullable=False)
    barcode = Column(String(50))
    name = Column(String(100), nullable=False)
    name_ar = Column(String(100))
    name_fr = Column(String(100))
    description = Column(Text)
    category_id = Column(Integer, ForeignKey('categories.id'))
    unit = Column(String(20), default='pcs')  # وحدة القياس
    cost_price = Column(Float, default=0.0)
    selling_price = Column(Float, default=0.0)
    min_stock = Column(Float, default=0.0)  # حد إعادة الطلب
    max_stock = Column(Float, default=0.0)
    tax_rate = Column(Float, default=0.0)  # نسبة الضريبة
    is_active = Column(Boolean, default=True)
    image_path = Column(String(255))
    created_at = Column(DateTime, default=datetime.now)
    
    # علاقات
    category = relationship("Category", back_populates="products")
    inventory_items = relationship("InventoryItem", back_populates="product")
    sale_items = relationship("SaleItem", back_populates="product")
    purchase_items = relationship("PurchaseItem", back_populates="product")


# جدول المخازن
class Warehouse(Base):
    __tablename__ = 'warehouses'
    
    id = Column(Integer, primary_key=True)
    code = Column(String(20), unique=True)
    name = Column(String(100), nullable=False)
    name_ar = Column(String(100))
    name_fr = Column(String(100))
    address = Column(Text)
    is_default = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    
    # علاقات
    inventory_items = relationship("InventoryItem", back_populates="warehouse")


# جدول المخزون
class InventoryItem(Base):
    __tablename__ = 'inventory_items'
    
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    warehouse_id = Column(Integer, ForeignKey('warehouses.id'), nullable=False)
    quantity = Column(Float, default=0.0)
    reserved_quantity = Column(Float, default=0.0)  # كمية محجوزة
    last_updated = Column(DateTime, default=datetime.now)
    
    # علاقات
    product = relationship("Product", back_populates="inventory_items")
    warehouse = relationship("Warehouse", back_populates="inventory_items")


# جدول المبيعات
class Sale(Base):
    __tablename__ = 'sales'
    
    id = Column(Integer, primary_key=True)
    number = Column(String(50), unique=True, nullable=False)
    customer_id = Column(Integer, ForeignKey('customers.id'))
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    date = Column(DateTime, default=datetime.now)
    type = Column(String(20), default='invoice')  # quote, order, invoice
    status = Column(String(20), default='draft')  # draft, confirmed, paid, cancelled
    subtotal = Column(Float, default=0.0)
    tax_amount = Column(Float, default=0.0)
    discount_amount = Column(Float, default=0.0)
    total = Column(Float, default=0.0)
    paid_amount = Column(Float, default=0.0)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    
    # علاقات
    customer = relationship("Customer", back_populates="sales")
    user = relationship("User", back_populates="sales")
    items = relationship("SaleItem", back_populates="sale", cascade="all, delete-orphan")
    invoices = relationship("Invoice", back_populates="sale")


# جدول عناصر المبيعات
class SaleItem(Base):
    __tablename__ = 'sale_items'
    
    id = Column(Integer, primary_key=True)
    sale_id = Column(Integer, ForeignKey('sales.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    quantity = Column(Float, nullable=False)
    unit_price = Column(Float, nullable=False)
    discount = Column(Float, default=0.0)
    tax_rate = Column(Float, default=0.0)
    tax_amount = Column(Float, default=0.0)
    subtotal = Column(Float, nullable=False)
    total = Column(Float, nullable=False)
    
    # علاقات
    sale = relationship("Sale", back_populates="items")
    product = relationship("Product", back_populates="sale_items")


# جدول الفواتير
class Invoice(Base):
    __tablename__ = 'invoices'
    
    id = Column(Integer, primary_key=True)
    number = Column(String(50), unique=True, nullable=False)
    sale_id = Column(Integer, ForeignKey('sales.id'))
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False)
    date = Column(Date, nullable=False)
    due_date = Column(Date)
    billing_address_id = Column(Integer, ForeignKey('addresses.id'))  # عنوان الفاتورة
    delivery_address_id = Column(Integer, ForeignKey('addresses.id'))  # عنوان التسليم
    payment_terms = Column(String(50))  # شروط الدفع
    subtotal = Column(Float, default=0.0)
    tax_amount = Column(Float, default=0.0)
    total = Column(Float, default=0.0)
    paid_amount = Column(Float, default=0.0)
    status = Column(String(20), default='unpaid')  # unpaid, partial, paid, overdue
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    
    # علاقات
    sale = relationship("Sale", back_populates="invoices")
    customer = relationship("Customer", back_populates="invoices")
    billing_address = relationship("Address", foreign_keys=[billing_address_id])
    delivery_address = relationship("Address", foreign_keys=[delivery_address_id])
    payments = relationship("Payment", back_populates="invoice", cascade="all, delete-orphan")


# جدول المدفوعات
class Payment(Base):
    __tablename__ = 'payments'
    
    id = Column(Integer, primary_key=True)
    invoice_id = Column(Integer, ForeignKey('invoices.id'))
    customer_id = Column(Integer, ForeignKey('customers.id'))
    date = Column(Date, nullable=False)
    amount = Column(Float, nullable=False)
    method = Column(String(50))  # cash, check, bank_transfer, card
    reference = Column(String(100))  # رقم الشيك أو المرجع
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    
    # علاقات
    invoice = relationship("Invoice", back_populates="payments")
    customer = relationship("Customer", back_populates="payments")


# جدول المشتريات
class Purchase(Base):
    __tablename__ = 'purchases'
    
    id = Column(Integer, primary_key=True)
    number = Column(String(50), unique=True, nullable=False)
    supplier_id = Column(Integer, ForeignKey('suppliers.id'))
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    date = Column(DateTime, default=datetime.now)
    type = Column(String(20), default='order')  # request, order, receipt
    status = Column(String(20), default='draft')  # draft, confirmed, received, cancelled
    subtotal = Column(Float, default=0.0)
    tax_amount = Column(Float, default=0.0)
    discount_amount = Column(Float, default=0.0)
    total = Column(Float, default=0.0)
    paid_amount = Column(Float, default=0.0)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    
    # علاقات
    supplier = relationship("Supplier", back_populates="purchases")
    user = relationship("User", back_populates="purchases")
    items = relationship("PurchaseItem", back_populates="purchase", cascade="all, delete-orphan")


# جدول عناصر المشتريات
class PurchaseItem(Base):
    __tablename__ = 'purchase_items'
    
    id = Column(Integer, primary_key=True)
    purchase_id = Column(Integer, ForeignKey('purchases.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    quantity = Column(Float, nullable=False)
    unit_price = Column(Float, nullable=False)
    discount = Column(Float, default=0.0)
    tax_rate = Column(Float, default=0.0)
    tax_amount = Column(Float, default=0.0)
    subtotal = Column(Float, nullable=False)
    total = Column(Float, nullable=False)
    
    # علاقات
    purchase = relationship("Purchase", back_populates="items")
    product = relationship("Product", back_populates="purchase_items")


# جدول الحسابات المحاسبية
class Account(Base):
    __tablename__ = 'accounts'
    
    id = Column(Integer, primary_key=True)
    code = Column(String(20), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    name_ar = Column(String(100))
    name_fr = Column(String(100))
    parent_id = Column(Integer, ForeignKey('accounts.id'), nullable=True)
    type = Column(String(50))  # asset, liability, equity, revenue, expense
    balance = Column(Float, default=0.0)
    is_active = Column(Boolean, default=True)
    
    # علاقات
    children = relationship("Account")
    journal_entries = relationship("JournalEntry", back_populates="account")


# جدول القيود المحاسبية
class JournalEntry(Base):
    __tablename__ = 'journal_entries'
    
    id = Column(Integer, primary_key=True)
    number = Column(String(50), unique=True)
    account_id = Column(Integer, ForeignKey('accounts.id'), nullable=False)
    date = Column(Date, nullable=False)
    description = Column(Text)
    debit = Column(Float, default=0.0)
    credit = Column(Float, default=0.0)
    reference_type = Column(String(50))  # sale, purchase, manual
    reference_id = Column(Integer)
    created_by = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime, default=datetime.now)
    
    # علاقات
    account = relationship("Account", back_populates="journal_entries")


# إنشاء الجداول
def init_database():
    """تهيئة قاعدة البيانات وإنشاء الجداول"""
    Base.metadata.create_all(engine)
    # print("تم إنشاء قاعدة البيانات بنجاح!")


if __name__ == "__main__":
    init_database()

