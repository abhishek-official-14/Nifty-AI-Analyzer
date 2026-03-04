import { useEffect, useState } from 'react';
import { fetchSectorStrength } from '../api/client';
import BarChartWidget from '../components/BarChartWidget';
import Card from '../components/Card';

export default function SectorStrengthPage() {
  const [data, setData] = useState([]);

  useEffect(() => {
    fetchSectorStrength().then(setData);
  }, []);

  return (
    <Card title="Sector Strength Ranking">
      <BarChartWidget labels={data.map((d) => d.sector)} values={data.map((d) => d.score)} label="Strength" />
    </Card>
  );
}
