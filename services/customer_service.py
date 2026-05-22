from database.models import Customer, Session


class CustomerService:
    @staticmethod
    def list(search=None):
        session = Session()
        try:
            query = session.query(Customer).filter(Customer.is_active == True)
            if search:
                query = query.filter(
                    Customer.name.ilike(f'%{search}%') |
                    Customer.code.ilike(f'%{search}%') |
                    Customer.email.ilike(f'%{search}%')
                )
            customers = query.all()
            return [{
                'id': c.id,
                'code': c.code,
                'name': c.name,
                'email': c.email,
                'phone': c.phone
            } for c in customers]
        finally:
            session.close()
