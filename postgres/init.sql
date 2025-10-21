-- if database doesn't exist
CREATE DATABASE stocks;

\c stocks

-- if table exists
DROP TABLE IF EXISTS ticks_raw;

-- create fresh table
CREATE TABLE ticks_raw (
  stream_ts TIMESTAMPTZ NOT NULL,
  date DATE NOT NULL,
  index TEXT NOT NULL,
  open NUMERIC,
  high NUMERIC,
  low NUMERIC,
  close NUMERIC NOT NULL,
  adj_close NUMERIC,
  volume BIGINT NOT NULL,
  close_usd NUMERIC,
  trade_value NUMERIC
);