import { Download, RefreshCcw, CheckCircle, FileText } from 'lucide-react';
import MetricsBar from './MetricsBar';
import ResultImage from './ResultImage';
import DetectionList from './DetectionList';
import { apiService } from '../services/api';

export default function ResultsDashboard({
  result,
  uniqueDetections,
  onReset,
  onDownloadReport,
  downloading,
}) {
  const imageUrl = apiService.getImageUrl(result.processed_image_url);

  return (
    <div className="results-panel animate-fade-in-up" role="region" aria-label="Painel de Resultados da Análise">
      <div className="results-header">
        <div className="results-title-group">
          <div className="results-status-badge">
            <CheckCircle size={14} aria-hidden="true" />
            <span>ANÁLISE CONCLUÍDA</span>
          </div>
          <h2>Resultados da Planta Técnica</h2>
          <p className="results-subtitle">
            Arquivo analisado: <strong className="file-highlight">{result.original_image}</strong>
          </p>
        </div>

        <div className="result-actions">
          <button
            type="button"
            className="primary-button new-analysis-btn"
            onClick={onReset}
          >
            <RefreshCcw size={15} aria-hidden="true" />
            <span>Nova Análise</span>
          </button>

          <button
            type="button"
            className="secondary-button download-pdf-btn"
            onClick={onDownloadReport}
            disabled={downloading}
          >
            <FileText size={15} aria-hidden="true" />
            <span>{downloading ? 'Gerando Relatório...' : 'Baixar Relatório PDF'}</span>
            <Download size={14} className="download-icon" aria-hidden="true" />
          </button>
        </div>
      </div>

      <MetricsBar
        tagsCount={uniqueDetections.length}
        regionsCount={result.stats?.regions_sent_to_ocr ?? 0}
        processingTime={result.stats?.processing_time_seconds ?? 0}
      />

      <div className="results-content-layout">
        <ResultImage imageUrl={imageUrl} alt={`Planta P&ID ${result.original_image}`} />
        <DetectionList detections={uniqueDetections} />
      </div>
    </div>
  );
}
