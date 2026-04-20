import asyncio
import json
from websockets.asyncio.client import connect
import aiohttp

class OrderBook:
    def __init__(self, symbol):
        self.symbol = symbol.upper()
        self.ws_symbol = symbol.lower()
        self.bids = {}
        self.asks = {}

    async def snapshot_data(self, session):
        try:
            async with session.get(f'https://api.binance.com/api/v3/depth?symbol={self.symbol}&limit=100') as response:
                data = await response.json()
                self.apply_snapshot(data)
        except Exception as e:
            print(f"[{self.symbol}] Snapshot Error: {e}")

    def apply_snapshot(self, data):
        self.bids = {float(p[0]): float(p[1]) for p in data['bids']}
        self.asks = {float(p[0]): float(p[1]) for p in data['asks']}
    
    async def update_data(self, event: asyncio.Event):
        count = 0
        uri = f'wss://stream.binance.com:9443/ws/{self.ws_symbol}@depth'
        
        async for websocket in connect(uri):
            try:
                async for message in websocket:
                    self.apply_updated_data(json.loads(message))
                    count += 1
                    if count % 5 == 0:
                        event.set()
                        await asyncio.sleep(0) 
                        event.clear()
                        
            except Exception as e:
                print(f"[{self.symbol}] Connection lost, retrying... Error: {e}")
                await asyncio.sleep(1) 
                
    def apply_updated_data(self, updated_data):
        for price_str, qty_str in updated_data.get('b', []):
            price, qty = float(price_str), float(qty_str)
            if qty == 0:
                self.bids.pop(price, None)
            else:
                self.bids[price] = qty

        for price_str, qty_str in updated_data.get('a', []):
            price, qty = float(price_str), float(qty_str)
            if qty == 0:
                self.asks.pop(price, None)
            else:
                self.asks[price] = qty

    def top(self, n):
        top_bids = sorted(self.bids.items(), key=lambda x: x[0], reverse=True)[:n]
        top_asks = sorted(self.asks.items(), key=lambda x: x[0])[:n]
        return top_bids, top_asks