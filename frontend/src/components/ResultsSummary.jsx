import { useMemo } from 'react';
import { Tag, Eye, Clock, TrendingUp, CheckCircle2, AlertTriangle } from 'lucide-react';

/**
 * Resumo executivo calculado exclusivamente a partir de uniqueDetections.
 * Nenhuma metrica inventada — somente dados reais da API.
 */
export default function ResultsSummary({ uniqueDetections, stats }) {
  const metrics = useMemo(() => {
    const total = uniqueDetections.length;
    if (total === 0) return { avgConf: 0, identified: 0, possible: 0, total: 0 };

    const identified = uniqueDetections.filter(
      (d) => d.status === 'Identificado'
    ).length;
    const possible = uniqueDetections.filter(
      (d) => d.status === 'Possível TAG' || d.status === 'Possivel TAG'
    ).length;
    const sum = uniqueDetections.reduce((acc, d) => acc + (d.confidence || 0), 0);

    return { total, identified, possible, avgConf: total > 0 ? sum / total : 0 };
  }, [uniqueDetections]);

  const confPct = Math.round(metrics.avgConf * 100);
  const confLevel = confPct >= 90 ? 'high' : confPct >= 70 ? 'medium' : 'low';
  const confLabel = { high: 'Alta', medium: 'Média', low: 'Baixa' }[confLevel];

  return (
    <div className="summary-grid" role="region" aria-label="Resumo Executivo da Análise">

      <div className="summary-card animate-fade-in-up" style={{ animationDelay: '0.04s' }}>
        <div className="summary-icon-wrap"><Tag size={18} aria-hidden="true" /></div>
        <div className="summary-data">
          <strong>{metrics.total}</strong>
          <span>TAGs únicas</span>
        </div>
      </div>

      <div className="summary-card summary-card--green animate-fade-in-up" style={{ animationDelay: '0.09s' }}>
        <div className="summary-icon-wrap green"><CheckCircle2 size={18} aria-hidden="true" /></div>
        <div className="summary-data">
          <strong>{metrics.identified}</strong>
          <span>Identificadas</span>
        </div>
      </div>

      <div className="summary-card summary-card--yellow animate-fade-in-up" style={{ animationDelay: '0.14s' }}>
        <div className="summary-icon-wrap yellow"><AlertTriangle size={18} aria-hidden="true" /></div>
        <div className="summary-data">
          <strong>{metrics.possible}</strong>
          <span>Possíveis TAGs</span>
        </div>
      </div>

      <div className="summary-card animate-fade-in-up" style={{ animationDelay: '0.19s' }}>
        <div className="summary-icon-wrap"><Eye size={18} aria-hidden="true" /></div>
        <div className="summary-data">
          <strong>{stats?.regions_sent_to_ocr ?? 0}</strong>
          <span>Regiões analisadas</span>
        </div>
      </div>

      <div className="summary-card animate-fade-in-up" style={{ animationDelay: '0.24s' }}>
        <div className="summary-icon-wrap"><Clock size={18} aria-hidden="true" /></div>
        <div className="summary-data">
          <strong>{stats?.processing_time_seconds ?? 0}s</strong>
          <span>Tempo de execução</span>
        </div>
      </div>

      <div className="summary-card animate-fade-in-up" style={{ animationDelay: '0.29s' }}>
        <div className={`summary-icon-wrap conf-${confLevel}`}>
          <TrendingUp size={18} aria-hidden="true" />
        </div>
        <div className="summary-data">
          <strong>{confPct}%</strong>
          <span>
            Confiança OCR média{' '}
            <em className={`conf-badge conf-badge--${confLevel}`}>{confLabel}</em>
          </span>
        </div>
      </div>

    </div>
  );
}
