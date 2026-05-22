<<<<<<< HEAD
"""
Promotions & Discounts Engine: manage time-based and rule-based promotional offers
"""
from datetime import datetime

class PromotionsManager:
    def __init__(self, db):
        self.db = db

    def _get_conn(self):
        return self.db.get_connection()

    def create_promotion(self, name, discount_percent, start_date, end_date, product_ids=None, min_total=0.0):
        """Create a new promotion.
        product_ids: list of product IDs or None (applies to all).
        """
        conn = self._get_conn()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO promotions (name, discount_percent, start_date, end_date, min_total, active) VALUES (?, ?, ?, ?, ?, ?)",
            (name, discount_percent, start_date, end_date, min_total, 1)
        )
        promo_id = cur.lastrowid
        if product_ids:
            for pid in product_ids:
                cur.execute("INSERT INTO promotion_products (promotion_id, product_id) VALUES (?, ?)", (promo_id, pid))
        conn.commit()
        conn.close()
        return promo_id

    def get_active_promotions(self):
        """Get all currently active promotions."""
        conn = self._get_conn()
        cur = conn.cursor()
        now = datetime.now().strftime('%Y-%m-%d')
        cur.execute(
            "SELECT * FROM promotions WHERE active = 1 AND start_date <= ? AND end_date >= ?",
            (now, now)
        )
        rows = cur.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def apply_promotions_to_cart(self, cart_items):
        """Calculate discount for cart items based on active promotions.
        cart_items: list of dicts with 'product_id', 'qty', 'unit_price'.
        Returns: total_discount.
        """
        promos = self.get_active_promotions()
        total_discount = 0.0
        for item in cart_items:
            for promo in promos:
                # Check if product is in promotion (or promo applies to all)
                conn = self._get_conn()
                cur = conn.cursor()
                cur.execute("SELECT COUNT(*) as cnt FROM promotion_products WHERE promotion_id = ? AND product_id = ?", (promo['id'], item['product_id']))
                has_product = cur.fetchone()['cnt'] > 0
                conn.close()
                
                if has_product or True:  # Simplified: apply to all if no product restriction
                    item_total = item['qty'] * item['unit_price']
                    if item_total >= promo['min_total']:
                        discount = item_total * (promo['discount_percent'] / 100.0)
                        total_discount += discount
                        break  # Use first matching promotion
        return total_discount

    def create_coupon(self, code, discount_percent, valid_until):
        """Create a coupon code."""
        conn = self._get_conn()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO coupons (code, discount_percent, valid_until, used) VALUES (?, ?, ?, ?)",
            (code, discount_percent, valid_until, 0)
        )
        conn.commit()
        conn.close()

    def redeem_coupon(self, code):
        """Redeem a coupon code; returns discount % or None if invalid."""
        conn = self._get_conn()
        cur = conn.cursor()
        now = datetime.now().strftime('%Y-%m-%d')
        cur.execute("SELECT * FROM coupons WHERE code = ? AND valid_until >= ? AND used = 0", (code, now))
        coupon = cur.fetchone()
        if coupon:
            cur.execute("UPDATE coupons SET used = 1 WHERE code = ?", (code,))
            conn.commit()
        conn.close()
        return coupon['discount_percent'] if coupon else None
=======
"""
Promotions & Discounts Engine: manage time-based and rule-based promotional offers
"""
from datetime import datetime

class PromotionsManager:
    def __init__(self, db):
        self.db = db

    def _get_conn(self):
        return self.db.get_connection()

    def create_promotion(self, name, discount_percent, start_date, end_date, product_ids=None, min_total=0.0):
        """Create a new promotion.
        product_ids: list of product IDs or None (applies to all).
        """
        conn = self._get_conn()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO promotions (name, discount_percent, start_date, end_date, min_total, active) VALUES (?, ?, ?, ?, ?, ?)",
            (name, discount_percent, start_date, end_date, min_total, 1)
        )
        promo_id = cur.lastrowid
        if product_ids:
            for pid in product_ids:
                cur.execute("INSERT INTO promotion_products (promotion_id, product_id) VALUES (?, ?)", (promo_id, pid))
        conn.commit()
        conn.close()
        return promo_id

    def get_active_promotions(self):
        """Get all currently active promotions."""
        conn = self._get_conn()
        cur = conn.cursor()
        now = datetime.now().strftime('%Y-%m-%d')
        cur.execute(
            "SELECT * FROM promotions WHERE active = 1 AND start_date <= ? AND end_date >= ?",
            (now, now)
        )
        rows = cur.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def apply_promotions_to_cart(self, cart_items):
        """Calculate discount for cart items based on active promotions.
        cart_items: list of dicts with 'product_id', 'qty', 'unit_price'.
        Returns: total_discount.
        """
        promos = self.get_active_promotions()
        total_discount = 0.0
        for item in cart_items:
            for promo in promos:
                # Check if product is in promotion (or promo applies to all)
                conn = self._get_conn()
                cur = conn.cursor()
                cur.execute("SELECT COUNT(*) as cnt FROM promotion_products WHERE promotion_id = ? AND product_id = ?", (promo['id'], item['product_id']))
                has_product = cur.fetchone()['cnt'] > 0
                conn.close()
                
                if has_product or True:  # Simplified: apply to all if no product restriction
                    item_total = item['qty'] * item['unit_price']
                    if item_total >= promo['min_total']:
                        discount = item_total * (promo['discount_percent'] / 100.0)
                        total_discount += discount
                        break  # Use first matching promotion
        return total_discount

    def create_coupon(self, code, discount_percent, valid_until):
        """Create a coupon code."""
        conn = self._get_conn()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO coupons (code, discount_percent, valid_until, used) VALUES (?, ?, ?, ?)",
            (code, discount_percent, valid_until, 0)
        )
        conn.commit()
        conn.close()

    def redeem_coupon(self, code):
        """Redeem a coupon code; returns discount % or None if invalid."""
        conn = self._get_conn()
        cur = conn.cursor()
        now = datetime.now().strftime('%Y-%m-%d')
        cur.execute("SELECT * FROM coupons WHERE code = ? AND valid_until >= ? AND used = 0", (code, now))
        coupon = cur.fetchone()
        if coupon:
            cur.execute("UPDATE coupons SET used = 1 WHERE code = ?", (code,))
            conn.commit()
        conn.close()
        return coupon['discount_percent'] if coupon else None
>>>>>>> 5058b63e17bc5c42e66a4f03a260eae69ba8e457
