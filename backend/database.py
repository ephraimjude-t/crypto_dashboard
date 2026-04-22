import os
import asyncio
import asyncpg

DATABASE_URL = os.getenv("DATABASE_URL")

async def get_pool():

    return await asyncpg.create_pool(dsn=DATABASE_URL)

async def initial_setup():
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS candles (
                symbol    TEXT,
                time      BIGINT,
                open      DOUBLE PRECISION,
                high      DOUBLE PRECISION,
                low       DOUBLE PRECISION,
                close     DOUBLE PRECISION,
                volume    DOUBLE PRECISION,
                PRIMARY KEY (symbol, time)
            )
        """)
    finally:
        await conn.close()

async def insert_data(symbol, candle):
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        await conn.execute("""
            INSERT INTO candles (symbol, time, open, high, low, close, volume)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            ON CONFLICT (symbol, time) 
            DO UPDATE SET 
                open = EXCLUDED.open,
                high = EXCLUDED.high,
                low = EXCLUDED.low,
                close = EXCLUDED.close,
                volume = EXCLUDED.volume
        """, symbol, candle['time'], candle['open'], candle['high'], 
             candle['low'], candle['close'], candle['volume']
        )
    finally:
        await conn.close()

async def get_candles(symbol, limit):
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        rows = await conn.fetch("""
            SELECT * FROM candles 
            WHERE symbol = $1 
            ORDER BY time DESC 
            LIMIT $2
        """, symbol, limit)
        return [dict(row) for row in rows]
    finally:
        await conn.close()