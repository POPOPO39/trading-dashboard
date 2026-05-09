-- Run this SQL in your Supabase project's SQL editor (https://supabase.com/dashboard)

-- Trades table
CREATE TABLE IF NOT EXISTS trades (
  id              TEXT PRIMARY KEY,
  date            TEXT NOT NULL,
  pair            TEXT NOT NULL,
  result          TEXT NOT NULL,
  pnl             DOUBLE PRECISION NOT NULL DEFAULT 0,
  commission      DOUBLE PRECISION NOT NULL DEFAULT 0,
  rr              DOUBLE PRECISION NOT NULL DEFAULT 0,
  rule_compliant  BOOLEAN NOT NULL DEFAULT TRUE,
  notes           TEXT,
  status          TEXT NOT NULL DEFAULT 'closed',
  is_demo         BOOLEAN NOT NULL DEFAULT FALSE,
  created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Settings table (single row)
CREATE TABLE IF NOT EXISTS settings (
  id                      SERIAL PRIMARY KEY,
  initial_balance         DOUBLE PRECISION NOT NULL DEFAULT 1000,
  monthly_target_pct      DOUBLE PRECISION NOT NULL DEFAULT 20,
  daily_loss_limit_pct    DOUBLE PRECISION NOT NULL DEFAULT 6,
  monthly_dd_limit_pct    DOUBLE PRECISION NOT NULL DEFAULT 10,
  min_win_rate            DOUBLE PRECISION NOT NULL DEFAULT 50,
  min_rr                  DOUBLE PRECISION NOT NULL DEFAULT 2,
  min_compliance_rate     DOUBLE PRECISION NOT NULL DEFAULT 90,
  max_risk_per_trade_pct  DOUBLE PRECISION NOT NULL DEFAULT 2,
  demo_initial_balance    DOUBLE PRECISION NOT NULL DEFAULT 10000
);

-- Insert default settings row
INSERT INTO settings (id) VALUES (1) ON CONFLICT DO NOTHING;

-- Allow public access (Anon key read/write) - Row Level Security off for simplicity
-- If you want to add auth later, enable RLS and add policies
ALTER TABLE trades DISABLE ROW LEVEL SECURITY;
ALTER TABLE settings DISABLE ROW LEVEL SECURITY;
