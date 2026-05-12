-- Run this in Supabase SQL Editor
-- Allow result_usd to be NULL (= active/pending bet)
ALTER TABLE prediction_bets ALTER COLUMN result_usd DROP NOT NULL;
ALTER TABLE prediction_bets ALTER COLUMN result_usd SET DEFAULT NULL;
