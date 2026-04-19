import { useEffect, useState } from "react";

function ChangePercent({activeTicker}: {activeTicker:string}){

    const [change, setChange] = useState('loading...')

    useEffect(() => {
        const get_change = async () => {
            try{
                const req = await fetch(`http://127.0.0.1:8000/priceChange/${activeTicker}`)
                const res = await req.json()
                setChange(res.ChangePercent)
            }
            catch(err){
                console.error("Connection error:", err)
            }
        }
        get_change()
    },[activeTicker])
    
    return(
        <>
            <div className={
                Number(change) > 0 ? "text-green-500" :
                Number(change) < 0 ? "text-red-500" :
                "text-gray-500"
            }>
                {change}%
            </div>
        </>
        
    )
}
export default ChangePercent;

