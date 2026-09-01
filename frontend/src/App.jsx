import { useState, useMemo } from 'react';
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
      setError('Formato de arquivo inválido. Por favor, envie uma imagem nos formatos JPG ou PNG.');
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
        setError(data?.detail || 'Erro ao processar imagem.');
      }
    } catch {
      setError('Não foi possível processar a planta. Confirme se o backend está em execução.');
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
      setError('Não foi possível gerar o PDF. Tente novamente em alguns instantes.');
    } finally {
      setDownloading(false);
    }
  };

  const uniqueDetections = useMemo(() => {
    return getUniqueDetections(result?.detections);
  }, [result?.detections]);

  return (
    <main className="app-shell">
      <div className="tech-grid" aria-hidden="true" />
      <Header />
      <Hero />

      <section className="analysis-section" id="analise">
        <div className="section-heading">
          <p className="eyebrow"><span /> Plataforma TAGVision</p>
          <h2>Analise sua planta</h2>
          <p>Envie um diagrama industrial P&amp;ID e receba a identificação estruturada das TAGs.</p>
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
            <p>{error}</p>
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
      </section>

      <footer id="sobre">
        <img src="/iastech-logo.png" alt="IASTECH" />
        <span>TAGVision P&amp;ID · Soluções em automação industrial</span>
      </footer>
    </main>
  );
}

export default App;
