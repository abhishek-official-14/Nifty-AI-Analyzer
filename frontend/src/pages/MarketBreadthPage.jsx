import { ArcElement, Chart as ChartJS, Legend, Tooltip } from 'chart.js';
import { useEffect, useState } from 'react';
import { Doughnut } from 'react-chartjs-2';
import { fetchMarketBreadth } from '../api/client';
import Card from '../components/Card';

ChartJS.register(ArcElement, Tooltip, Legend);

export default function MarketBreadthPage() {
  const [data, setData] = useState(null);

  useEffect(() => {
    fetchMarketBreadth().then(setData);
  }, []);

  if (!data) return null;

  return (
    <Card title="Market Breadth">
      <div className="mx-auto max-w-sm">
        <Doughnut
          data={{
            labels: ['Advances', 'Declines', 'Unchanged'],
            datasets: [{ data: [data.advances, data.declines, data.unchanged], backgroundColor: ['#22c55e', '#ef4444', '#eab308'] }],
          }}
        />
      </div>
      <p className="mt-3 text-center text-slate-300">Advance/Decline Ratio: {data.ratio}</p>
    </Card>
  );
}
