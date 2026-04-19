import aiosqlite

async def initial_setup():
    async with aiosqlite.connect('candles.db') as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS candles (
                symbol    TEXT,
                time      INTEGER,
                open      REAL,
                high      REAL,
                low       REAL,
                close     REAL,
                volume    REAL,
                PRIMARY KEY (symbol, time)
            )
        """)
        await db.commit()

async def insert_data(symbol, candle):
    async with aiosqlite.connect('candles.db') as db:
        await db.execute("""
            INSERT OR REPLACE INTO candles VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (symbol, candle['time'], candle['open'], candle['high'], 
              candle['low'], candle['close'], candle['volume'])
        )
        await db.commit()

async def get_candles(symbol, limit):
    async with aiosqlite.connect('candles.db') as db:
        cursor = await db.execute("""
            SELECT * FROM candles 
            WHERE symbol = ? 
            ORDER BY time DESC 
            LIMIT ?
        """, (symbol, limit)
        )
        rows = await cursor.fetchall()
        return rows
