import aiohttp
import asyncio
import time

tickers = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'BNBUSDT']

async def fetch_price(session, ticker):
    url = f"https://api.binance.com/api/v3/ticker/price?symbol={ticker}"
    async with session.get(url) as response:
        data = await response.json()
        return data

async def main():
    start = time.time()
    async with aiohttp.ClientSession() as session:
        db = []
        result = await asyncio.gather(*[fetch_price(session, ticker) for ticker in tickers])   
        print(result)
    end = time.time()
    print(f"total:{end-start:.3f}s")

    


asyncio.run(main())


    


