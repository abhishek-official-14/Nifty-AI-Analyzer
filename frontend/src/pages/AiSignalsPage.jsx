import { useEffect, useState } from 'react';
import { fetchAiSignals } from '../api/client';
import Card from '../components/Card';

export default function AiSignalsPage() {
  const [signals, setSignals] = useState([]);

  useEffect(() => {
    fetchAiSignals().then(setSignals);
  }, []);

  return (
    <Card title="AI Signals">
      <div className="grid gap-3 md:grid-cols-3">
        {signals.map((signal) => (
          <div key={signal.symbol} className="rounded-lg border border-slate-700 bg-slate-900 p-3">
            <p className="font-semibold">{signal.symbol}</p>
            <p className={signal.signal === 'BUY' ? 'text-emerald-300' : signal.signal === 'SELL' ? 'text-red-300' : 'text-yellow-300'}>
              {signal.signal}
            </p>
            <p className="text-sm text-slate-400">Confidence: {signal.confidence}%</p>
            <p className="text-sm text-slate-400">Horizon: {signal.horizon}</p>
          </div>
        ))}
      </div>
    </Card>
  );
}
