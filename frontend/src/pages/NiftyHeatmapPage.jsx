import { useEffect, useState } from 'react';
import { fetchHeatmap } from '../api/client';
import Card from '../components/Card';
import DataState from '../components/DataState';

const colorMap = {
  Bullish: 'bg-emerald-500/20 border-emerald-500/50',
  Bearish: 'bg-red-500/20 border-red-500/50',
  Neutral: 'bg-yellow-500/20 border-yellow-500/50',
};

export default function NiftyHeatmapPage() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchHeatmap().then((res) => {
      setData(res);
      setLoading(false);
    });
  }, []);

  return (
    <DataState loading={loading}>
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {data.map((stock) => (
          <Card key={stock.symbol} className={`border ${colorMap[stock.bias]}`}>
            <p className="mb-2 text-lg font-semibold">{stock.symbol}</p>
            <p className="text-sm">Technical Score: {stock.technical}</p>
            <p className="text-sm">Options Score: {stock.options}</p>
            <p className="text-sm">Fundamental Score: {stock.fundamental}</p>
            <p className="text-sm">AI Confidence: {stock.confidence}%</p>
            <p className="mt-2 text-xs uppercase tracking-wider text-slate-300">{stock.bias}</p>
          </Card>
        ))}
      </div>
    </DataState>
  );
}
