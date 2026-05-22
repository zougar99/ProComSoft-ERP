<<<<<<< HEAD
"""
ReportManager: provides simple aggregated report queries for the POS
"""
from datetime import datetime

class ReportManager:
    def __init__(self, db):
        self.db = db

    def _get_conn(self):
        return self.db.get_connection()

    def daily_sales(self, date_str):
        """Return total number of invoices and sum of totals for a given date (YYYY-MM-DD)."""
        conn = self._get_conn()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) as cnt, SUM(total) as total FROM invoices WHERE date(created_at) = ?", (date_str,))
        row = cur.fetchone()
        conn.close()
        cnt = row['cnt'] if row and row['cnt'] is not None else 0
        total = float(row['total']) if row and row['total'] is not None else 0.0
        return {'date': date_str, 'invoices': cnt, 'total': total}

    def monthly_sales(self, year, month):
        """Return invoice count and sum for a given year and month (month as 1-12)."""
        ym = f"{int(year):04d}",
        mm = f"{int(month):02d}"
        conn = self._get_conn()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) as cnt, SUM(total) as total FROM invoices WHERE strftime('%Y', created_at)=? AND strftime('%m', created_at)=?", (ym[0], mm[0]))
        row = cur.fetchone()
        conn.close()
        cnt = row['cnt'] if row and row['cnt'] is not None else 0
        total = float(row['total']) if row and row['total'] is not None else 0.0
        return {'year': ym[0], 'month': mm[0], 'invoices': cnt, 'total': total}

    def top_products(self, limit=10, start_date=None, end_date=None):
        """Return top products by quantity sold and revenue in a date range (dates as YYYY-MM-DD)."""
        conn = self._get_conn()
        cur = conn.cursor()
        params = []
        where = ""
        if start_date:
            where += " AND date(inv.created_at) >= ?"
            params.append(start_date)
        if end_date:
            where += " AND date(inv.created_at) <= ?"
            params.append(end_date)

        sql = f"""
            SELECT p.id, p.name, SUM(ii.quantity) AS qty, SUM(ii.subtotal) AS revenue
            FROM invoice_items ii
            JOIN products p ON ii.product_id = p.id
            JOIN invoices inv ON ii.invoice_id = inv.id
            WHERE 1=1 {where}
            GROUP BY p.id
            ORDER BY qty DESC
            LIMIT ?
        """
        params.append(limit)
        cur.execute(sql, tuple(params))
        rows = cur.fetchall()
        conn.close()
        result = []
        for r in rows:
            result.append({'product_id': r['id'], 'name': r['name'], 'quantity': int(r['qty'] or 0), 'revenue': float(r['revenue'] or 0.0)})
        return result

    def sales_summary_range(self, start_date, end_date):
        """Return aggregated sales totals for a date range."""
        conn = self._get_conn()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) as cnt, SUM(total) as total FROM invoices WHERE date(created_at) >= ? AND date(created_at) <= ?", (start_date, end_date))
        row = cur.fetchone()
        conn.close()
        cnt = row['cnt'] if row and row['cnt'] is not None else 0
        total = float(row['total']) if row and row['total'] is not None else 0.0
        return {'start': start_date, 'end': end_date, 'invoices': cnt, 'total': total}
=======
"""
ReportManager: provides simple aggregated report queries for the POS
"""
from datetime import datetime

class ReportManager:
    def __init__(self, db):
        self.db = db

    def _get_conn(self):
        return self.db.get_connection()

    def daily_sales(self, date_str):
        """Return total number of invoices and sum of totals for a given date (YYYY-MM-DD)."""
        conn = self._get_conn()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) as cnt, SUM(total) as total FROM invoices WHERE date(created_at) = ?", (date_str,))
        row = cur.fetchone()
        conn.close()
        cnt = row['cnt'] if row and row['cnt'] is not None else 0
        total = float(row['total']) if row and row['total'] is not None else 0.0
        return {'date': date_str, 'invoices': cnt, 'total': total}

    def monthly_sales(self, year, month):
        """Return invoice count and sum for a given year and month (month as 1-12)."""
        ym = f"{int(year):04d}",
        mm = f"{int(month):02d}"
        conn = self._get_conn()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) as cnt, SUM(total) as total FROM invoices WHERE strftime('%Y', created_at)=? AND strftime('%m', created_at)=?", (ym[0], mm[0]))
        row = cur.fetchone()
        conn.close()
        cnt = row['cnt'] if row and row['cnt'] is not None else 0
        total = float(row['total']) if row and row['total'] is not None else 0.0
        return {'year': ym[0], 'month': mm[0], 'invoices': cnt, 'total': total}

    def top_products(self, limit=10, start_date=None, end_date=None):
        """Return top products by quantity sold and revenue in a date range (dates as YYYY-MM-DD)."""
        conn = self._get_conn()
        cur = conn.cursor()
        params = []
        where = ""
        if start_date:
            where += " AND date(inv.created_at) >= ?"
            params.append(start_date)
        if end_date:
            where += " AND date(inv.created_at) <= ?"
            params.append(end_date)

        sql = f"""
            SELECT p.id, p.name, SUM(ii.quantity) AS qty, SUM(ii.subtotal) AS revenue
            FROM invoice_items ii
            JOIN products p ON ii.product_id = p.id
            JOIN invoices inv ON ii.invoice_id = inv.id
            WHERE 1=1 {where}
            GROUP BY p.id
            ORDER BY qty DESC
            LIMIT ?
        """
        params.append(limit)
        cur.execute(sql, tuple(params))
        rows = cur.fetchall()
        conn.close()
        result = []
        for r in rows:
            result.append({'product_id': r['id'], 'name': r['name'], 'quantity': int(r['qty'] or 0), 'revenue': float(r['revenue'] or 0.0)})
        return result

    def sales_summary_range(self, start_date, end_date):
        """Return aggregated sales totals for a date range."""
        conn = self._get_conn()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) as cnt, SUM(total) as total FROM invoices WHERE date(created_at) >= ? AND date(created_at) <= ?", (start_date, end_date))
        row = cur.fetchone()
        conn.close()
        cnt = row['cnt'] if row and row['cnt'] is not None else 0
        total = float(row['total']) if row and row['total'] is not None else 0.0
        return {'start': start_date, 'end': end_date, 'invoices': cnt, 'total': total}
>>>>>>> 5058b63e17bc5c42e66a4f03a260eae69ba8e457
