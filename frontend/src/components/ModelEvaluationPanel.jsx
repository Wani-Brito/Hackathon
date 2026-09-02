import { AlertTriangle, BarChart3, CheckCircle2, Database, Target } from 'lucide-react';

function formatPercent(value) {
  if (typeof value !== 'number') return '-';
  return `${(value * 100).toFixed(1)}%`;
}

function formatF1(value) {
  if (typeof value !== 'number') return '-';
  return value.toFixed(4);
}

function getMatrixColumns(confusionMatrix) {
  if (!Array.isArray(confusionMatrix) || confusionMatrix.length === 0) return [];
  return Object.keys(confusionMatrix[0]).filter((key) => key !== 'actual');
}

export default function ModelEvaluationPanel({ metrics, loading, error, onRetry }) {
  const globalMetrics = metrics?.global_metrics || {};
  const confusionMatrix = metrics?.confusion_matrix || [];
  const matrixColumns = getMatrixColumns(confusionMatrix);

  return (
    <section
      className="model-evaluation-section"
      id="avaliacao-modelo"
      tabIndex={-1}
      aria-label="Avaliação do Modelo"
    >
      <div className="section-heading evaluation-heading">
        <div className="eyebrow">
          <span className="eyebrow-line" />
          <span>Avaliação Validada</span>
        </div>
        <h2>Avaliação do Modelo</h2>
        <p>
          Métricas calculadas a partir de uma amostra validada manualmente. Estes números não
          representam a imagem enviada na análise atual.
        </p>
      </div>

      {loading && (
        <div className="evaluation-panel">
          <div className="evaluation-state">
            <BarChart3 size={18} aria-hidden="true" />
            <span>Carregando métricas reais da avaliação...</span>
          </div>
        </div>
      )}

      {!loading && error && (
        <div className="evaluation-panel evaluation-error" role="alert">
          <AlertTriangle size={18} aria-hidden="true" />
          <div className="offline-copy">
            <strong>Avaliação temporariamente indisponível</strong>
            <span>{error}</span>
          </div>
          <button type="button" className="secondary-button retry-button" onClick={onRetry}>
            Tentar novamente
          </button>
        </div>
      )}

      {!loading && !error && metrics && (
        <div className="evaluation-panel animate-fade-in-up">
          <div className="evaluation-source-note">
            <Database size={16} aria-hidden="true" />
            <span>
              Fonte: metrics_summary.json e confusion_matrix_status.csv. Amostra manual:
              {' '}
              {metrics.total_images_evaluated} imagens, {metrics.total_ground_truth_tags} TAGs de referência.
            </span>
          </div>

          <div className="evaluation-metrics-grid">
            <div className="evaluation-metric-card">
              <span>Precision</span>
              <strong>{formatPercent(globalMetrics.precision)}</strong>
            </div>
            <div className="evaluation-metric-card">
              <span>Recall</span>
              <strong>{formatPercent(globalMetrics.recall)}</strong>
            </div>
            <div className="evaluation-metric-card">
              <span>F1-Score</span>
              <strong>{formatF1(globalMetrics.f1_score)}</strong>
            </div>
            <div className="evaluation-metric-card">
              <span>Imagens avaliadas</span>
              <strong>{metrics.total_images_evaluated}</strong>
            </div>
            <div className="evaluation-metric-card">
              <span>TAGs de referência</span>
              <strong>{metrics.total_ground_truth_tags}</strong>
            </div>
          </div>

          <div className="evaluation-counts-row" aria-label="Contagens globais">
            <div>
              <CheckCircle2 size={15} aria-hidden="true" />
              <span>TP</span>
              <strong>{globalMetrics.tp ?? '-'}</strong>
            </div>
            <div>
              <Target size={15} aria-hidden="true" />
              <span>FP</span>
              <strong>{globalMetrics.fp ?? '-'}</strong>
            </div>
            <div>
              <Target size={15} aria-hidden="true" />
              <span>FN</span>
              <strong>{globalMetrics.fn ?? '-'}</strong>
            </div>
          </div>

          <div className="confusion-matrix-block">
            <div className="confusion-matrix-header">
              <h3>Matriz de Confusão</h3>
              <p>Linhas: status real. Colunas: status previsto.</p>
            </div>

            <div className="confusion-matrix-scroll">
              <table className="confusion-matrix-table">
                <thead>
                  <tr>
                    <th scope="col">Real \ Previsto</th>
                    {matrixColumns.map((column) => (
                      <th key={column} scope="col">{column}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {confusionMatrix.map((row) => (
                    <tr key={row.actual}>
                      <th scope="row">{row.actual}</th>
                      {matrixColumns.map((column) => (
                        <td key={`${row.actual}-${column}`}>{row[column]}</td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </section>
  );
}
