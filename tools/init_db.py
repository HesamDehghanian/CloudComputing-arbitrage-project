import asyncio
from sqlalchemy import text
from main.db import engine

DDL = r"""
CREATE TABLE IF NOT EXISTS exchanges (
  id SERIAL PRIMARY KEY,
  name TEXT UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS pairs (
  id SERIAL PRIMARY KEY,
  symbol TEXT UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS ticks (
  id BIGSERIAL PRIMARY KEY,
  exchange_id INT NOT NULL REFERENCES exchanges(id),
  pair_id INT NOT NULL REFERENCES pairs(id),
  price NUMERIC(18,8) NOT NULL,
  fetched_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_ticks_pair_time ON ticks(pair_id, fetched_at DESC);
CREATE INDEX IF NOT EXISTS idx_ticks_exchange_time ON ticks(exchange_id, fetched_at DESC);

CREATE TABLE IF NOT EXISTS opportunities (
  id BIGSERIAL PRIMARY KEY,
  pair_id INT NOT NULL REFERENCES pairs(id),
  buy_exchange_id INT NOT NULL REFERENCES exchanges(id),
  sell_exchange_id INT NOT NULL REFERENCES exchanges(id),
  diff_abs NUMERIC(18,8) NOT NULL,
  diff_pct NUMERIC(9,6) NOT NULL,
  est_profit_usd NUMERIC(18,8),
  detected_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_opps_pair_time ON opportunities(pair_id, detected_at DESC);

CREATE TABLE IF NOT EXISTS alerts_sent (
  id BIGSERIAL PRIMARY KEY,
  opportunity_id BIGINT NOT NULL REFERENCES opportunities(id),
  chat_id TEXT,
  ok BOOLEAN NOT NULL,
  sent_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  error TEXT
);
CREATE INDEX IF NOT EXISTS idx_alerts_time ON alerts_sent(sent_at DESC);

INSERT INTO exchanges(name) VALUES ('Nobitex') ON CONFLICT DO NOTHING;
INSERT INTO exchanges(name) VALUES ('Wallex') ON CONFLICT DO NOTHING;
INSERT INTO pairs(symbol) VALUES ('BTCUSDT') ON CONFLICT DO NOTHING;
"""

async def run():
    async with engine.begin() as conn:
        for stmt in filter(None, DDL.split(';')):
            s = stmt.strip()
            if s:
                await conn.execute(text(s))

if __name__ == "__main__":
    asyncio.run(run())
