from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from contextlib import asynccontextmanager
import asyncio
from orderbook import OrderBook  
import aiohttp
import json
from database import initial_setup, insert_data, get_candles
from fastapi.middleware.cors import CORSMiddleware


orderbooks = {}
update_events = {} 
symbols = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT']

async def fill_all_history_in_background():
    async with aiohttp.ClientSession() as session:
        for symbol in symbols:
            print(f"BACKGROUND: Starting {symbol}...")
            async with session.get(f'https://api.binance.com/api/v3/klines?symbol={symbol}&interval=1d&limit=200') as response:
                klines = await response.json()
                for k in klines:
                    await insert_data(symbol, {
                        'time':   int(k([0]) // 1000),
                        'open':   float(k[1]),
                        'high':   float(k[2]),
                        'low':    float(k[3]),
                        'close':  float(k[4]),
                        'volume': float(k[5]),
                    })


@asynccontextmanager
async def lifespan(app: FastAPI):

    await initial_setup()
    async with aiohttp.ClientSession() as session:
        for symbol in symbols:
            orderbooks[symbol] = OrderBook(symbol)
            update_events[symbol] = asyncio.Event()
            await orderbooks[symbol].snapshot_data(session)
    
    asyncio.create_task(fill_all_history_in_background())
                    
    tasks = []
    for symbol, ob_instance in orderbooks.items():
        tasks.append(asyncio.create_task(ob_instance.update_data(update_events[symbol])))
    yield
    
    for task in tasks:
        task.cancel()
    await asyncio.gather(*tasks, return_exceptions=True)

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"], 
)
@app.get("/")
async def start():
    print("connected successfully")

@app.get("/price/{symbol}")
async def get_price(symbol:str):
    async with aiohttp.ClientSession() as session:
        async with session.get(f'https://api.binance.com/api/v3/ticker/price?symbol={symbol.upper()}') as response:
            data = await response.json()
            return {"price": data['price']}

@app.get("/candles/{symbol}")
async def fetch_candles(symbol: str):
    rows = await get_candles(symbol.upper(), 1100)
    return [
        {
            "time": r['time'], 
            "open": r['open'], 
            "high": r['high'], 
            "low": r['low'], 
            "close": r['close'], 
            "volume": r['volume']
        }
        for r in rows
    ]

@app.websocket("/ws/orderbook/{symbol}")
async def ws_orderbook(websocket: WebSocket, symbol: str):
    symbol = symbol.upper()
    await websocket.accept()

    if symbol not in orderbooks:
        await websocket.send_json({"error": "Invalid symbol"})
        await websocket.close()
        return
    
    target_book = orderbooks[symbol]
    target_event = update_events[symbol]

    try:
        while True: 
            await target_event.wait()           
            top_bids, top_asks = target_book.top(10)
            await websocket.send_json({
                "symbol": symbol,
                "bids": [{"price": p, "quantity": q} for p, q in top_bids],
                "asks": [{"price": p, "quantity": q} for p, q in top_asks],
            })
            
            await asyncio.sleep(0.1) 
            
    except WebSocketDisconnect:
        pass