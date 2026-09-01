import { useState, useEffect } from 'react';
import { Loader2, CheckCircle2, Circle, ScanLine, Cpu, Search, CheckCircle } from 'lucide-react';

const STAGES = [
  { id: 1, label: 'Carregando e preparando imagem', icon: ScanLine },
  { id: 2, label: 'Segmentando regiões e contornos (OpenCV)', icon: Cpu },
  { id: 3, label: 'Extraindo caracteres com EasyOCR', icon: Search },
  { id: 4, label: 'Cruzando com catálogo de equipamentos', icon: CheckCircle },
];

export default function ProcessingState() {
  const [activeStage, setActiveStage] = useState(0);

  useEffect(() => {
    const timer1 = setTimeout(() => setActiveStage(1), 1000);
    const timer2 = setTimeout(() => setActiveStage(2), 3000);
    const timer3 = setTimeout(() => setActiveStage(3), 7000);

    return () => {
      clearTimeout(timer1);
      clearTimeout(timer2);
      clearTimeout(timer3);
    };
  }, []);

  return (
    <div className="status-panel processing-panel animate-fade-in" role="status" aria-live="polite">
      <div className="processing-header">
        <div className="pulse-loader-ring">
          <Loader2 className="spinning-loader" size={36} aria-hidden="true" />
        </div>
        <div className="processing-title-group">
          <span className="processing-badge">
            <span className="pulse-dot-red" /> PROCESSAMENTO ATIVO
          </span>
          <h3>Analisando Planta Industrial</h3>
          <p>O pipeline de visão computacional está inspecionando o diagrama.</p>
        </div>
      </div>

      <div className="scan-progress-track" aria-hidden="true">
        <div className="scan-progress-bar" />
      </div>

      <div className="pipeline-steps-list">
        {STAGES.map((stage, idx) => {
          const isDone = idx < activeStage;
          const isCurrent = idx === activeStage;

          return (
            <div
              key={stage.id}
              className={`pipeline-step-item ${isDone ? 'step-done' : ''} ${isCurrent ? 'step-active' : 'step-pending'}`}
            >
              <div className="step-indicator">
                {isDone ? (
                  <CheckCircle2 size={16} className="step-icon-done" />
                ) : isCurrent ? (
                  <Loader2 size={16} className="step-icon-active spinning-loader" />
                ) : (
                  <Circle size={14} className="step-icon-pending" />
                )}
              </div>
              <span className="step-label">{stage.label}</span>
              {isDone && <span className="step-status-tag">OK</span>}
              {isCurrent && <span className="step-status-tag active">EM CURSO</span>}
            </div>
          );
        })}
      </div>
    </div>
  );
}
