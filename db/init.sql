CREATE TABLE IF NOT EXISTS kpi_monthly (
  month date PRIMARY KEY,
  revenue numeric,
  orders integer,
  customers integer,
  aov numeric
);
