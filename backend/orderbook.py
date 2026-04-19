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
            async with session.get(f'https://api.binance.com/api/v3/depth?symbol={self.symbol}&limit=20') as response:
                data = await response.json()
                self.apply_snapshot(data)
        except Exception as e:
            print(f"connection error {e}")

    def apply_snapshot(self, data):
        self.bids = {float(p[0]): float(p[1]) for p in data['bids']}
        self.asks = {float(p[0]): float(p[1]) for p in data['asks']}
    
    async def update_data(self, event: asyncio.Event):
        count = 0
        async for websocket in connect(f'wss://stream.binance.com:9443/ws/{self.ws_symbol}@depth'):
            try:
                async for message in websocket:
                    self.apply_updated_data(json.loads(message))
                    count += 1
                    if count % 5 == 0:
                        event.set() 
            except Exception as e:
                print(f"error: {e}")
                
    def apply_updated_data(self, updated_data):
        updated_bids =  updated_data['b']
        updated_asks =  updated_data['a']
        for elements in updated_bids:
            bids_price = float(elements[0])
            bids_qty = float(elements[1])
            if bids_qty == 0.0:
                self.bids.pop(bids_price ,None)
            else:
                self.bids[bids_price] = bids_qty
        for elements in updated_asks:
            asks_price = float(elements[0])
            asks_qty = float(elements[1])
            if asks_qty == 0.0000000000000000000000:
                self.asks.pop(asks_price ,None)
            else:
                self.asks[asks_price] = asks_qty

    def top(self, n):
        top_bids = sorted(self.bids.items(), key=lambda x: x[0], reverse=True)[:n]
        top_asks = sorted(self.asks.items(), key=lambda x: x[0])[:n]
        return top_bids, top_asks

async def main():
    async with aiohttp.ClientSession() as session:
        result = OrderBook('BTCUSDT')
        await result.snapshot_data(session)  
        await result.update_data()  
        
        
        

if __name__ == '__main__':
    asyncio.run(main())
    
    
    


        

        
        
   

