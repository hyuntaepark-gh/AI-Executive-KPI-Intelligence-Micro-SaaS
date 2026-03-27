CREATE TABLE IF NOT EXISTS kpi_monthly (
    month TEXT PRIMARY KEY,
    revenue REAL,
    orders INTEGER,
    customers INTEGER,
    aov REAL
);

INSERT OR REPLACE INTO kpi_monthly (month, revenue, orders, customers, aov) VALUES
('2025-10-01', 120000, 2400, 1800, 50.0),
('2025-11-01', 115000, 2200, 1700, 52.27),
('2025-12-01', 108000, 2000, 1600, 54.0);
