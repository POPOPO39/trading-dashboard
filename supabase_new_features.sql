-- Run in Supabase SQL Editor

-- Add entry price to trades
ALTER TABLE trades ADD COLUMN IF NOT EXISTS entry_price DOUBLE PRECISION NOT NULL DEFAULT 0;

-- Poker hand reviews table
CREATE TABLE IF NOT EXISTS poker_hand_reviews (
  id               TEXT PRIMARY KEY,
  date             TEXT NOT NULL,
  hero_position    TEXT NOT NULL DEFAULT '',
  villain_position TEXT NOT NULL DEFAULT '',
  hero_hand        TEXT NOT NULL DEFAULT '[]',
  villain_hand     TEXT NOT NULL DEFAULT '[]',
  flop_board       TEXT NOT NULL DEFAULT '[]',
  turn_card        TEXT NOT NULL DEFAULT 'null',
  river_card       TEXT NOT NULL DEFAULT 'null',
  preflop_pot_bb   DOUBLE PRECISION NOT NULL DEFAULT 0,
  preflop_action   TEXT NOT NULL DEFAULT '',
  preflop_memo     TEXT NOT NULL DEFAULT '',
  flop_pot_bb      DOUBLE PRECISION NOT NULL DEFAULT 0,
  flop_action      TEXT NOT NULL DEFAULT '',
  flop_memo        TEXT NOT NULL DEFAULT '',
  turn_pot_bb      DOUBLE PRECISION NOT NULL DEFAULT 0,
  turn_action      TEXT NOT NULL DEFAULT '',
  turn_memo        TEXT NOT NULL DEFAULT '',
  river_pot_bb     DOUBLE PRECISION NOT NULL DEFAULT 0,
  river_action     TEXT NOT NULL DEFAULT '',
  river_memo       TEXT NOT NULL DEFAULT '',
  result_bb        DOUBLE PRECISION,
  notes            TEXT NOT NULL DEFAULT '',
  created_at       TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE poker_hand_reviews DISABLE ROW LEVEL SECURITY;
