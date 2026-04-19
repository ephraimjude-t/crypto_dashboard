import asyncio
import json
from websockets.asyncio.client import connect

async def consume():
    i = 0
    async for websocket in connect('wss://stream.binance.com:9443/ws/btcusdt@trade'):
        try:
            async for message in websocket:
                i+=1
                data = json.loads(message)
                price = data['p']
                quantity = data['q']
                is_marketMaker = data['m']
                side = "SELL" if is_marketMaker else "BUY"
                print(f'BTCUSDT, Price[{price}], quantity[{quantity}], signal[{side}], count=[{i}]')

        except Exception as e:
            print(f"connection lost {e}")

async def main():
    try:
        await asyncio.wait_for(consume(), timeout=15)
    except asyncio.TimeoutError:
        print(f"done")

if __name__ == "__main__":
    asyncio.run(main())

    




