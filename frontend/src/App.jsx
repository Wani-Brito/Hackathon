import { useState, useMemo, useEffect } from 'react';
import Header from './components/Header';
import Hero from './components/Hero';
import UploadArea from './components/UploadArea';
import ProcessingState from './components/ProcessingState';
import ResultsDashboard from './components/ResultsDashboard';
import ModelEvaluationPanel from './components/ModelEvaluationPanel';
import { apiService } from './services/api';
import { getUniqueDetections, isValidImageFile } from './utils/formatters';

function App() {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [downloading, setDownloading] = useState(false);
  const [error, setError] = useState(null);
  const [apiOnline, setApiOnline] = useState(null);
  const [apiChecking, setApiChecking] = useState(true);
  const [evaluationMetrics, setEvaluationMetrics] = useState(null);
  const [evaluationLoading, setEvaluationLoading] = useState(true);
  const [evaluationError, setEvaluationError] = useState(null);

  const checkInitialApiHealth = async () => {
    try {
      await apiService.checkHealth();
      setApiOnline(true);
    } catch {
      setApiOnline(false);
    } finally {
      setApiChecking(false);
    }
  };

  const loadEvaluationMetrics = async () => {
    setEvaluationLoading(true);
    try {
      const data = await apiService.getEvaluationMetrics();
      setEvaluationMetrics(data);
      setEvaluationError(null);
    } catch {
      setEvaluationMetrics(null);
      setEvaluationError('As métricas de avaliação não puderam ser carregadas porque a API está indisponível no momento.');
    } finally {
      setEvaluationLoading(false);
    }
  };

  const handleRetryApi = () => {
    setApiChecking(true);
    checkInitialApiHealth();
    loadEvaluationMetrics();
  };

  const handleFileSelect = (selectedFile) => {
    if (!selectedFile) return;

    if (!isValidImageFile(selectedFile)) {
      setError('Formato de arquivo não suportado. Por favor, utilize uma imagem JPG ou PNG.');
      return;
    }

    setFile(selectedFile);
    setPreview(URL.createObjectURL(selectedFile));
    setResult(null);
    setError(null);
  };

  const handleReset = () => {
    if (preview) {
      URL.revokeObjectURL(preview);
    }
    setFile(null);
    setPreview(null);
    setResult(null);
    setError(null);

    // Scroll suave para a area de upload
    const target = document.getElementById('analise');
    if (target) {
      target.scrollIntoView({ behavior: 'smooth' });
    }
  };

  const handleProcessImage = async () => {
    if (!file) return;
    setLoading(true);
    setError(null);

    try {
      const data = await apiService.processImage(file);
      setApiOnline(true);
      if (data?.success) {
        setResult(data);
      } else {
        setError(data?.detail || 'Erro ao processar diagrama.');
      }
    } catch {
      setApiOnline(false);
      setError('A análise está temporariamente indisponível. Verifique a API e tente novamente.');
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadReport = async () => {
    if (!result?.report_id) return;
    setDownloading(true);
    setError(null);

    try {
      const pdfBlob = await apiService.downloadReport(result.report_id);
      const url = URL.createObjectURL(new Blob([pdfBlob], { type: 'application/pdf' }));
      const link = document.createElement('a');
      link.href = url;
      link.download = `relatorio_tagvision_${result.report_id.slice(0, 8)}.pdf`;
      document.body.appendChild(link);
      link.click();
      link.remove();
      URL.revokeObjectURL(url);
    } catch {
      setError('Não foi possível gerar o relatório PDF. Tente novamente em instantes.');
    } finally {
      setDownloading(false);
    }
  };

  const uniqueDetections = useMemo(() => {
    return getUniqueDetections(result?.detections);
  }, [result?.detections]);

  // Scroll suave para os resultados ao concluir analise
  useEffect(() => {
    if (result) {
      const target = document.getElementById('analise');
      if (target) {
        target.scrollIntoView({ behavior: 'smooth' });
      }
    }
  }, [result]);

  useEffect(() => {
    let active = true;

    async function loadInitialEvaluationMetrics() {
      try {
        const data = await apiService.getEvaluationMetrics();
        if (active) {
          setEvaluationMetrics(data);
          setEvaluationError(null);
        }
      } catch {
        if (active) {
          setEvaluationError('Não foi possível carregar as métricas reais da avaliação.');
        }
      } finally {
        if (active) {
          setEvaluationLoading(false);
        }
      }
    }

    window.setTimeout(() => {
      checkInitialApiHealth();
      loadInitialEvaluationMetrics();
    }, 0);

    return () => {
      active = false;
    };
  }, []);

  return (
    <div className="app-shell">
      <div className="tech-grid" aria-hidden="true" />
      <Header />
      <Hero />

      <main className="analysis-section" id="analise" tabIndex={-1}>
        <div className="section-heading">
          <div className="eyebrow">
            <span className="eyebrow-line" />
            <span>Módulo de Extração</span>
          </div>
          <h2>Análise de Planta P&amp;ID</h2>
          <p>
            Envie seu diagrama técnico para identificação e classificação de equipamentos conforme normas de instrumentação.
          </p>
        </div>

        {apiOnline === false && (
          <div className="api-offline-banner" role="status">
            <div className="offline-copy">
              <strong>Análise temporariamente indisponível</strong>
              <span>O backend não respondeu agora. A navegação e o painel institucional continuam disponíveis.</span>
            </div>
            <button
              type="button"
              className="secondary-button retry-button"
              onClick={handleRetryApi}
              disabled={apiChecking || evaluationLoading}
            >
              {apiChecking ? 'Verificando...' : 'Tentar novamente'}
            </button>
          </div>
        )}

        {!result && !loading && (
          <UploadArea
            file={file}
            preview={preview}
            onFileSelect={handleFileSelect}
            onProcess={handleProcessImage}
            onReset={handleReset}
            disabled={loading || apiOnline === false}
          />
        )}

        {loading && <ProcessingState />}

        {error && (
          <div className="error-message" role="alert">
            <strong>Atenção:</strong> {error}
          </div>
        )}

        {result && (
          <ResultsDashboard
            result={result}
            uniqueDetections={uniqueDetections}
            onReset={handleReset}
            onDownloadReport={handleDownloadReport}
            downloading={downloading}
          />
        )}
      </main>

      <ModelEvaluationPanel
        metrics={evaluationMetrics}
        loading={evaluationLoading}
        error={evaluationError}
        onRetry={handleRetryApi}
      />

      <footer id="sobre" role="contentinfo">
        <div className="footer-content">
          <div className="footer-brand">
            <img src="/iastech-logo.png" alt="IASTECH" />
            <span>TAGVision P&amp;ID · Soluções em automação industrial</span>
          </div>
          <div className="footer-links">
            <span>Tecnologia de Reconhecimento Óptico de Diagramas Industriais</span>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;
