"""
AI Module for ProComSoft ERP
Features: sales forecasting, product recommendations, stock prediction, customer insights
"""
from datetime import datetime, timedelta
from collections import defaultdict
from database.models import Sale, SaleItem, Product, Customer, InventoryItem, Session
from sqlalchemy import func, extract
import math


class SalesForecaster:
    @staticmethod
    def predict_next_period(days=30):
        """Predict total sales for next N days using linear regression"""
        session = Session()
        try:
            end = datetime.now()
            start = end - timedelta(days=days * 3)
            sales = session.query(
                func.date(Sale.date).label('day'),
                func.sum(Sale.total).label('total')
            ).filter(Sale.date >= start).group_by(func.date(Sale.date)).all()

            if len(sales) < 3:
                return {'prediction': 0, 'confidence': 'low', 'message': 'Not enough data'}

            x_vals = list(range(len(sales)))
            y_vals = [float(s.total) for s in sales]
            n = len(x_vals)
            sum_x = sum(x_vals)
            sum_y = sum(y_vals)
            sum_xy = sum(x * y for x, y in zip(x_vals, y_vals))
            sum_xx = sum(x * x for x in x_vals)

            slope = (n * sum_xy - sum_x * sum_y) / (n * sum_xx - sum_x * sum_x) if (n * sum_xx - sum_x * sum_x) != 0 else 0
            intercept = (sum_y - slope * sum_x) / n if n > 0 else 0

            prediction = sum(slope * (n + i) + intercept for i in range(days))
            prediction = max(0, prediction)

            daily_avg = sum_y / n if n > 0 else 0
            confidence = 'high' if n > 20 and abs(slope / daily_avg) < 0.1 else 'medium' if n > 7 else 'low'

            return {
                'prediction': round(prediction, 2),
                'daily_avg': round(daily_avg, 2),
                'trend': 'up' if slope > 0 else 'down',
                'confidence': confidence,
                'days_analyzed': n,
            }
        finally:
            session.close()


class ProductRecommender:
    @staticmethod
    def get_frequently_bought_together(product_id, limit=5):
        """Find products frequently bought with a given product"""
        session = Session()
        try:
            sale_ids = session.query(SaleItem.sale_id).filter(
                SaleItem.product_id == product_id).subquery()
            related = session.query(
                SaleItem.product_id,
                func.count(SaleItem.id).label('count'),
                Product.name,
                Product.selling_price,
            ).join(Product, SaleItem.product_id == Product.id
            ).filter(
                SaleItem.sale_id.in_(sale_ids),
                SaleItem.product_id != product_id,
                Product.is_active == True,
            ).group_by(SaleItem.product_id
            ).order_by(func.count(SaleItem.id).desc()
            ).limit(limit).all()

            return [{
                'product_id': r.product_id,
                'name': r.name,
                'price': float(r.selling_price),
                'score': int(r.count),
            } for r in related]
        finally:
            session.close()

    @staticmethod
    def get_top_selling_products(limit=10):
        """Get top selling products"""
        session = Session()
        try:
            results = session.query(
                Product.id,
                Product.name,
                Product.code,
                func.coalesce(func.sum(SaleItem.quantity), 0).label('qty'),
                func.coalesce(func.sum(SaleItem.total), 0).label('revenue'),
            ).outerjoin(SaleItem, Product.id == SaleItem.product_id
            ).filter(Product.is_active == True
            ).group_by(Product.id
            ).order_by(func.sum(SaleItem.quantity).desc()
            ).limit(limit).all()

            return [{
                'id': r.id,
                'name': r.name,
                'code': r.code,
                'quantity': int(r.qty),
                'revenue': round(float(r.revenue), 2),
            } for r in results]
        finally:
            session.close()

    @staticmethod
    def personalized_recommendations(customer_id, limit=5):
        """Recommend products based on customer purchase history"""
        session = Session()
        try:
            bought_product_ids = session.query(SaleItem.product_id).join(
                Sale, SaleItem.sale_id == Sale.id
            ).filter(Sale.customer_id == customer_id).distinct().subquery()

            top_products = session.query(
                Product.id, Product.name, Product.selling_price,
                func.count(SaleItem.id).label('popularity')
            ).join(SaleItem, Product.id == SaleItem.product_id
            ).join(Sale, SaleItem.sale_id == Sale.id
            ).filter(
                Sale.customer_id != customer_id,
                Product.id.notin_(bought_product_ids),
                Product.is_active == True,
            ).group_by(Product.id
            ).order_by(func.count(SaleItem.id).desc()
            ).limit(limit).all()

            return [{
                'id': p.id,
                'name': p.name,
                'price': float(p.selling_price),
            } for p in top_products]
        finally:
            session.close()


class StockPredictor:
    @staticmethod
    def get_low_stock_alerts(threshold_days=7):
        """Alert when stock will run out based on avg daily sales"""
        session = Session()
        try:
            now = datetime.now()
            thirty_days_ago = now - timedelta(days=30)

            results = session.query(
                Product.id,
                Product.name,
                Product.code,
                Product.min_stock,
                InventoryItem.quantity,
                func.coalesce(func.sum(SaleItem.quantity), 0).label('sold_30d'),
            ).join(InventoryItem, Product.id == InventoryItem.product_id
            ).outerjoin(SaleItem, Product.id == SaleItem.product_id
            ).outerjoin(Sale, SaleItem.sale_id == Sale.id
            ).filter(
                Sale.date >= thirty_days_ago,
                Product.is_active == True,
            ).group_by(Product.id).all()

            alerts = []
            for r in results:
                qty = float(r.quantity or 0)
                sold = float(r.sold_30d or 0)
                daily_rate = sold / 30 if sold > 0 else 0
                days_left = qty / daily_rate if daily_rate > 0 else float('inf')

                if daily_rate > 0 and days_left < threshold_days:
                    alerts.append({
                        'product_id': r.id,
                        'name': r.name,
                        'code': r.code,
                        'current_stock': qty,
                        'daily_sales': round(daily_rate, 2),
                        'days_remaining': round(days_left, 1),
                        'min_stock': float(r.min_stock or 0),
                    })

            return sorted(alerts, key=lambda a: a['days_remaining'])
        finally:
            session.close()


class CustomerInsights:
    @staticmethod
    def get_top_customers(limit=10):
        """Get top customers by total spending"""
        session = Session()
        try:
            results = session.query(
                Customer.id,
                Customer.code,
                Customer.name,
                func.count(Sale.id).label('orders'),
                func.coalesce(func.sum(Sale.total), 0).label('total_spent'),
                func.coalesce(func.avg(Sale.total), 0).label('avg_order'),
            ).outerjoin(Sale, Customer.id == Sale.customer_id
            ).filter(Customer.is_active == True
            ).group_by(Customer.id
            ).order_by(func.sum(Sale.total).desc()
            ).limit(limit).all()

            return [{
                'id': r.id,
                'code': r.code,
                'name': r.name,
                'orders': int(r.orders),
                'total_spent': round(float(r.total_spent), 2),
                'avg_order': round(float(r.avg_order), 2),
            } for r in results]
        finally:
            session.close()

    @staticmethod
    def get_sales_summary():
        """Get sales summary statistics"""
        session = Session()
        try:
            now = datetime.now()
            today = now.date()
            this_month = now.replace(day=1).date()

            today_total = session.query(func.coalesce(func.sum(Sale.total), 0)).filter(
                func.date(Sale.date) == today).scalar()
            month_total = session.query(func.coalesce(func.sum(Sale.total), 0)).filter(
                Sale.date >= this_month).scalar()
            total_sales = session.query(func.count(Sale.id)).scalar()
            avg_sale = session.query(func.coalesce(func.avg(Sale.total), 0)).scalar()

            return {
                'today': round(float(today_total), 2),
                'this_month': round(float(month_total), 2),
                'total_transactions': total_sales or 0,
                'average_sale': round(float(avg_sale), 2),
            }
        finally:
            session.close()
