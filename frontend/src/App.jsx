import { useState, useMemo, useEffect } from 'react';
import Header from './components/Header';
import Hero from './components/Hero';
import UploadArea from './components/UploadArea';
import ProcessingState from './components/ProcessingState';
import ResultsDashboard from './components/ResultsDashboard';
import { apiService } from './services/api';
import { getUniqueDetections, isValidImageFile } from './utils/formatters';

function App() {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [downloading, setDownloading] = useState(false);
  const [error, setError] = useState(null);

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
      if (data?.success) {
        setResult(data);
      } else {
        setError(data?.detail || 'Erro ao processar diagrama.');
      }
    } catch {
      setError('Falha na comunicação com o backend. Verifique se a API está em execução (porta 8000).');
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

        {!result && !loading && (
          <UploadArea
            file={file}
            preview={preview}
            onFileSelect={handleFileSelect}
            onProcess={handleProcessImage}
            onReset={handleReset}
            disabled={loading}
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
