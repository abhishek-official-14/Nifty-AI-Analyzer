import {
  BarElement,
  CategoryScale,
  Chart as ChartJS,
  Legend,
  LinearScale,
  Tooltip,
} from 'chart.js';
import { useEffect, useState } from 'react';
import { Bar } from 'react-chartjs-2';
import { fetchFiiDii } from '../api/client';
import Card from '../components/Card';

ChartJS.register(CategoryScale, LinearScale, BarElement, Tooltip, Legend);

export default function FiiDiiPage() {
  const [data, setData] = useState([]);

  useEffect(() => {
    fetchFiiDii().then((res) => setData(res.history));
  }, []);

  return (
    <Card title="FII / DII Tracker">
      <Bar
        data={{
          labels: data.map((d) => d.date),
          datasets: [
            { label: 'FII', data: data.map((d) => d.fii), backgroundColor: 'rgba(56, 189, 248, 0.7)' },
            { label: 'DII', data: data.map((d) => d.dii), backgroundColor: 'rgba(34, 197, 94, 0.7)' },
          ],
        }}
      />
    </Card>
  );
}
