import { NavLink } from 'react-router-dom';

const navItems = [
  ['/', 'Dashboard'],
  ['/nifty-overview', 'Nifty Overview'],
  ['/nifty-heatmap', 'Nifty 50 Heatmap'],
  ['/stock-analysis', 'Stock Analysis'],
  ['/options-chain', 'Option Chain Analyzer'],
  ['/sector-strength', 'Sector Strength'],
  ['/market-breadth', 'Market Breadth'],
  ['/fii-dii', 'FII/DII Tracker'],
  ['/smart-money', 'Smart Money Tracker'],
  ['/ai-signals', 'AI Signals'],
];

export default function AppLayout({ children }) {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 lg:flex">
      <aside className="border-b border-slate-800 bg-panel p-4 lg:min-h-screen lg:w-72 lg:border-b-0 lg:border-r">
        <h1 className="mb-5 text-xl font-bold text-sky-300">Nifty AI Analyzer Pro</h1>
        <nav className="grid grid-cols-2 gap-2 lg:grid-cols-1">
          {navItems.map(([to, label]) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) =>
                `rounded-lg px-3 py-2 text-sm transition ${
                  isActive ? 'bg-sky-500/20 text-sky-300' : 'text-slate-300 hover:bg-slate-800'
                }`
              }
            >
              {label}
            </NavLink>
          ))}
        </nav>
      </aside>
      <main className="flex-1 p-4 lg:p-6">{children}</main>
    </div>
  );
}
