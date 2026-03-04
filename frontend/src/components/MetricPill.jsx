export default function MetricPill({ label, value, trend = 'neutral' }) {
  const tone = {
    positive: 'text-emerald-300 bg-emerald-500/10',
    negative: 'text-red-300 bg-red-500/10',
    neutral: 'text-yellow-300 bg-yellow-500/10',
  }[trend];

  return (
    <div className={`rounded-lg px-3 py-2 ${tone}`}>
      <div className="text-xs uppercase text-slate-400">{label}</div>
      <div className="text-lg font-semibold">{value}</div>
    </div>
  );
}
