from datetime import datetime
from database.models import Sale, Purchase, Invoice, Session
from sqlalchemy import func


class NumberingService:
    @staticmethod
    def generate_number(doc_type, session_model, prefix):
        session = Session()
        try:
            year = datetime.now().year
            last = session.query(func.max(session_model.id)).scalar() or 0
            return f"{prefix}-{year}-{last + 1:04d}"
        finally:
            session.close()

    @staticmethod
    def generate_sale_number():
        return NumberingService.generate_number('sale', Sale, 'INV')

    @staticmethod
    def generate_purchase_number():
        return NumberingService.generate_number('purchase', Purchase, 'PUR')

    @staticmethod
    def generate_invoice_number():
        return NumberingService.generate_number('invoice', Invoice, 'INV')
