import os
import asyncpg
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")


pool = None

async def get_pool():
    global pool
    if pool is None:
        print(f"DEBUG: Initializing pool with URL starting with: {str(DATABASE_URL)[:15]}...")
        if not DATABASE_URL:
            raise ValueError("DATABASE_URL is not set in Environment Variables!")
  
        pool = await asyncpg.create_pool(
            dsn=DATABASE_URL,
            min_size=1,
            max_size=5,
            ssl="require",
            command_timeout=60,
            statement_cache_size=0
        )
    return pool

async def initial_setup():
    print("DEBUG: Inside initial_setup, calling get_pool()...")
    db_pool = await get_pool()
    async with db_pool.acquire() as conn:
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

async def insert_data(symbol, candle):
    db_pool = await get_pool()
    async with db_pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO candles (symbol, time, open, high, low, close, volume)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            ON CONFLICT (symbol, time) DO UPDATE SET
                open = EXCLUDED.open, high = EXCLUDED.high, 
                low = EXCLUDED.low, close = EXCLUDED.close, volume = EXCLUDED.volume
        """, symbol, candle['time'], candle['open'], candle['high'], 
             candle['low'], candle['close'], candle['volume'])

async def get_candles(symbol, limit):
    db_pool = await get_pool()
    async with db_pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT * FROM candles WHERE symbol = $1 
            ORDER BY time DESC LIMIT $2
        """, symbol, limit)
        return [dict(row) for row in rows]