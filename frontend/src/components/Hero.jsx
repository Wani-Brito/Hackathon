import { CheckCircle2, ScanLine } from 'lucide-react';

export default function Hero() {
  return (
    <section className="hero" id="inicio">
      <div className="hero-copy">
        <p className="eyebrow"><span /> Inteligência industrial</p>
        <h1>Precisão visual para <em>plantas industriais.</em></h1>
        <p className="hero-description">
          Utilize visão computacional para identificar TAGs e organizar informações essenciais dos seus diagramas P&amp;ID.
        </p>
        <div className="hero-points">
          <span><CheckCircle2 size={17} /> Leitura de TAGs</span>
          <span><CheckCircle2 size={17} /> Processamento seguro</span>
        </div>
      </div>
      <div className="hero-visual" aria-hidden="true">
        <div className="radar-ring ring-one" />
        <div className="radar-ring ring-two" />
        <div className="radar-core"><ScanLine size={42} /></div>
        <div className="floating-label label-top">OCR ATIVO</div>
        <div className="floating-label label-bottom">P&amp;ID SCAN</div>
      </div>
    </section>
  );
}
