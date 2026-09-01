export default function MetricsBar({ tagsCount = 0, regionsCount = 0, processingTime = 0 }) {
  return (
    <div className="metrics-bar">
      <div className="metric-item">
        <strong>{tagsCount}</strong>
        <span>TAGs identificadas</span>
      </div>
      <div className="metric-item">
        <strong>{regionsCount}</strong>
        <span>Regiões analisadas</span>
      </div>
      <div className="metric-item">
        <strong>{processingTime}s</strong>
        <span>Tempo de processamento</span>
      </div>
    </div>
  );
}
