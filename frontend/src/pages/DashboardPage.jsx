import { useEffect, useMemo, useState } from 'react';
import {
  fetchAiSignals,
  fetchFiiDii,
  fetchLiquidityHeatmap,
  fetchMarketBreadth,
  fetchNiftyOverview,
  fetchOptionsChain,
  fetchSectorStrength,
  fetchSmartMoney,
} from '../api/client';
import BarChartWidget from '../components/BarChartWidget';
import Card from '../components/Card';
import DataState from '../components/DataState';
import MetricPill from '../components/MetricPill';
import TrendLightweightChart from '../components/TrendLightweightChart';

export default function DashboardPage() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      fetchNiftyOverview(),
      fetchSectorStrength(),
      fetchMarketBreadth(),
      fetchOptionsChain(),
      fetchAiSignals(),
      fetchFiiDii(),
      fetchSmartMoney(),
      fetchLiquidityHeatmap(),
    ]).then(([overview, sectorStrength, breadth, options, aiSignals, fiiDii, smartMoney, liquidity]) => {
      setData({ overview, sectorStrength, breadth, options, aiSignals, fiiDii, smartMoney, liquidity });
      setLoading(false);
    });
  }, []);

  const fiiLatest = useMemo(() => data?.fiiDii?.history?.at(-1), [data]);

  return (
    <DataState loading={loading}>
      {data && (
        <div className="space-y-4">
          <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-5">
            <MetricPill label="Nifty" value={data.overview.nifty.value.toFixed(2)} trend="positive" />
            <MetricPill label="Market Breadth" value={`${data.breadth.advances}:${data.breadth.declines}`} trend="positive" />
            <MetricPill label="PCR / Max Pain" value={`${data.options.pcr} / ${data.options.maxPain}`} trend="neutral" />
            <MetricPill label="AI Sentiment" value={data.overview.aiSentiment} trend="positive" />
            <MetricPill label="FII Net Flow" value={fiiLatest?.fii ?? 0} trend={fiiLatest?.fii > 0 ? 'positive' : 'negative'} />
          </div>

          <div className="grid gap-4 xl:grid-cols-3">
            <Card title="Nifty Trend Chart" className="xl:col-span-2">
              <TrendLightweightChart data={data.overview.trend} />
            </Card>
            <Card title="Sector Ranking">
              <BarChartWidget
                labels={data.sectorStrength.map((s) => s.sector)}
                values={data.sectorStrength.map((s) => s.score)}
              />
            </Card>
          </div>

          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
            <Card title="Top Gainers / Losers">
              {[...data.overview.topGainers, ...data.overview.topLosers].map((s) => (
                <div key={s.symbol} className="mb-2 flex justify-between text-sm">
                  <span>{s.symbol}</span>
                  <span className={s.change > 0 ? 'text-emerald-300' : 'text-red-300'}>{s.change}%</span>
                </div>
              ))}
            </Card>
            <Card title="Smart Money Activity">
              {data.smartMoney.map((s) => (
                <div key={s.instrument} className="mb-2 text-sm">
                  <p className="font-medium">{s.instrument}</p>
                  <p className="text-slate-400">{s.action} · Conviction {s.conviction}%</p>
                </div>
              ))}
            </Card>
            <Card title="Volume Spikes / Liquidity">
              {data.liquidity.map((l) => (
                <div key={l.zone} className="mb-2 flex justify-between text-sm">
                  <span>{l.zone}</span>
                  <span>{l.intensity}%</span>
                </div>
              ))}
            </Card>
          </div>
        </div>
      )}
    </DataState>
  );
}
