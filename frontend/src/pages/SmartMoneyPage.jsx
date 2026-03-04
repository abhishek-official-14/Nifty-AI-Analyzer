import { useEffect, useState } from 'react';
import { fetchSmartMoney } from '../api/client';
import Card from '../components/Card';

export default function SmartMoneyPage() {
  const [rows, setRows] = useState([]);

  useEffect(() => {
    fetchSmartMoney().then(setRows);
  }, []);

  return (
    <Card title="Smart Money Tracker">
      <div className="overflow-x-auto">
        <table className="min-w-full text-left text-sm">
          <thead className="text-slate-400">
            <tr>
              <th>Instrument</th>
              <th>Action</th>
              <th>Volume</th>
              <th>Conviction</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr key={row.instrument} className="border-t border-slate-800">
                <td className="py-2">{row.instrument}</td>
                <td>{row.action}</td>
                <td>{row.volume.toLocaleString()}</td>
                <td>{row.conviction}%</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Card>
  );
}
