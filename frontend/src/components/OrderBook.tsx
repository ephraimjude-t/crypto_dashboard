import { useEffect, useState } from "react";

interface Order {
    price: number;
    quantity: number;
}

interface OrderBookData {
    symbol: string;
    bids: Order[];
    asks: Order[];
}

function OrderBook({symbol}: {symbol:string}){
    const [data, setData] = useState<OrderBookData>({
        symbol:"",
        bids:[],
        asks:[]
    })
    const [connected, setConnected] = useState(false)

    useEffect(() =>{
        const socket = new WebSocket(`ws://localhost:8000/ws/orderbook/${symbol}`)

        socket.onopen = () => setConnected(true)

        socket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            setData(data)

        }

        socket.onclose = () => setConnected(false)

        return () => socket.close();
    },[symbol])


    

    return (
        <div className="bg-[#E1E1E1] dark:bg-[#151921] text-[#1E293B] dark:text-[#EAECEF] p-[20px]">
            <h3>{data.symbol || "Loading..."} Order Book</h3>
            <div style={{ fontSize: '0.8rem', color: connected ? '#4caf50' : '#f44336' }}>
                {connected ? "● Live" : "○ Disconnected"}
            </div>

            <div style={{ marginTop: '20px' }}>
              
                <div className="asks-section">
                    {data.asks.slice().reverse().map((ask, i) => (
                        <div key={i} style={{ display: 'flex', justifyContent: 'space-between', color: '#ff4d4d' }}>
                            <span>{ask.price.toFixed(2)}</span>
                            <span>{ask.quantity.toFixed(4)}</span>
                        </div>
                    ))}
                </div>

                <div style={{ textAlign: 'center', margin: '10px 0', borderTop: '1px solid #333', borderBottom: '1px solid #333', padding: '5px' }}>
                    <strong>{data.bids[0]?.price || '---'}</strong>
                </div>

                <div className="bids-section">
                    {data.bids.map((bid, i) => (
                        <div key={i} style={{ display: 'flex', justifyContent: 'space-between', color: '#00ff7f' }}>
                            <span>{bid.price.toFixed(2)}</span>
                            <span>{bid.quantity.toFixed(4)}</span>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );

}
export default OrderBook;