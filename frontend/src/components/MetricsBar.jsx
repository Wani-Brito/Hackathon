import { Tag, Eye, Clock } from 'lucide-react';

export default function MetricsBar({ tagsCount = 0, regionsCount = 0, processingTime = 0 }) {
  return (
    <div className="metrics-bar" role="region" aria-label="Métricas da Análise">
      <div className="metric-item">
        <div className="metric-icon-wrap">
          <Tag size={18} aria-hidden="true" />
        </div>
        <div className="metric-data">
          <strong>{tagsCount}</strong>
          <span>TAGs Únicas</span>
        </div>
      </div>

      <div className="metric-item">
        <div className="metric-icon-wrap">
          <Eye size={18} aria-hidden="true" />
        </div>
        <div className="metric-data">
          <strong>{regionsCount}</strong>
          <span>Regiões Inspecionadas</span>
        </div>
      </div>

      <div className="metric-item">
        <div className="metric-icon-wrap">
          <Clock size={18} aria-hidden="true" />
        </div>
        <div className="metric-data">
          <strong>{processingTime}s</strong>
          <span>Tempo de Execução</span>
        </div>
      </div>
    </div>
  );
}
