/**
 * Grafico de barras horizontais simples — 100% CSS/React, sem dependencias externas.
 * Recebe: title (string), data ([{label, value}]), colorMap ({label: hex}), defaultColor.
 */
export default function DistributionChart({ title, data = [], colorMap = {}, defaultColor = '#5d8cae' }) {
  const total = data.reduce((s, d) => s + d.value, 0);
  if (!data.length || total === 0) return null;

  return (
    <div className="dist-chart" role="region" aria-label={`Gr\u00e1fico: ${title}`}>
      <p className="dist-chart-title">{title}</p>
      <ul className="dist-chart-list" role="list">
        {data.map(({ label, value }, idx) => {
          const pct = Math.round((value / total) * 100);
          const color = colorMap[label] ?? defaultColor;
          return (
            <li
              key={label}
              className="dist-bar-row animate-fade-in-up"
              style={{ animationDelay: `${0.05 + idx * 0.06}s` }}
            >
              <span className="dist-bar-label" title={label}>{label}</span>
              <div
                className="dist-bar-track"
                role="progressbar"
                aria-valuenow={pct}
                aria-valuemin={0}
                aria-valuemax={100}
                aria-label={`${label}: ${value} (${pct}%)`}
              >
                <div
                  className="dist-bar-fill"
                  style={{ width: `${pct}%`, background: color }}
                />
              </div>
              <span className="dist-bar-count">{value}</span>
            </li>
          );
        })}
      </ul>
    </div>
  );
}
