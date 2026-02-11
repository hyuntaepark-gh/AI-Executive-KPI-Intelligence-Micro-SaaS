CREATE TABLE kpi_monthly (
    month DATE PRIMARY KEY,
    revenue NUMERIC,
    orders INT,
    customers INT,
    aov NUMERIC
);

INSERT INTO kpi_monthly VALUES
('2024-01-01', 10000, 120, 80, 125),
('2024-02-01', 13000, 150, 95, 136),
('2024-03-01', 9000, 110, 70, 118);
