import { Download, RefreshCcw } from 'lucide-react';
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
    <div className="results-panel">
      <div className="results-header">
        <div>
          <p className="eyebrow"><span /> Análise concluída</p>
          <h2>Resultados da planta</h2>
        </div>
        <div className="result-actions">
          <button
            type="button"
            className="secondary-button reset-button"
            onClick={onReset}
          >
            <RefreshCcw size={16} /> Nova análise
          </button>
          <button
            type="button"
            className="primary-button download-button"
            onClick={onDownloadReport}
            disabled={downloading}
          >
            {downloading ? 'Gerando PDF...' : 'Baixar relatório PDF'} <Download size={16} />
          </button>
        </div>
      </div>

      <MetricsBar
        tagsCount={uniqueDetections.length}
        regionsCount={result.stats?.regions_sent_to_ocr ?? 0}
        processingTime={result.stats?.processing_time_seconds ?? 0}
      />

      <div className="results-content-layout">
        <ResultImage imageUrl={imageUrl} alt={result.original_image || 'Planta P&ID'} />
        <DetectionList detections={uniqueDetections} />
      </div>
    </div>
  );
}
