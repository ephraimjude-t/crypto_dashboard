import { useState } from "react";

interface SelectorProps {
  onSelectChange: (ticker: string) => void;
}

function Selector({onSelectChange}: SelectorProps) {

    const tickers = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT']

    const [select, setSelect] = useState('BTCUSDT')
    const [isOpen, setIsOpen] = useState(false)

    const handleSelect = (ticker: string) =>{
        setSelect(ticker);
        setIsOpen(false);
        onSelectChange(ticker)      
    }

    return(
        <>
            <div className="relative inline-block text-left">
                <button onClick={() => setIsOpen(!isOpen)} className="inline-flex w-full justify-center gap-x-1.5 rounded-xl bg-transparent px-4 py-2 text-sm font-semibold text-[#64748B] dark:text-[#707A8A] shadow-sm hover:bg-slate-700 transition-colors">
                    {select}
                    <svg className="-mr-1 h-5 w-5 text-gray-400" viewBox="0 0 20 20" fill="currentColor">
                        <path fillRule="evenodd" d="M5.23 7.21a.75.75 0 011.06.02L10 11.168l3.71-3.938a.75.75 0 111.08 1.04l-4.25 4.5a.75.75 0 01-1.08 0l-4.25-4.5a.75.75 0 01.02-1.06z" clip-rule="evenodd" />
                    </svg>                 
                </button>
                {isOpen && (
                    <div  className="absolute left-0 z-10 mt-2 w-40 origin-top-left rounded-md bg-white shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none">
                        <div className="py-1">
                            {tickers.map((ticker) => (
                                <button key={ticker} onClick={()=> handleSelect(ticker)} className="block w-full px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-100 hover:text-gray-900">
                                {ticker}
                                </button>
                            ))}

                        </div>
                    </div>
                )}
            </div>
        </>
        
        
    )

}

export default Selector;