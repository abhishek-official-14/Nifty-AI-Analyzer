export default function Card({ title, subtitle, children, className = '' }) {
  return (
    <section className={`rounded-xl border border-slate-800 bg-panel p-4 shadow-glow ${className}`}>
      {(title || subtitle) && (
        <header className="mb-3">
          {title && <h3 className="text-sm font-semibold uppercase tracking-wide text-sky-300">{title}</h3>}
          {subtitle && <p className="text-xs text-slate-400">{subtitle}</p>}
        </header>
      )}
      {children}
    </section>
  );
}
