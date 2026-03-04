import { createChart } from 'lightweight-charts';
import { useEffect, useRef } from 'react';

export default function TrendLightweightChart({ data = [], color = '#38bdf8' }) {
  const containerRef = useRef(null);

  useEffect(() => {
    if (!containerRef.current) return undefined;

    const chart = createChart(containerRef.current, {
      layout: { background: { color: '#0f172a' }, textColor: '#94a3b8' },
      grid: { vertLines: { color: '#1e293b' }, horzLines: { color: '#1e293b' } },
      width: containerRef.current.clientWidth,
      height: 280,
      timeScale: { borderColor: '#334155' },
      rightPriceScale: { borderColor: '#334155' },
    });

    const series = chart.addLineSeries({ color, lineWidth: 2 });
    series.setData(data);

    const handleResize = () => chart.applyOptions({ width: containerRef.current.clientWidth });
    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      chart.remove();
    };
  }, [data, color]);

  return <div ref={containerRef} className="w-full" />;
}
