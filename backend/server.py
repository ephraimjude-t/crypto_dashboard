from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from contextlib import asynccontextmanager
import asyncio
from orderbook import OrderBook  
import aiohttp
from websockets.asyncio.client import connect
import json
from database import initial_setup, insert_data, get_candles
from fastapi.middleware.cors import CORSMiddleware

orderbooks = {}
symbols = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT']


@asynccontextmanager
async def lifespan(app:FastAPI):
    await initial_setup()
    async with aiohttp.ClientSession() as session:
        for symbol in symbols:
            orderbooks[symbol] = OrderBook(symbol)
            await orderbooks[symbol].snapshot_data(session)
            async with session.get(f'https://api.binance.com/api/v3/klines?symbol={symbol}&interval=1d&limit=200') as response:
                klines = await response.json()
                for k in klines:
                    await insert_data(f'{symbol}', {
                        'time':   k[0] // 1000,
                        'open':   float(k[1]),
                        'high':   float(k[2]),
                        'low':    float(k[3]),
                        'close':  float(k[4]),
                        'volume': float(k[5]),
                    })
    tasks = []
    for symbol, ob_instance in orderbooks.items():
        tasks.append(asyncio.create_task(ob_instance.update_data(update_event)))
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

@app.get("/orderbook/{symbol}")
async def get_orderbook(symbol: str):
    symbol = symbol.upper()
    if symbol not in orderbooks:
        return {"error": "Symbol not supported"}, 404
    top_bids, top_asks = orderbooks[symbol].top(10) 
    return{
        "bids": [{"price": p, "quantity": q,}for p,q  in top_bids],
        "asks":[{"price": p, "quantity": q,}for p,q  in top_asks]
    }
    

@app.get("/price/{symbol}")
async def get_price(symbol:str):
    async with aiohttp.ClientSession() as session:
        async with session.get(f'https://api.binance.com/api/v3/ticker/price?symbol={symbol.upper()}') as response:
            data = await response.json()
            return {"price": data['price']}

@app.get("/priceChange/{symbol}")
async def get_change(symbol:str):
    async with aiohttp.ClientSession() as session:
        async with session.get(f'https://api.binance.com/api/v3/ticker/24hr?symbol={symbol.upper()}') as response:
            data = await response.json()
            return {"ChangePercent": data['priceChangePercent']}
        

update_event = asyncio.Event() 

@app.get("/candles/{symbol}")
async def fetch_candles(symbol: str):
    rows = await get_candles(symbol.upper(), 1100)
    return [
        {"time": r[1], "open": r[2], "high": r[3], 
         "low": r[4], "close": r[5], "volume": r[6]}
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

    try:
        while True: 
            await update_event.wait()
            update_event.clear()   
            top_bids, top_asks = target_book.top(5)
            data = {
                "symbol": symbol,
                "bids": [{"price": p, "quantity": q,}for p,q  in top_bids],
                "asks":[{"price": p, "quantity": q,}for p,q  in top_asks],
            
            }
            await websocket.send_json(data)
            
            
    except WebSocketDisconnect:
        print("Client disconnected normally.")
    except Exception as e:
        print(f"Error: {e}")
    

