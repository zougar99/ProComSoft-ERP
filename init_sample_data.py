# -*- coding: utf-8 -*-
"""
أداة تهيئة قاعدة البيانات - إنشاء بيانات تجريبية
"""
from database.models import (init_database, Session, User, Customer, Product, Category,
                            Warehouse, InventoryItem)
from utils.security import create_user
from utils.helpers import generate_code


def create_sample_data():
    """إنشاء بيانات تجريبية"""
    session = Session()
    
    try:
        # إنشاء مستخدم إداري إذا لم يكن موجوداً
        admin = session.query(User).filter(User.username == 'admin').first()
        if not admin:
            create_user('admin', 'admin', 'admin@procomsoft.com', 'Administrator', 'admin')
            print("✓ تم إنشاء المستخدم الإداري")
        
        # إنشاء مخزن افتراضي
        warehouse = session.query(Warehouse).filter(Warehouse.is_default == True).first()
        if not warehouse:
            warehouse = Warehouse(
                code="WH-001",
                name="المخزن الرئيسي",
                name_ar="المخزن الرئيسي",
                name_fr="Entrepôt Principal",
                is_default=True,
                is_active=True
            )
            session.add(warehouse)
            session.flush()
            print("✓ تم إنشاء المخزن الافتراضي")
        
        # إنشاء فئات
        categories_data = [
            {"code": "CAT-001", "name": "إلكترونيات", "name_ar": "إلكترونيات", "name_fr": "Électronique"},
            {"code": "CAT-002", "name": "ملابس", "name_ar": "ملابس", "name_fr": "Vêtements"},
            {"code": "CAT-003", "name": "أغذية", "name_ar": "أغذية", "name_fr": "Alimentation"},
        ]
        
        for cat_data in categories_data:
            category = session.query(Category).filter(Category.code == cat_data['code']).first()
            if not category:
                category = Category(**cat_data, is_active=True)
                session.add(category)
        session.flush()
        print("✓ تم إنشاء الفئات")
        
        # إنشاء عملاء تجريبيين
        customers_data = [
            {
                "code": "CUST-001",
                "name": "شركة التقنية الحديثة",
                "name_ar": "شركة التقنية الحديثة",
                "name_fr": "Société Technologie Moderne",
                "phone": "+213555123456",
                "email": "contact@techmodern.dz",
                "city": "الجزائر"
            },
            {
                "code": "CUST-002",
                "name": "مؤسسة التجارة العامة",
                "name_ar": "مؤسسة التجارة العامة",
                "name_fr": "Établissement Commerce Général",
                "phone": "+213555789012",
                "email": "info@commerce.dz",
                "city": "وهران"
            }
        ]
        
        for cust_data in customers_data:
            customer = session.query(Customer).filter(Customer.code == cust_data['code']).first()
            if not customer:
                customer = Customer(**cust_data, is_active=True)
                session.add(customer)
        session.flush()
        print("✓ تم إنشاء العملاء التجريبيين")
        
        # إنشاء منتجات تجريبية
        products_data = [
            {
                "code": "PROD-001",
                "barcode": "1234567890123",
                "name": "Laptop Dell",
                "name_ar": "حاسوب محمول ديل",
                "name_fr": "Ordinateur Portable Dell",
                "category_id": session.query(Category).filter(Category.code == "CAT-001").first().id,
                "unit": "pcs",
                "cost_price": 50000.0,
                "selling_price": 65000.0,
                "min_stock": 5.0,
                "tax_rate": 19.0
            },
            {
                "code": "PROD-002",
                "barcode": "1234567890124",
                "name": "Smartphone Samsung",
                "name_ar": "هاتف ذكي سامسونج",
                "name_fr": "Smartphone Samsung",
                "category_id": session.query(Category).filter(Category.code == "CAT-001").first().id,
                "unit": "pcs",
                "cost_price": 25000.0,
                "selling_price": 32000.0,
                "min_stock": 10.0,
                "tax_rate": 19.0
            },
            {
                "code": "PROD-003",
                "barcode": "1234567890125",
                "name": "T-Shirt",
                "name_ar": "قميص",
                "name_fr": "T-Shirt",
                "category_id": session.query(Category).filter(Category.code == "CAT-002").first().id,
                "unit": "pcs",
                "cost_price": 800.0,
                "selling_price": 1200.0,
                "min_stock": 50.0,
                "tax_rate": 19.0
            }
        ]
        
        for prod_data in products_data:
            product = session.query(Product).filter(Product.code == prod_data['code']).first()
            if not product:
                product = Product(**prod_data, is_active=True)
                session.add(product)
                session.flush()
                
                # إنشاء سجل مخزون
                inventory = InventoryItem(
                    product_id=product.id,
                    warehouse_id=warehouse.id,
                    quantity=20.0  # كمية ابتدائية
                )
                session.add(inventory)
        print("✓ تم إنشاء المنتجات التجريبية")
        
        session.commit()
        print("\n✓ تم إنشاء جميع البيانات التجريبية بنجاح!")
        
    except Exception as e:
        session.rollback()
        print(f"✗ خطأ في إنشاء البيانات التجريبية: {str(e)}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    print("تهيئة قاعدة البيانات...")
    init_database()
    print("\nإنشاء البيانات التجريبية...")
    create_sample_data()

