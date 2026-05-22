<<<<<<< HEAD
"""
Loyalty Manager: manage customer loyalty points and redemption
"""
from datetime import datetime

class LoyaltyManager:
    def __init__(self, db):
        self.db = db

    def _get_conn(self):
        return self.db.get_connection()

    def add_points(self, customer_id, points, reason='Purchase'):
        """Add loyalty points to a customer."""
        conn = self._get_conn()
        cur = conn.cursor()
        cur.execute("UPDATE customers SET loyalty_points = loyalty_points + ? WHERE id = ?", (points, customer_id))
        cur.execute(
            "INSERT INTO loyalty_log (customer_id, points, type, reason, created_at) VALUES (?, ?, ?, ?, ?)",
            (customer_id, points, 'add', reason, datetime.now())
        )
        conn.commit()
        conn.close()

    def redeem_points(self, customer_id, points, reason='Redemption'):
        """Redeem loyalty points from a customer."""
        conn = self._get_conn()
        cur = conn.cursor()
        cur.execute("SELECT loyalty_points FROM customers WHERE id = ?", (customer_id,))
        row = cur.fetchone()
        if row and row['loyalty_points'] >= points:
            cur.execute("UPDATE customers SET loyalty_points = loyalty_points - ? WHERE id = ?", (points, customer_id))
            cur.execute(
                "INSERT INTO loyalty_log (customer_id, points, type, reason, created_at) VALUES (?, ?, ?, ?, ?)",
                (customer_id, points, 'redeem', reason, datetime.now())
            )
            conn.commit()
            conn.close()
            return True
        conn.close()
        return False

    def get_customer_points(self, customer_id):
        """Get current loyalty points for customer."""
        conn = self._get_conn()
        cur = conn.cursor()
        cur.execute("SELECT loyalty_points FROM customers WHERE id = ?", (customer_id,))
        row = cur.fetchone()
        conn.close()
        return row['loyalty_points'] if row else 0

    def get_loyalty_log(self, customer_id):
        """Get loyalty transaction log for customer."""
        conn = self._get_conn()
        cur = conn.cursor()
        cur.execute("SELECT * FROM loyalty_log WHERE customer_id = ? ORDER BY created_at DESC", (customer_id,))
        rows = cur.fetchall()
        conn.close()
        return [dict(r) for r in rows]
=======
"""
Loyalty Manager: manage customer loyalty points and redemption
"""
from datetime import datetime

class LoyaltyManager:
    def __init__(self, db):
        self.db = db

    def _get_conn(self):
        return self.db.get_connection()

    def add_points(self, customer_id, points, reason='Purchase'):
        """Add loyalty points to a customer."""
        conn = self._get_conn()
        cur = conn.cursor()
        cur.execute("UPDATE customers SET loyalty_points = loyalty_points + ? WHERE id = ?", (points, customer_id))
        cur.execute(
            "INSERT INTO loyalty_log (customer_id, points, type, reason, created_at) VALUES (?, ?, ?, ?, ?)",
            (customer_id, points, 'add', reason, datetime.now())
        )
        conn.commit()
        conn.close()

    def redeem_points(self, customer_id, points, reason='Redemption'):
        """Redeem loyalty points from a customer."""
        conn = self._get_conn()
        cur = conn.cursor()
        cur.execute("SELECT loyalty_points FROM customers WHERE id = ?", (customer_id,))
        row = cur.fetchone()
        if row and row['loyalty_points'] >= points:
            cur.execute("UPDATE customers SET loyalty_points = loyalty_points - ? WHERE id = ?", (points, customer_id))
            cur.execute(
                "INSERT INTO loyalty_log (customer_id, points, type, reason, created_at) VALUES (?, ?, ?, ?, ?)",
                (customer_id, points, 'redeem', reason, datetime.now())
            )
            conn.commit()
            conn.close()
            return True
        conn.close()
        return False

    def get_customer_points(self, customer_id):
        """Get current loyalty points for customer."""
        conn = self._get_conn()
        cur = conn.cursor()
        cur.execute("SELECT loyalty_points FROM customers WHERE id = ?", (customer_id,))
        row = cur.fetchone()
        conn.close()
        return row['loyalty_points'] if row else 0

    def get_loyalty_log(self, customer_id):
        """Get loyalty transaction log for customer."""
        conn = self._get_conn()
        cur = conn.cursor()
        cur.execute("SELECT * FROM loyalty_log WHERE customer_id = ? ORDER BY created_at DESC", (customer_id,))
        rows = cur.fetchall()
        conn.close()
        return [dict(r) for r in rows]
>>>>>>> 5058b63e17bc5c42e66a4f03a260eae69ba8e457
