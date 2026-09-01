import { LoaderCircle } from 'lucide-react';

export default function ProcessingState() {
  return (
    <div className="status-panel" role="status" aria-live="polite">
      <LoaderCircle className="loader" size={42} />
      <p className="eyebrow"><span /> Processamento em andamento</p>
      <h3>Analisando sua planta industrial</h3>
      <p>Identificando regiões, aplicando OCR e mapeando TAGs técnicas. Isso pode levar alguns instantes.</p>
    </div>
  );
}
