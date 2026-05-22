"""
AI Module for ProComSoft ERP
<<<<<<< HEAD
Advanced analytics: forecasting, recommendations, anomaly detection, customer insights
"""
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from database.models import Sale, SaleItem, Product, Customer, Invoice, Payment
from database.models import InventoryItem, Warehouse, Supplier, Purchase, Session
from sqlalchemy import func, extract, case
import math
import statistics


class AdvancedForecaster:
    """Multiple forecasting methods for sales prediction"""

    @staticmethod
    def _get_daily_sales(days=90):
        session = Session()
        try:
            start = datetime.now() - timedelta(days=days)
            data = session.query(
                func.date(Sale.date).label('day'),
                func.sum(Sale.total).label('total'),
                func.count(Sale.id).label('count'),
            ).filter(Sale.date >= start).group_by(func.date(Sale.date)).order_by(
                func.date(Sale.date)).all()
            return [{'date': str(r.day), 'total': float(r.total or 0), 'count': int(r.count)}
                    for r in data]
        finally:
            session.close()

    @staticmethod
    def moving_average(days=30, window=7):
        """Forecast using moving average"""
        data = AdvancedForecaster._get_daily_sales(days * 3)
        values = [d['total'] for d in data]
        if len(values) < window:
            return {'prediction': 0, 'confidence': 'low'}
        recent = values[-window:]
        avg = sum(recent) / len(recent)
        projected = avg * days
        std = statistics.stdev(recent) if len(recent) > 1 else avg * 0.1
        return {
            'prediction': round(projected, 2),
            'daily_avg': round(avg, 2),
            'std_dev': round(std, 2),
            'confidence': 'high' if len(values) > 30 else 'medium',
            'method': 'moving_average',
            'window': window,
        }

    @staticmethod
    def exponential_smoothing(days=30, alpha=0.3):
        """Forecast using exponential smoothing"""
        data = AdvancedForecaster._get_daily_sales(days * 3)
        values = [d['total'] for d in data]
        if not values:
            return {'prediction': 0, 'confidence': 'low'}
        smoothed = values[0]
        for v in values[1:]:
            smoothed = alpha * v + (1 - alpha) * smoothed
        return {
            'prediction': round(smoothed * days, 2),
            'daily_avg': round(smoothed, 2),
            'alpha': alpha,
            'confidence': 'medium',
            'method': 'exponential_smoothing',
        }

    @staticmethod
    def linear_regression(days=30):
        """Forecast using linear regression"""
        data = AdvancedForecaster._get_daily_sales(days * 3)
        values = [d['total'] for d in data]
        n = len(values)
        if n < 3:
            return {'prediction': 0, 'confidence': 'low', 'message': 'Not enough data'}
        x = list(range(n))
        y = values
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(i * j for i, j in zip(x, y))
        sum_xx = sum(i * i for i in x)
        denom = n * sum_xx - sum_x * sum_x
        slope = (n * sum_xy - sum_x * sum_y) / denom if denom != 0 else 0
        intercept = (sum_y - slope * sum_x) / n
        prediction = sum(slope * (n + i) + intercept for i in range(days))
        prediction = max(0, prediction)
        daily_avg = sum_y / n
        conf = 'high' if n > 20 and abs(slope / daily_avg) < 0.05 else 'medium' if n > 7 else 'low'
        return {
            'prediction': round(prediction, 2),
            'daily_avg': round(daily_avg, 2),
            'trend': 'up' if slope > 0 else 'down',
            'slope': round(slope, 4),
            'confidence': conf,
            'method': 'linear_regression',
            'days_analyzed': n,
        }

    @staticmethod
    def seasonal_forecast(days=30):
        """Detect weekly seasonality and forecast"""
        data = AdvancedForecaster._get_daily_sales(60)
        if len(data) < 14:
            return {'prediction': 0, 'confidence': 'low', 'message': 'Need 14+ days'}
        weekday_totals = defaultdict(list)
        for d in data:
            dt = datetime.strptime(d['date'], '%Y-%m-%d')
            weekday_totals[dt.weekday()].append(d['total'])
        weekday_avg = {}
        for day, vals in weekday_totals.items():
            weekday_avg[day] = sum(vals) / len(vals) if vals else 0
        prediction = 0
        today = datetime.now()
        for i in range(days):
            future_day = (today + timedelta(days=i)).weekday()
            prediction += weekday_avg.get(future_day, 0)
        overall_avg = sum(weekday_avg.values()) / 7 if weekday_avg else 0
        return {
            'prediction': round(prediction, 2),
            'daily_avg': round(overall_avg, 2),
            'method': 'seasonal',
            'confidence': 'high' if len(data) > 40 else 'medium',
            'pattern': {['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'][k]: round(v, 2)
                       for k, v in sorted(weekday_avg.items())},
        }

    @staticmethod
    def ensemble_forecast(days=30):
        """Combine all methods for best prediction"""
        results = []
        methods = [
            AdvancedForecaster.moving_average(days),
            AdvancedForecaster.exponential_smoothing(days),
            AdvancedForecaster.linear_regression(days),
            AdvancedForecaster.seasonal_forecast(days),
        ]
        valid = [m for m in methods if m.get('prediction', 0) > 0 and m.get('confidence') != 'low']
        if not valid:
            return {'prediction': 0, 'confidence': 'low', 'message': 'Not enough data'}
        predictions = [m['prediction'] for m in valid]
        weights = {'high': 3, 'medium': 2, 'low': 1}
        total_weight = sum(weights.get(m.get('confidence', 'low'), 1) for m in valid)
        weighted_pred = sum(
            m['prediction'] * weights.get(m.get('confidence', 'low'), 1) for m in valid
        ) / total_weight if total_weight > 0 else sum(predictions) / len(predictions)
        return {
            'prediction': round(weighted_pred, 2),
            'methods_used': len(valid),
            'confidence': 'high' if any(m.get('confidence') == 'high' for m in valid) else 'medium',
            'ensemble_size': len(valid),
            'details': {m['method']: m['prediction'] for m in valid},
        }


class MarketBasketAnalyzer:
    """Association rule mining for product recommendations"""

    @staticmethod
    def get_association_rules(min_support=2, min_confidence=0.3):
        """Find product associations using market basket analysis"""
        session = Session()
        try:
            thirty_days = datetime.now() - timedelta(days=60)
            baskets = session.query(
                SaleItem.sale_id, SaleItem.product_id
            ).join(Sale, SaleItem.sale_id == Sale.id
            ).filter(Sale.date >= thirty_days).all()

            transaction_map = defaultdict(set)
            for sale_id, product_id in baskets:
                transaction_map[sale_id].add(product_id)

            pair_counts = Counter()
            item_counts = Counter()
            product_names = {}

            for txn_id, items in transaction_map.items():
                items_list = list(items)
                for i in items_list:
                    item_counts[i] += 1
                for i in range(len(items_list)):
                    for j in range(i + 1, len(items_list)):
                        a, b = items_list[i], items_list[j]
                        if a < b:
                            pair_counts[(a, b)] += 1
                        else:
                            pair_counts[(b, a)] += 1

            for pid in item_counts:
                prod = session.query(Product.name).filter(Product.id == pid).first()
                if prod:
                    product_names[pid] = prod.name

            rules = []
            for (a, b), count in pair_counts.items():
                if count < min_support:
                    continue
                support_a = item_counts[a]
                support_b = item_counts[b]
                confidence_ab = count / support_a if support_a > 0 else 0
                confidence_ba = count / support_b if support_b > 0 else 0
                lift = count / ((support_a / len(transaction_map)) * (support_b / len(transaction_map))) if support_a > 0 and support_b > 0 else 0
                if confidence_ab >= min_confidence:
                    rules.append({
                        'product_a': a, 'product_b': b,
                        'name_a': product_names.get(a, 'Unknown'),
                        'name_b': product_names.get(b, 'Unknown'),
                        'support': count,
                        'confidence': round(confidence_ab, 3),
                        'lift': round(lift, 2),
                    })
                if confidence_ba >= min_confidence:
                    rules.append({
                        'product_a': b, 'product_b': a,
                        'name_a': product_names.get(b, 'Unknown'),
                        'name_b': product_names.get(a, 'Unknown'),
                        'support': count,
                        'confidence': round(confidence_ba, 3),
                        'lift': round(lift, 2),
                    })

            return sorted(rules, key=lambda r: r['lift'], reverse=True)[:50]
        finally:
            session.close()

    @staticmethod
    def suggest_bundle(product_ids, max_items=3):
        """Suggest product bundle based on association rules"""
        rules = MarketBasketAnalyzer.get_association_rules(min_support=1, min_confidence=0.2)
        suggestions = defaultdict(float)
        for r in rules:
            if r['product_a'] in product_ids and r['product_b'] not in product_ids:
                suggestions[r['product_b']] = max(suggestions[r['product_b']], r['lift'])
        top = sorted(suggestions.items(), key=lambda x: x[1], reverse=True)[:max_items]
        session = Session()
        try:
            result = []
            for pid, score in top:
                p = session.query(Product.id, Product.name, Product.selling_price
                ).filter(Product.id == pid).first()
                if p:
                    result.append({
                        'product_id': p.id, 'name': p.name,
                        'price': float(p.selling_price), 'score': round(score, 2),
                    })
            return result
        finally:
            session.close()


class CustomerAnalytics:
    """Advanced customer analytics: RFM, churn, CLV, segmentation"""

    @staticmethod
    def rfm_segmentation():
        """RFM (Recency, Frequency, Monetary) customer segmentation"""
        session = Session()
        try:
            now = datetime.now()
            customers = session.query(
                Customer.id, Customer.name, Customer.code, Customer.email, Customer.phone,
                func.max(Sale.date).label('last_purchase'),
                func.count(Sale.id).label('frequency'),
                func.coalesce(func.sum(Sale.total), 0).label('monetary'),
            ).outerjoin(Sale, Customer.id == Sale.customer_id
            ).filter(Customer.is_active == True
            ).group_by(Customer.id).all()

            segments = []
            for c in customers:
                if c.frequency == 0:
                    segments.append({'id': c.id, 'name': c.name, 'code': c.code,
                                     'segment': 'Inactive', 'score': 0})
                    continue
                days_since = (now - c.last_purchase).days if c.last_purchase else 999
                r_score = 5 if days_since <= 7 else 4 if days_since <= 30 else 3 if days_since <= 90 else 2 if days_since <= 180 else 1
                f_score = 5 if c.frequency >= 10 else 4 if c.frequency >= 5 else 3 if c.frequency >= 3 else 2 if c.frequency >= 1 else 1
                m_score = 5 if c.monetary >= 100000 else 4 if c.monetary >= 50000 else 3 if c.monetary >= 10000 else 2 if c.monetary >= 1000 else 1
                total_score = r_score + f_score + m_score
                if total_score >= 13:
                    segment = 'Champion'
                elif total_score >= 10:
                    segment = 'Loyal'
                elif total_score >= 7:
                    segment = 'Potential'
                elif r_score <= 2 and f_score >= 3:
                    segment = 'At Risk'
                elif r_score <= 2:
                    segment = 'Lost'
                else:
                    segment = 'New'
                segments.append({
                    'id': c.id, 'name': c.name, 'code': c.code,
                    'email': c.email, 'phone': c.phone,
                    'recency_days': days_since,
                    'frequency': int(c.frequency),
                    'monetary': round(float(c.monetary), 2),
                    'r_score': r_score, 'f_score': f_score, 'm_score': m_score,
                    'rfm_score': total_score,
                    'segment': segment,
                })
            return sorted(segments, key=lambda s: s['rfm_score'], reverse=True)
        finally:
            session.close()

    @staticmethod
    def churn_prediction(days_no_purchase=90):
        """Predict customers at risk of churning"""
        segments = CustomerAnalytics.rfm_segmentation()
        churned = [s for s in segments if s['segment'] in ('At Risk', 'Lost')]
        at_risk = [s for s in segments if s['segment'] == 'At Risk']
        return {
            'total_customers': len(segments),
            'churned_count': len(churned),
            'at_risk_count': len(at_risk),
            'churn_rate': round(len(churned) / len(segments) * 100, 1) if segments else 0,
            'churned': [{
                'name': s['name'], 'code': s['code'],
                'days_inactive': s['recency_days'],
                'last_spent': s['monetary'],
                'segment': s['segment'],
            } for s in churned[:20]],
            'at_risk': [{
                'name': s['name'], 'code': s['code'],
                'days_inactive': s['recency_days'],
                'last_spent': s['monetary'],
            } for s in at_risk[:20]],
        }

    @staticmethod
    def customer_lifetime_value():
        """Predict Customer Lifetime Value (CLV)"""
        segments = CustomerAnalytics.rfm_segmentation()
        total_clv = sum(s['monetary'] for s in segments)
        avg_clv = total_clv / len(segments) if segments else 0
        result = {'total_clv': round(total_clv, 2), 'avg_clv': round(avg_clv, 2),
                  'segments': {}}
        seg_groups = defaultdict(list)
        for s in segments:
            seg_groups[s['segment']].append(s['monetary'])
        for seg, vals in seg_groups.items():
            result['segments'][seg] = {
                'count': len(vals),
                'total': round(sum(vals), 2),
                'avg': round(sum(vals) / len(vals), 2),
                'pct': round(len(vals) / len(segments) * 100, 1),
            }
        return result

    @staticmethod
    def purchase_behavior_analysis():
        """Analyze customer purchase patterns"""
        session = Session()
        try:
            now = datetime.now()
            year_ago = now - timedelta(days=365)
            data = session.query(
                func.strftime('%H', Sale.date).label('hour'),
                func.count(Sale.id).label('count'),
                func.sum(Sale.total).label('total'),
            ).filter(Sale.date >= year_ago
            ).group_by('hour').order_by('hour').all()

            hourly = [{'hour': int(r.hour), 'count': int(r.count),
                       'total': round(float(r.total), 2)} for r in data]

            peak_hour = max(hourly, key=lambda h: h['count']) if hourly else {}
            return {
                'total_transactions': sum(h['count'] for h in hourly),
                'peak_hour': peak_hour.get('hour', '-'),
                'peak_count': peak_hour.get('count', 0),
                'hourly_breakdown': hourly,
                'busiest_day': CustomerAnalytics._busiest_day(),
            }
        finally:
            session.close()

    @staticmethod
    def _busiest_day():
        session = Session()
        try:
            now = datetime.now()
            year_ago = now - timedelta(days=365)
            data = session.query(
                func.strftime('%w', Sale.date).label('dow'),
                func.count(Sale.id).label('count'),
            ).filter(Sale.date >= year_ago
            ).group_by('dow').order_by('count').all()
            days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
            return [{'day': days[int(r.dow)], 'count': int(r.count)} for r in data]
        finally:
            session.close()


class AnomalyDetector:
    """Statistical anomaly detection for sales data"""

    @staticmethod
    def detect_sales_anomalies(days=30, threshold=2.0):
        """Detect unusual sales patterns using z-score"""
        session = Session()
        try:
            start = datetime.now() - timedelta(days=days)
            data = session.query(
                func.date(Sale.date).label('day'),
                func.sum(Sale.total).label('total'),
                func.count(Sale.id).label('count'),
            ).filter(Sale.date >= start
            ).group_by(func.date(Sale.date)).all()

            values = [float(r.total) for r in data]
            if len(values) < 5:
                return {'anomalies': [], 'message': 'Not enough data'}

            mean = statistics.mean(values)
            std = statistics.stdev(values) if len(values) > 1 else 0
            anomalies = []
            for r in data:
                val = float(r.total)
                z = (val - mean) / std if std > 0 else 0
                if abs(z) > threshold:
                    anomalies.append({
                        'date': str(r.day), 'value': round(val, 2),
                        'expected': round(mean, 2), 'z_score': round(z, 2),
                        'type': 'spike' if val > mean else 'drop',
                        'severity': 'high' if abs(z) > 3 else 'medium',
                    })

            return {
                'anomalies': sorted(anomalies, key=lambda a: abs(a['z_score']), reverse=True),
                'total_days': len(values),
                'mean': round(mean, 2),
                'std': round(std, 2),
                'threshold': threshold,
            }
        finally:
            session.close()

    @staticmethod
    def detect_unusual_transactions(days=7, max_deviation=3):
        """Flag unusually large or small transactions"""
        session = Session()
        try:
            start = datetime.now() - timedelta(days=days)
            sales = session.query(
                Sale.id, Sale.number, Sale.total, Sale.date,
                Customer.name.label('customer'),
            ).outerjoin(Customer, Sale.customer_id == Customer.id
            ).filter(Sale.date >= start).all()

            totals = [float(s.total) for s in sales if s.total > 0]
            if len(totals) < 5:
                return {'flags': []}

            mean = statistics.mean(totals)
            std = statistics.stdev(totals) if len(totals) > 1 else 0
            flags = []
            for s in sales:
                val = float(s.total)
                if std > 0 and abs(val - mean) / std > max_deviation:
                    flags.append({
                        'id': s.id, 'number': s.number,
                        'amount': round(val, 2), 'date': s.date.strftime('%Y-%m-%d'),
                        'customer': s.customer or 'Walk-in',
                        'deviation': round(abs(val - mean) / std, 1),
                        'reason': 'Very high' if val > mean else 'Very low',
                    })
            return {'flags': flags, 'mean': round(mean, 2), 'std': round(std, 2)}
        finally:
            session.close()


class PriceOptimizer:
    """Price analysis and optimization suggestions"""

    @staticmethod
    def price_elasticity():
        """Estimate price elasticity from sales data"""
        session = Session()
        try:
            products = session.query(
                Product.id, Product.name, Product.code,
                Product.cost_price, Product.selling_price,
                func.coalesce(func.sum(SaleItem.quantity), 0).label('qty_sold'),
                func.coalesce(func.sum(SaleItem.total), 0).label('revenue'),
                func.count(SaleItem.id).label('sale_count'),
            ).outerjoin(SaleItem, Product.id == SaleItem.product_id
            ).filter(Product.is_active == True, Product.cost_price > 0
            ).group_by(Product.id).having(func.sum(SaleItem.quantity) > 0).all()

            insights = []
            for p in products:
                margin = ((p.selling_price - p.cost_price) / p.selling_price * 100) if p.selling_price > 0 else 0
                markup = ((p.selling_price - p.cost_price) / p.cost_price * 100) if p.cost_price > 0 else 0
                recommended_price = p.cost_price * 1.4
                optimal_price = min(recommended_price, p.selling_price * 1.1)
                insights.append({
                    'id': p.id, 'name': p.name, 'code': p.code,
                    'cost': round(float(p.cost_price), 2),
                    'current_price': round(float(p.selling_price), 2),
                    'margin_pct': round(margin, 1),
                    'markup_pct': round(markup, 1),
                    'qty_sold': int(p.qty_sold),
                    'revenue': round(float(p.revenue), 2),
                    'recommended_price': round(max(p.cost_price * 1.2, optimal_price), 2),
                    'status': 'Good' if margin >= 30 else 'Low Margin' if margin >= 15 else 'Thin',
                })

            return sorted(insights, key=lambda x: x['margin_pct'])
        finally:
            session.close()

    @staticmethod
    def suggest_dynamic_pricing(product_id):
        """Suggest optimal price based on sales velocity"""
        session = Session()
        try:
            p = session.query(Product).filter(Product.id == product_id).first()
            if not p:
                return None
            thirty_days = datetime.now() - timedelta(days=30)
            sales_data = session.query(
                func.sum(SaleItem.quantity).label('qty'),
                func.avg(SaleItem.unit_price).label('avg_price'),
            ).filter(SaleItem.product_id == product_id
            ).join(Sale, SaleItem.sale_id == Sale.id
            ).filter(Sale.date >= thirty_days).first()

            qty = float(sales_data.qty or 0)
            avg_price = float(sales_data.avg_price or p.selling_price)
            daily_rate = qty / 30
            stock = session.query(InventoryItem.quantity).filter(
                InventoryItem.product_id == product_id,
                InventoryItem.warehouse_id == Warehouse.id,
                Warehouse.is_default == True,
            ).scalar() or 0

            suggestions = []
            suggestions.append({
                'strategy': 'Maintain',
                'price': round(float(p.selling_price), 2),
                'reason': 'Current pricing',
            })
            if daily_rate > 3 and stock < 20:
                suggestions.append({
                    'strategy': 'Increase 10%',
                    'price': round(float(p.selling_price) * 1.1, 2),
                    'reason': f'High demand ({daily_rate:.1f}/day), low stock ({stock})',
                })
            elif daily_rate < 1 and stock > 50:
                suggestions.append({
                    'strategy': 'Discount 15%',
                    'price': round(float(p.selling_price) * 0.85, 2),
                    'reason': f'Slow moving ({daily_rate:.1f}/day), excess stock ({stock})',
                })
            if p.cost_price > 0:
                min_price = p.cost_price * 1.1
                price_range = [min_price, p.selling_price * 1.2]
                suggestions.append({
                    'strategy': 'Range',
                    'price': f'{round(price_range[0], 2)} - {round(price_range[1], 2)}',
                    'reason': f'Cost-based range (cost: {p.cost_price})',
                })
            return {
                'product': p.name, 'code': p.code,
                'current_price': float(p.selling_price),
                'daily_sales': round(daily_rate, 2),
                'stock': float(stock),
                'suggestions': suggestions,
=======
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
>>>>>>> 5058b63e17bc5c42e66a4f03a260eae69ba8e457
            }
        finally:
            session.close()


<<<<<<< HEAD
class InventoryIntelligence:
    """Smart inventory management"""

    @staticmethod
    def reorder_recommendations():
        """Calculate optimal reorder quantities and times"""
        session = Session()
        try:
            thirty_days = datetime.now() - timedelta(days=30)
            data = session.query(
                Product.id, Product.name, Product.code,
                Product.min_stock, Product.max_stock,
                Product.cost_price,
                InventoryItem.quantity,
                func.coalesce(func.sum(SaleItem.quantity), 0).label('sold'),
=======
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
>>>>>>> 5058b63e17bc5c42e66a4f03a260eae69ba8e457
            ).join(InventoryItem, Product.id == InventoryItem.product_id
            ).outerjoin(SaleItem, Product.id == SaleItem.product_id
            ).outerjoin(Sale, SaleItem.sale_id == Sale.id
            ).filter(
<<<<<<< HEAD
                Sale.date >= thirty_days, Product.is_active == True,
            ).group_by(Product.id).all()

            recommendations = []
            for r in data:
                qty = float(r.quantity or 0)
                sold = float(r.sold or 0)
                daily_rate = sold / 30
                days_left = qty / daily_rate if daily_rate > 0 else float('inf')
                eoq = math.sqrt((2 * daily_rate * 365 * 50) / 5) if daily_rate > 0 else 0
                reorder_point = daily_rate * 7
                order_qty = max(r.min_stock or 10, int(eoq))

                if qty <= reorder_point or days_left < 7:
                    recommendations.append({
                        'id': r.id, 'name': r.name, 'code': r.code,
                        'current_stock': round(qty, 1),
                        'daily_sales': round(daily_rate, 2),
                        'days_remaining': round(days_left, 1) if days_left != float('inf') else '-',
                        'min_stock': float(r.min_stock or 0),
                        'reorder_point': round(reorder_point, 1),
                        'recommended_order': order_qty,
                        'cost': round(float(r.cost_price or 0), 2),
                        'estimated_cost': round(order_qty * float(r.cost_price or 0), 2),
                        'priority': 'High' if days_left < 3 else 'Medium' if days_left < 7 else 'Low',
                    })

            return sorted(recommendations, key=lambda x: x.get('days_remaining', 999) if isinstance(x.get('days_remaining'), (int, float)) else 999)
        finally:
            session.close()

    @staticmethod
    def stock_health_summary():
        """Overall stock health dashboard"""
        session = Session()
        try:
            total = session.query(func.count(Product.id)).filter(Product.is_active == True).scalar() or 0
            out_of_stock = session.query(func.count(InventoryItem.id)).filter(
                InventoryItem.quantity <= 0).scalar() or 0
            low_stock = session.query(func.count(InventoryItem.id)).join(
                Product, InventoryItem.product_id == Product.id
            ).filter(InventoryItem.quantity <= Product.min_stock,
                     InventoryItem.quantity > 0).scalar() or 0
            total_items = session.query(func.sum(InventoryItem.quantity)).scalar() or 0
            total_value = session.query(
                func.sum(InventoryItem.quantity * Product.cost_price)
            ).join(Product, InventoryItem.product_id == Product.id).scalar() or 0

            return {
                'total_products': total,
                'out_of_stock': out_of_stock,
                'low_stock': low_stock,
                'healthy': total - out_of_stock - low_stock,
                'total_items': int(total_items),
                'total_value': round(float(total_value), 2),
                'stock_health_pct': round((total - out_of_stock - low_stock) / total * 100, 1) if total else 0,
            }
        finally:
            session.close()


class BusinessIntelligence:
    """Overall business health and cash flow analysis"""

    @staticmethod
    def cash_flow_forecast(days=30):
        """Predict cash flow based on historical patterns"""
        session = Session()
        try:
            now = datetime.now()
            past = now - timedelta(days=90)
            sales_data = session.query(
                func.date(Sale.date).label('day'),
                func.sum(Sale.total).label('inflow'),
            ).filter(Sale.date >= past).group_by(func.date(Sale.date)).all()

            inflows = [float(r.inflow) for r in sales_data]
            avg_daily_inflow = sum(inflows) / len(inflows) if inflows else 0

            purchases_data = session.query(
                func.date(Purchase.date).label('day'),
                func.sum(Purchase.total).label('outflow'),
            ).filter(Purchase.date >= past).group_by(func.date(Purchase.date)).all()

            outflows = [float(r.outflow) for r in purchases_data]
            avg_daily_outflow = sum(outflows) / len(outflows) if outflows else 0

            projected_inflow = avg_daily_inflow * days
            projected_outflow = avg_daily_outflow * days
            net = projected_inflow - projected_outflow

            trend_in = 'up' if len(inflows) > 5 and inflows[-1] > inflows[0] else 'down' if inflows else 'stable'
            trend_out = 'up' if len(outflows) > 5 and outflows[-1] > outflows[0] else 'down' if outflows else 'stable'

            return {
                'projected_inflow': round(projected_inflow, 2),
                'projected_outflow': round(projected_outflow, 2),
                'net_cashflow': round(net, 2),
                'avg_daily_inflow': round(avg_daily_inflow, 2),
                'avg_daily_outflow': round(avg_daily_outflow, 2),
                'inflow_trend': trend_in,
                'outflow_trend': trend_out,
                'health': 'Good' if net > 0 else 'Warning' if net > -10000 else 'Critical',
            }
        finally:
            session.close()

    @staticmethod
    def business_health_score():
        """Calculate overall business health score (0-100)"""
        score = 0
        reasons = []

        session = Session()
        try:
            week_ago = datetime.now() - timedelta(days=7)
            recent_sales = session.query(func.count(Sale.id)).filter(
                Sale.date >= week_ago).scalar() or 0
            if recent_sales > 10:
                score += 20
                reasons.append(f'Active sales ({recent_sales} in 7d)')
            elif recent_sales > 0:
                score += 10
                reasons.append('Some sales activity')
            else:
                reasons.append('No recent sales (-10)')

            total_customers = session.query(func.count(Customer.id)).filter(
                Customer.is_active == True).scalar() or 0
            score += min(total_customers, 15)
            if total_customers > 10:
                reasons.append(f'Good customer base ({total_customers})')
            elif total_customers > 0:
                reasons.append(f'Building customer base ({total_customers})')

            stock = InventoryIntelligence.stock_health_summary()
            if stock['stock_health_pct'] > 80:
                score += 20
                reasons.append('Healthy stock levels')
            elif stock['stock_health_pct'] > 50:
                score += 10
                reasons.append('Adequate stock')
            else:
                reasons.append('Stock issues')

            cf = BusinessIntelligence.cash_flow_forecast(30)
            if cf['net_cashflow'] > 0:
                score += 20
                reasons.append('Positive cashflow')
            elif cf['net_cashflow'] > -10000:
                score += 10
                reasons.append('Cashflow manageable')
            else:
                reasons.append('Negative cashflow')

            sales_month = session.query(func.coalesce(func.sum(Sale.total), 0)).filter(
                Sale.date >= datetime.now().replace(day=1)).scalar()
            if sales_month > 0:
                score += 15
                reasons.append('Monthly revenue generating')

            churn = CustomerAnalytics.churn_prediction()
            if churn['churn_rate'] < 20:
                score += 10
                reasons.append('Low churn rate')
            elif churn['churn_rate'] < 40:
                score += 5
                reasons.append('Moderate churn')

            return {
                'score': min(score, 100),
                'rating': 'Excellent' if score >= 80 else 'Good' if score >= 60 else 'Fair' if score >= 40 else 'Poor',
                'reasons': reasons,
                'recent_sales_7d': recent_sales,
                'total_customers': total_customers,
                'stock_health': stock['stock_health_pct'],
                'cashflow': cf['net_cashflow'],
                'churn_rate': churn['churn_rate'],
            }
        finally:
            session.close()

    @staticmethod
    def revenue_breakdown():
        """Revenue breakdown by category"""
        session = Session()
        try:
            from database.models import Category
            year_ago = datetime.now() - timedelta(days=365)
            data = session.query(
                Category.name.label('category'),
                func.coalesce(func.sum(SaleItem.total), 0).label('revenue'),
                func.coalesce(func.sum(SaleItem.quantity), 0).label('qty'),
            ).join(Product, Category.id == Product.category_id
            ).join(SaleItem, Product.id == SaleItem.product_id
            ).join(Sale, SaleItem.sale_id == Sale.id
            ).filter(Sale.date >= year_ago
            ).group_by(Category.id).order_by(func.sum(SaleItem.total).desc()).all()

            total = sum(float(r.revenue) for r in data)
            return [{
                'category': r.category,
                'revenue': round(float(r.revenue), 2),
                'qty': int(r.qty),
                'pct': round(float(r.revenue) / total * 100, 1) if total else 0,
            } for r in data]
        finally:
            session.close()


# Enhanced aliases for backward compatibility
SalesForecaster = AdvancedForecaster
ProductRecommender = MarketBasketAnalyzer
StockPredictor = InventoryIntelligence
CustomerInsights = CustomerAnalytics
=======
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
>>>>>>> 5058b63e17bc5c42e66a4f03a260eae69ba8e457
