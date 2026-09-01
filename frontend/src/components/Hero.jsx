import { ArrowDown, Cpu, FileSearch, ShieldCheck, Activity } from 'lucide-react';

export default function Hero() {
  const scrollToAnalysis = (e) => {
    e.preventDefault();
    const target = document.getElementById('analise');
    if (target) {
      target.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <section className="hero" id="inicio" aria-labelledby="hero-title">
      <div className="hero-copy animate-fade-in-up">
        <div className="eyebrow" aria-hidden="true">
          <span className="eyebrow-line" />
          <span>Inteligência Visual Industrial</span>
        </div>
        <h1 id="hero-title" className="hero-title-stagger">
          Extração automatizada de TAGs em <em>plantas P&amp;ID.</em>
        </h1>
        <p className="hero-description hero-desc-stagger">
          Tecnologia de visão computacional e OCR para identificar instrumentos,
          válvulas e equipamentos técnicos diretamente de diagramas de engenharia.
        </p>

        <div className="hero-features-grid hero-pills-stagger" role="list">
          <div className="feature-pill" role="listitem">
            <Cpu size={15} aria-hidden="true" />
            <span>Processamento com OpenCV</span>
          </div>
          <div className="feature-pill" role="listitem">
            <FileSearch size={15} aria-hidden="true" />
            <span>OCR de Alta Precisão</span>
          </div>
          <div className="feature-pill" role="listitem">
            <ShieldCheck size={15} aria-hidden="true" />
            <span>Catálogo ISA-5.1 Integrado</span>
          </div>
        </div>

        <div className="hero-cta-wrap hero-cta-stagger">
          <a href="#analise" onClick={scrollToAnalysis} className="hero-action-link">
            <span>Iniciar Análise Técnica</span>
            <ArrowDown size={14} aria-hidden="true" />
          </a>
        </div>
      </div>

      <div className="hero-visual" aria-hidden="true">
        <div className="radar-frame">
          <div className="radar-ring ring-one" />
          <div className="radar-ring ring-two" />
          <div className="radar-sweep" />
          <div className="radar-crosshair-h" />
          <div className="radar-crosshair-v" />
          <div className="radar-core pulse-glow">
            <Activity size={32} className="radar-core-icon" />
          </div>
          <div className="radar-badge badge-top">
            <span className="status-dot-active pulse-dot" /> ENGINE OCR PRONTO
          </div>
          <div className="radar-badge badge-bottom">
            <span>VARREDURA TÉCNICA</span>
          </div>
        </div>
      </div>
    </section>
  );
}
