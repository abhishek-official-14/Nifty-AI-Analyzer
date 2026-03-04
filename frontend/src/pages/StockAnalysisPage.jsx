import { useEffect, useState } from 'react';
import { fetchStockAnalysis } from '../api/client';
import Card from '../components/Card';

export default function StockAnalysisPage() {
  const [symbol, setSymbol] = useState('RELIANCE');
  const [data, setData] = useState(null);

  useEffect(() => {
    fetchStockAnalysis(symbol).then(setData);
  }, [symbol]);

  return (
    <div className="space-y-4">
      <Card title="Stock Analysis">
        <div className="flex flex-wrap items-center gap-3">
          <input
            className="rounded-md border border-slate-700 bg-slate-900 px-3 py-2"
            value={symbol}
            onChange={(e) => setSymbol(e.target.value.toUpperCase())}
          />
          <span className="text-slate-400">Type any symbol to fetch /api/stock-analysis/{'{symbol}'}</span>
        </div>
      </Card>
      {data && (
        <Card title={`${data.symbol} Snapshot`}>
          <p>LTP: {data.ltp}</p>
          <p>Trend: {data.trend}</p>
          <p>Recommendation: {data.recommendation}</p>
          <p>AI Confidence: {data.confidence}%</p>
          <ul className="mt-2 list-disc pl-5 text-slate-300">
            {data.technicals.map((item) => (
              <li key={item.metric}>
                {item.metric}: {item.value}
              </li>
            ))}
          </ul>
        </Card>
      )}
    </div>
  );
}
