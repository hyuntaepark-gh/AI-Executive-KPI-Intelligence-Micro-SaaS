from datetime import date
from typing import Optional
from psycopg2.extras import RealDictCursor
from ..db import get_conn

def fetch_kpi(from_: Optional[date] = None, to: Optional[date] = None):
    conn = get_conn(dict_cursor=True)
    cur = conn.cursor()

    if from_ and to:
        cur.execute("""
            SELECT month, revenue, orders, customers, aov
            FROM kpi_monthly
            WHERE month BETWEEN %s AND %s
            ORDER BY month;
        """, (from_, to))
    elif from_:
        cur.execute("""
            SELECT month, revenue, orders, customers, aov
            FROM kpi_monthly
            WHERE month >= %s
            ORDER BY month;
        """, (from_,))
    elif to:
        cur.execute("""
            SELECT month, revenue, orders, customers, aov
            FROM kpi_monthly
            WHERE month <= %s
            ORDER BY month;
        """, (to,))
    else:
        cur.execute("""
            SELECT month, revenue, orders, customers, aov
            FROM kpi_monthly
            ORDER BY month;
        """)

    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def upsert_kpi(month: date, revenue: float, orders: int, customers: int, aov: float):
    conn = get_conn(dict_cursor=False)
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO kpi_monthly (month, revenue, orders, customers, aov)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (month) DO UPDATE SET
            revenue = EXCLUDED.revenue,
            orders = EXCLUDED.orders,
            customers = EXCLUDED.customers,
            aov = EXCLUDED.aov;
    """, (month, revenue, orders, customers, aov))

    conn.commit()
    cur.close()
    conn.close()
    return {"month": str(month), "revenue": revenue, "orders": orders, "customers": customers, "aov": aov}
