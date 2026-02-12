CREATE TABLE IF NOT EXISTS analysis_log (
  id SERIAL PRIMARY KEY,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  metric TEXT NOT NULL,
  range TEXT NOT NULL,
  style TEXT NOT NULL,
  sql TEXT NOT NULL,
  narrative TEXT,
  risk TEXT,
  recommendation TEXT
);
