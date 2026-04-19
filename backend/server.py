from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from contextlib import asynccontextmanager
import asyncio
from orderbook import OrderBook  
import aiohttp
from websockets.asyncio.client import connect
import json
from database import initial_setup, insert_data, get_candles
from fastapi.middleware.cors import CORSMiddleware

book = OrderBook('BTCUSDT')
symbols = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT']


@asynccontextmanager
async def lifespan(app:FastAPI):
    await initial_setup()
    async with aiohttp.ClientSession() as session:
        await book.snapshot_data(session)
        for symbol in symbols:  
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
    update = asyncio.create_task(book.update_data(update_event))  
    yield
    update.cancel()  
    try:
        await update
    except asyncio.CancelledError:
        print('error: asyncio canceleld')

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"], 
)

@app.get("/orderbook")
async def get_orderbook():
    top_bids, top_asks = book.top(10) 
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
    

@app.websocket("/ws/orderbook")
async def ws_orderbook(websocket: WebSocket):
    await websocket.accept()
    try:
        while True: 
            await update_event.wait()
            update_event.clear()   
            top_bids, top_asks = book.top(5)
            data = {
                "symbol": book.symbol,
                "bids": [{"price": p, "quantity": q,}for p,q  in top_bids],
                "asks":[{"price": p, "quantity": q,}for p,q  in top_asks],
            
            }
            await websocket.send_json(data)
            
            
    except WebSocketDisconnect:
        print("Client disconnected normally.")
    except Exception as e:
        print(f"Error: {e}")
    

