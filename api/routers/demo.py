from datetime import date, timedelta
import random
from fastapi import APIRouter
from sqlalchemy import create_engine, text
import os

router = APIRouter(tags=["demo"])

DATABASE_URL = os.getenv("DATABASE_URL", "").strip()
if not DATABASE_URL:
    # 안전 fallback (로컬 실행용)
    DATABASE_URL = "postgresql+psycopg://admin:admin123@localhost:5432/analytics"

engine = create_engine(DATABASE_URL, pool_pre_ping=True)


@router.post("/seed-demo")
def seed_demo(days: int = 90):
    """
    10초 데모 데이터 생성:
    - demo_sales_daily 테이블 없으면 자동 생성
    - 최근 N일치 일자/국가별 revenue/orders/customers 생성
    """
    countries = ["US", "CA", "KR", "JP", "BR", "DE"]
    today = date.today()
    start = today - timedelta(days=days - 1)

    create_sql = """
    CREATE TABLE IF NOT EXISTS demo_sales_daily (
      d date NOT NULL,
      country text NOT NULL,
      revenue numeric(14,2) NOT NULL,
      orders int NOT NULL,
      customers int NOT NULL,
      PRIMARY KEY (d, country)
    );
    """

    # 기존 데이터 삭제 후 재생성(데모용)
    # 원하면 이 줄 지워도 됨.
    truncate_sql = "TRUNCATE TABLE demo_sales_daily;"

    insert_sql = """
    INSERT INTO demo_sales_daily (d, country, revenue, orders, customers)
    VALUES (:d, :country, :revenue, :orders, :customers)
    ON CONFLICT (d, country)
    DO UPDATE SET revenue=EXCLUDED.revenue, orders=EXCLUDED.orders, customers=EXCLUDED.customers;
    """

    rows = 0
    with engine.begin() as conn:
        conn.execute(text(create_sql))
        conn.execute(text(truncate_sql))

        d = start
        while d <= today:
            base_mult = 1.0 + (0.15 * (1 if d.weekday() in (4, 5) else 0))  # 금/토 약간 상승
            for c in countries:
                # 국가별 베이스 스케일
                scale = {
                    "US": 1.00, "CA": 0.35, "KR": 0.55, "JP": 0.50, "BR": 0.40, "DE": 0.45
                }[c]

                orders = max(5, int(random.gauss(120 * scale * base_mult, 18 * scale)))
                customers = max(3, int(orders * random.uniform(0.55, 0.85)))
                aov = random.uniform(35, 95) * (1.05 if c in ("US", "DE") else 1.0)
                revenue = round(orders * aov * random.uniform(0.92, 1.08), 2)

                conn.execute(
                    text(insert_sql),
                    {"d": d, "country": c, "revenue": revenue, "orders": orders, "customers": customers},
                )
                rows += 1
            d += timedelta(days=1)

    return {
        "ok": True,
        "message": "Demo data seeded.",
        "table": "demo_sales_daily",
        "days": days,
        "rows_upserted": rows,
        "countries": countries,
    }
