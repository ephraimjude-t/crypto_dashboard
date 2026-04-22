import { useEffect, useRef} from 'react';
import { createChart, AreaSeries, CandlestickSeries, ColorType } from 'lightweight-charts';
import type { IChartApi, Time } from 'lightweight-charts'

interface RawCandle {
  time: number;
  open: number;
  high: number;
  low: number;
  close: number;
}

interface ChartCandle {
  time: Time;
  open: number;
  high: number;
  low: number;
  close: number;
}
interface AreaData {
  time: Time;
  value: number;
}



function Chart({activeTicker}: {activeTicker:string}) {
    const containerRef = useRef<HTMLDivElement>(null);
    const chartRef = useRef<IChartApi | null>(null);

    useEffect(() => {

        if (!containerRef.current) return;
        
        const chart = createChart(containerRef.current, {
            width: containerRef.current.clientWidth,
            height: containerRef.current.clientHeight,
            layout: {
                textColor:'white',
                background:{
                    type:ColorType.Solid,
                    color:'rgba(0, 0, 0, 0)'
                    
                }
            }
        })
        

        chartRef.current = chart;
       
        const areaSeries = chart.addSeries(AreaSeries,{
            lineColor: '#2962FF', topColor: '#2962FF', bottomColor: 'rgba(41, 98, 255, 0.28)',
        });
        const candlestickSeries = chart.addSeries(CandlestickSeries, {
                upColor: '#26a69a', downColor: '#ef5350', borderVisible: false,
                wickUpColor: '#26a69a', wickDownColor: '#ef5350',
            }
        )
    

        const get_data = async () => {
            try{
                const req = await fetch(`http://127.0.0.1:8000/candles/${activeTicker}`)
                const res = await req.json() as RawCandle[]
                const candleStickData: ChartCandle[]  = res.map(item => ({
                    time: item.time as Time, 
                    open: item.open,
                    close: item.close,
                    low: item.low,
                    high: item.high,
                })).sort((a, b)=> (a.time as number) - (b.time as number));
                candlestickSeries.setData(candleStickData)
                
                const areaSeriesData: AreaData[] = res.map(item =>({
                    time: item.time as Time,
                    value: item.close
                })).sort((a,b)=> (a.time as number) - (b.time as number))
                areaSeries.setData(areaSeriesData)

                chart.timeScale().fitContent();
                
                
            }
            catch(err){
                console.error("Connection error:", err);
            }
            
        }
        get_data()



        const handleResize = () => {
            if (containerRef.current && chartRef.current) {
                chartRef.current.applyOptions({
                    width: containerRef.current.clientWidth,
                    height: containerRef.current.clientHeight,
                })
            }
        }
        window.addEventListener('resize', handleResize);


        return() => {
            window.removeEventListener('resize', handleResize);
            if (chartRef.current) {
                chartRef.current.remove()
                chartRef.current = null
            }

        }


    },[activeTicker])

    useEffect(() => {
        if (!chartRef.current) return;

        const syncTheme = () => {
            const isDarkSystem = document.documentElement.classList.contains('dark');

            chartRef.current?.applyOptions({
                layout: {
                    textColor: isDarkSystem ? '#f3f4f6' : '#1f2937',
                },
                grid: {
                    vertLines: { color: isDarkSystem ? '#374151' : '#f3f4f6' },
                    horzLines: { color: isDarkSystem ? '#374151' : '#f3f4f6' },
                }
            })

        }
        syncTheme();

        const observer = new MutationObserver(syncTheme);
        observer.observe(document.documentElement, {
            attributes: true,
            attributeFilter: ['class'],
        });

        return () => observer.disconnect();

    },[])
    

    
   

    return(
        <>
            <div ref={containerRef} className='w-full h-full'>

            </div>
        </>
    )


}

export default Chart;
