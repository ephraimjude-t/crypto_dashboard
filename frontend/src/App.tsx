import { useState, useEffect } from "react"
import Selector from './components/tickerSelector.tsx'
import ThemeToggle from "./components/SwitchTheme.tsx";
import Chart from "./components/TradingChart.tsx";
import ChangePercent from "./components/ChangePercent.tsx";
import OrderBook from "./components/OrderBook.tsx";

function App() {

  const [activeTicker, setActiveTicker] = useState('BTCUSDT');
  const [price, setprice] = useState("Loading...")

  useEffect(() => {
    const price = async () => {
      try{
        const req = await fetch(`http://localhost:8000/price/${activeTicker}`)
        const res = await req.json()
        setprice(res.price);        
      }
      catch(err){
        console.error("Connection error:", err);
      }
    }
    price();
  },[activeTicker])
  
  return (
    <>
      <div className="bg-[#F8FAFC] dark:bg-[#0B0E11] absolute w-full min-h-screen  overflow-x-hidden">
        <div className="relative top-[3vh] left-[95vw]">
          <ThemeToggle />
        </div>  
        <div className="px-8 relative top-[9vh]">
          <Selector onSelectChange={(ticker) => setActiveTicker(ticker)} />
        </div>
        <div className="text-[#1E293B] dark:text-[#EAECEF] font-bold relative top-[9vh] px-8">
            ${price}
            <div>
              <ChangePercent activeTicker={activeTicker} />
            </div>
        </div>
        <div className=" w-full h-screen grid grid-cols-12 grid-rows-12 gap-5 px-6">
          <div className="bg-[#E1E1E1] dark:bg-[#151921] row-start-2 col-span-9 row-span-7 rounded-[25px] overflow-hidden relative">
            <Chart activeTicker={activeTicker}/>
          </div>
          <div className="bg-[#E1E1E1] dark:bg-[#151921] row-start-2 col-start-10 col-span-3 row-span-7 rounded-[25px]">
            <OrderBook symbol={activeTicker}/>
          </div>
        </div>
      </div>
    </>
    
  )
}

export default App
