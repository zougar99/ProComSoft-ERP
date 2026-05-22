from database.models import Product, Session


class ProductService:
    @staticmethod
    def list(search=None):
        session = Session()
        try:
            query = session.query(Product).filter(Product.is_active == True)
            if search:
                query = query.filter(
                    Product.name.ilike(f'%{search}%') |
                    Product.code.ilike(f'%{search}%') |
                    Product.barcode.ilike(f'%{search}%')
                )
            products = query.all()
            return [{
                'id': p.id,
                'code': p.code,
                'name': p.name,
                'sale_price': p.selling_price,
                'stock_quantity': 0
            } for p in products]
        finally:
            session.close()
