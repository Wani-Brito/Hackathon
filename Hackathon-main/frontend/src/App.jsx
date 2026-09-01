import { useState } from 'react';
import axios from 'axios';
import {
  CheckCircle2,
  ChevronRight,
  Download,
  FileImage,
  LoaderCircle,
  RefreshCcw,
  ScanLine,
  ShieldCheck,
  UploadCloud,
} from 'lucide-react';

const API_URL = 'http://localhost:8000';

function App() {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [downloading, setDownloading] = useState(false);
  const [error, setError] = useState(null);

  const handleFileChange = (event) => {
    const selectedFile = event.target.files?.[0];
    if (!selectedFile) return;
    setFile(selectedFile);
    setPreview(URL.createObjectURL(selectedFile));
    setResult(null);
    setError(null);
  };

  const resetAnalysis = () => {
    setFile(null);
    setPreview(null);
    setResult(null);
    setError(null);
  };

  const processImage = async () => {
    if (!file) return;
    setLoading(true);
    setError(null);
    const formData = new FormData();
    formData.append('file', file);
    try {
      const response = await axios.post(`${API_URL}/process-image`, formData);
      setResult(response.data);
    } catch {
      setError('Não foi possível processar a planta. Confirme se o backend está em execução.');
    } finally {
      setLoading(false);
    }
  };

  const downloadReport = async () => {
    if (!result?.report_id) return;
    setDownloading(true);
    setError(null);
    try {
      const response = await axios.get(`${API_URL}/download-report/${result.report_id}`, { responseType: 'blob' });
      const url = URL.createObjectURL(new Blob([response.data], { type: 'application/pdf' }));
      const link = document.createElement('a');
      link.href = url;
      link.download = 'relatorio_tagvision_pid.pdf';
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

  return (
    <main className="app-shell">
      <div className="tech-grid" aria-hidden="true" />
      <header className="topbar">
        <a className="brand" href="#inicio" aria-label="IASTECH">
          <img src="/iastech-logo.png" alt="IASTECH Industrial Automation" />
        </a>
        <nav className="nav-links" aria-label="Navegação principal">
          <a href="#inicio">Início</a>
          <a href="#analise">Análise P&amp;ID</a>
        </nav>
      </header>

      <section className="hero" id="inicio">
        <div className="hero-copy">
          <p className="eyebrow"><span /> Inteligência industrial</p>
          <h1>Precisão visual para <em>plantas industriais.</em></h1>
          <p className="hero-description">Utilize visão computacional para identificar TAGs e organizar informações essenciais dos seus diagramas P&amp;ID.</p>
          <div className="hero-points">
            <span><CheckCircle2 size={17} /> Leitura de TAGs</span>
            <span><CheckCircle2 size={17} /> Processamento seguro</span>
          </div>
        </div>
        <div className="hero-visual" aria-hidden="true">
          <div className="radar-ring ring-one" /><div className="radar-ring ring-two" />
          <div className="radar-core"><ScanLine size={42} /></div>
          <div className="floating-label label-top">OCR ATIVO</div>
          <div className="floating-label label-bottom">P&amp;ID SCAN</div>
        </div>
      </section>

      <section className="analysis-section" id="analise">
        <div className="section-heading">
          <p className="eyebrow"><span /> Plataforma TAGVision</p>
          <h2>Analise sua planta</h2>
          <p>Envie um diagrama e receba a identificação das TAGs encontradas.</p>
        </div>

        {!result && !loading && (
          <div className="upload-panel">
            <div className="upload-copy">
              <div className="step-number">01</div><h3>Enviar diagrama P&amp;ID</h3>
              <p>Formatos aceitos: JPG e PNG. Selecione o arquivo da planta que deseja analisar.</p>
              <div className="upload-note"><ShieldCheck size={18} /> Seu arquivo é utilizado somente durante a análise.</div>
            </div>
            <div className={`drop-zone ${preview ? 'has-preview' : ''}`}>
              {preview ? <><img src={preview} alt="Prévia da planta selecionada" /><div className="preview-footer"><FileImage size={17} /><span>{file?.name}</span></div></> : <><div className="upload-icon"><UploadCloud size={29} /></div><strong>Selecione o arquivo da planta</strong><span>ou arraste-o para esta área</span></>}
              <input id="plant-file" type="file" accept="image/jpeg,image/png" onChange={handleFileChange} />
              <label htmlFor="plant-file" className="secondary-button">{preview ? 'Trocar arquivo' : 'Selecionar arquivo'}</label>
            </div>
            <button type="button" className="primary-button process-button" onClick={processImage} disabled={!file}>Processar planta <ScanLine size={19} /></button>
          </div>
        )}

        {loading && <div className="status-panel"><LoaderCircle className="loader" size={42} /><p className="eyebrow"><span /> Processamento em andamento</p><h3>Analisando sua planta industrial</h3><p>Identificando regiões e TAGs técnicas. Isso pode levar alguns instantes.</p></div>}
        {error && <div className="error-message">{error}</div>}

        {result && (
          <div className="results-panel">
            <div className="results-header"><div><p className="eyebrow"><span /> Análise concluída</p><h2>Resultados da planta</h2></div><div className="result-actions"><button type="button" className="primary-button download-button" onClick={downloadReport} disabled={downloading}>{downloading ? 'Gerando PDF...' : 'Baixar relatório PDF'} <Download size={17} /></button><button type="button" className="secondary-button reset-button" onClick={resetAnalysis}><RefreshCcw size={17} /> Nova análise</button></div></div>
            <div className="result-image-wrap"><img src={`${API_URL}${result.processed_image_url}`} alt="Planta processada com as regiões identificadas" /></div>
            <div className="detection-summary"><div><strong>{result.detections.length}</strong><span>TAGs identificadas</span></div><div><strong>{result.stats?.regions_sent_to_ocr ?? 0}</strong><span>Regiões analisadas</span></div><div><strong>{result.stats?.processing_time_seconds ?? 0}s</strong><span>Tempo de processamento</span></div></div>
            <div className="detection-grid">
              {result.detections.length > 0 ? result.detections.map((detection, index) => <article className="detection-card" key={`${detection.tag}-${index}`}><div className="tag-name">{detection.tag}<span className={detection.status === 'Identificado' ? 'identified' : 'possible'}>{detection.status}</span></div><p>{detection.tipo} <i /> {detection.classe}</p><small>Confiança: {(detection.confidence * 100).toFixed(0)}%</small></article>) : <p className="empty-state">Nenhum equipamento cadastrado foi identificado nesta imagem.</p>}
            </div>
          </div>
        )}
      </section>
      <footer id="sobre"><img src="/iastech-logo.png" alt="IASTECH" /><span>TAGVision P&amp;ID · Soluções em automação industrial</span></footer>
    </main>
  );
}

export default App;
