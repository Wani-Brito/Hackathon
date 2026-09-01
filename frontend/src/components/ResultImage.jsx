import { useState } from 'react';
import { Maximize2, Minimize2 } from 'lucide-react';

export default function ResultImage({ imageUrl, alt = 'Planta processada' }) {
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <div className={`result-image-container ${isExpanded ? 'is-expanded' : ''}`}>
      <div className="image-toolbar">
        <span className="image-label">Planta Anotada</span>
        <button
          type="button"
          className="image-action-btn"
          onClick={() => setIsExpanded(!isExpanded)}
          title={isExpanded ? 'Visualização padrão' : 'Expandir imagem'}
        >
          {isExpanded ? (
            <>
              <Minimize2 size={14} /> <span>Reduzir</span>
            </>
          ) : (
            <>
              <Maximize2 size={14} /> <span>Expandir</span>
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
    </div>
  );
}
