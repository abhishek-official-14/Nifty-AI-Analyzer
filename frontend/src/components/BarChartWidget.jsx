import {
  BarElement,
  CategoryScale,
  Chart as ChartJS,
  Legend,
  LinearScale,
  Tooltip,
} from 'chart.js';
import { Bar } from 'react-chartjs-2';

ChartJS.register(CategoryScale, LinearScale, BarElement, Tooltip, Legend);

export default function BarChartWidget({ labels = [], values = [], label = 'Score' }) {
  return (
    <Bar
      data={{
        labels,
        datasets: [
          {
            label,
            data: values,
            backgroundColor: 'rgba(56, 189, 248, 0.7)',
            borderRadius: 8,
          },
        ],
      }}
      options={{
        responsive: true,
        plugins: { legend: { labels: { color: '#cbd5e1' } } },
        scales: {
          x: { ticks: { color: '#94a3b8' }, grid: { color: '#1e293b' } },
          y: { ticks: { color: '#94a3b8' }, grid: { color: '#1e293b' } },
        },
      }}
    />
  );
}
