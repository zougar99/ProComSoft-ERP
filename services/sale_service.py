from database.models import Sale, SaleItem, Invoice, InventoryItem, Session
from datetime import datetime
from sqlalchemy import func


class SaleService:
    @staticmethod
    def get_available_products():
        session = Session()
        try:
            from database.models import Product
            products = session.query(Product, func.coalesce(InventoryItem.quantity, 0).label('stock'))\
                .outerjoin(InventoryItem, Product.id == InventoryItem.product_id)\
                .filter(Product.is_active == True).all()
            result = []
            for product, stock in products:
                result.append({
                    'id': product.id,
                    'code': product.code,
                    'name': product.name,
                    'sale_price': product.selling_price,
                    'stock_quantity': stock or 0
                })
            return result
        finally:
            session.close()

    @staticmethod
    def create(sale_data):
        session = Session()
        try:
            from database.models import Product, Warehouse, Customer
            next_number = session.query(func.max(Sale.id)).scalar() or 0
            sale = Sale(
                number=f"INV-{next_number + 1:05d}",
                customer_id=sale_data.get('customer_id'),
                user_id=sale_data.get('created_by', 1),
                date=datetime.now(),
                type='invoice',
                status='confirmed',
                subtotal=sale_data.get('subtotal', 0),
                tax_amount=sale_data.get('tax_amount', 0),
                discount_amount=sale_data.get('discount_amount', 0),
                total=sale_data.get('total_amount', 0),
                paid_amount=sale_data.get('total_amount', 0) if sale_data.get('payment_status') == 'paid' else 0,
                notes=sale_data.get('notes', '')
            )
            session.add(sale)
            session.flush()

            for item in sale_data.get('items', []):
                sale_item = SaleItem(
                    sale_id=sale.id,
                    product_id=item['product_id'],
                    quantity=item['quantity'],
                    unit_price=item['unit_price'],
                    discount=item.get('discount_percent', 0),
                    tax_rate=0,
                    tax_amount=0,
                    subtotal=item['quantity'] * item['unit_price'],
                    total=item['line_total']
                )
                session.add(sale_item)

                warehouse = session.query(Warehouse).filter(Warehouse.is_default == True).first()
                if warehouse:
                    inv = session.query(InventoryItem).filter_by(
                        product_id=item['product_id'],
                        warehouse_id=warehouse.id
                    ).first()
                    if inv:
                        inv.quantity -= item['quantity']
                        inv.last_updated = datetime.now()

            invoice = Invoice(
                number=sale.number,
                sale_id=sale.id,
                customer_id=sale_data.get('customer_id'),
                date=datetime.now().date(),
                subtotal=sale_data.get('subtotal', 0),
                tax_amount=sale_data.get('tax_amount', 0),
                total=sale_data.get('total_amount', 0),
                paid_amount=sale_data.get('total_amount', 0) if sale_data.get('payment_status') == 'paid' else 0,
                status='paid' if sale_data.get('payment_status') == 'paid' else 'unpaid',
                notes=sale_data.get('notes', '')
            )
            session.add(invoice)

            session.commit()
            return {'id': sale.id, 'sale_number': sale.number}
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
