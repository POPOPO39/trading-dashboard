-- Run this SQL in your Supabase project's SQL editor

-- Poker sessions table
CREATE TABLE IF NOT EXISTS poker_sessions (
  id               TEXT PRIMARY KEY,
  date             TEXT NOT NULL,
  hands            INTEGER NOT NULL DEFAULT 0,
  bb_size          DOUBLE PRECISION NOT NULL DEFAULT 1,
  result_bb        DOUBLE PRECISION NOT NULL DEFAULT 0,
  rule_no_emotion      BOOLEAN NOT NULL DEFAULT TRUE,
  rule_stop_tilted     BOOLEAN NOT NULL DEFAULT TRUE,
  rule_no_random_calls BOOLEAN NOT NULL DEFAULT TRUE,
  notes            TEXT,
  created_at       TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE poker_sessions DISABLE ROW LEVEL SECURITY;
