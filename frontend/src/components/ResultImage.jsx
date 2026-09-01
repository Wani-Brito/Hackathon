import { useState } from 'react';
import { Maximize2, Minimize2, Image as ImageIcon } from 'lucide-react';

export default function ResultImage({ imageUrl, alt = 'Planta industrial processada' }) {
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <div className={`result-image-container ${isExpanded ? 'is-expanded' : ''}`} role="region" aria-label="Visualizador da Planta">
      <div className="image-toolbar">
        <div className="image-toolbar-left">
          <ImageIcon size={14} aria-hidden="true" />
          <span className="image-label">Diagrama com Anotações Técnicas</span>
        </div>
        <button
          type="button"
          className="image-action-btn"
          onClick={() => setIsExpanded(!isExpanded)}
          title={isExpanded ? 'Restaurar tamanho padrão' : 'Expandir diagrama para melhor legibilidade'}
          aria-expanded={isExpanded}
        >
          {isExpanded ? (
            <>
              <Minimize2 size={13} aria-hidden="true" /> <span>Reduzir</span>
            </>
          ) : (
            <>
              <Maximize2 size={13} aria-hidden="true" /> <span>Expandir Imagem</span>
            </>
          )}
        </button>
      </div>

      <div className="result-image-wrap">
        <img
          src={imageUrl}
          alt={alt}
          className="result-img"
          onClick={() => setIsExpanded(!isExpanded)}
          title="Clique para alternar tamanho"
        />
      </div>
      <div className="image-footer-note">
        <span>Legenda: caixas coloridas demarcam regiões de texto e símbolos identificados pelo OCR.</span>
      </div>
    </div>
  );
}
