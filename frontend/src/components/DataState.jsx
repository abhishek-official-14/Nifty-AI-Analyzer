export default function DataState({ loading, error, children }) {
  if (loading) return <div className="rounded-xl border border-slate-800 bg-panel p-6 text-slate-400">Loading...</div>;
  if (error)
    return <div className="rounded-xl border border-red-500/30 bg-red-500/10 p-6 text-red-300">{error}</div>;
  return children;
}
