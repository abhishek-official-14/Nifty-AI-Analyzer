import { useEffect, useState } from 'react';
import { fetchNiftyOverview } from '../api/client';
import Card from '../components/Card';
import DataState from '../components/DataState';
import MetricPill from '../components/MetricPill';
import TrendLightweightChart from '../components/TrendLightweightChart';

export default function NiftyOverviewPage() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchNiftyOverview().then((res) => {
      setData(res);
      setLoading(false);
    });
  }, []);

  return (
    <DataState loading={loading}>
      {data && (
        <div className="space-y-4">
          <div className="grid gap-3 md:grid-cols-3">
            <MetricPill label="Index Value" value={data.nifty.value} trend="positive" />
            <MetricPill label="Day Change" value={`${data.nifty.change} (${data.nifty.changePercent}%)`} trend="positive" />
            <MetricPill label="AI Sentiment" value={data.aiSentiment} trend="positive" />
          </div>
          <Card title="Index Trend">
            <TrendLightweightChart data={data.trend} color="#22c55e" />
          </Card>
        </div>
      )}
    </DataState>
  );
}
