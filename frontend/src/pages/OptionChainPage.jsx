import { useEffect, useState } from 'react';
import { fetchOptionsChain } from '../api/client';
import Card from '../components/Card';
import MetricPill from '../components/MetricPill';

export default function OptionChainPage() {
  const [data, setData] = useState(null);

  useEffect(() => {
    fetchOptionsChain().then(setData);
  }, []);

  if (!data) return null;

  return (
    <Card title="Option Chain Analyzer" subtitle="PCR, OI imbalance, and Max Pain">
      <div className="grid gap-3 md:grid-cols-4">
        <MetricPill label="PCR" value={data.pcr} trend="neutral" />
        <MetricPill label="Max Pain" value={data.maxPain} trend="neutral" />
        <MetricPill label="Call OI (Cr)" value={data.callOI} trend="negative" />
        <MetricPill label="Put OI (Cr)" value={data.putOI} trend="positive" />
      </div>
    </Card>
  );
}
