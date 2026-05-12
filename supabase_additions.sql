-- Run this SQL in your Supabase project's SQL editor

-- Poker daily GTO checkins (1 row per date)
CREATE TABLE IF NOT EXISTS poker_daily_checkins (
  date     TEXT PRIMARY KEY,
  todo_gto BOOLEAN NOT NULL DEFAULT FALSE
);
ALTER TABLE poker_daily_checkins DISABLE ROW LEVEL SECURITY;

-- Prediction market bets
CREATE TABLE IF NOT EXISTS prediction_bets (
  id               TEXT PRIMARY KEY,
  date             TEXT NOT NULL,
  category         TEXT NOT NULL DEFAULT '',
  title            TEXT NOT NULL DEFAULT '',
  bet_amount       DOUBLE PRECISION NOT NULL DEFAULT 0,
  result_usd       DOUBLE PRECISION NOT NULL DEFAULT 0,
  rule_positive_ev  BOOLEAN NOT NULL DEFAULT TRUE,
  rule_used_ev_calc BOOLEAN NOT NULL DEFAULT TRUE,
  notes            TEXT,
  created_at       TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE prediction_bets DISABLE ROW LEVEL SECURITY;
