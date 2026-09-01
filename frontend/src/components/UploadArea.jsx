import { useState } from 'react';
import { UploadCloud, FileImage, ShieldCheck, ArrowRight, X } from 'lucide-react';
import { formatFileSize } from '../utils/formatters';

export default function UploadArea({ file, preview, onFileSelect, onProcess, onReset, disabled }) {
  const [isDragOver, setIsDragOver] = useState(false);

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragOver(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragOver(false);
    const droppedFile = e.dataTransfer.files?.[0];
    if (droppedFile) {
      onFileSelect(droppedFile);
    }
  };

  const handleChange = (e) => {
    const selected = e.target.files?.[0];
    if (selected) {
      onFileSelect(selected);
    }
  };

  return (
    <div className="upload-panel animate-fade-in-up" role="region" aria-label="Upload de planta técnica">
      <div className="upload-copy">
        <div className="step-tag">ETAPA 01</div>
        <h3>Carregar Diagrama P&amp;ID</h3>
        <p>
          Selecione uma imagem de planta técnica industrial para reconhecimento automático de componentes e TAGs.
        </p>

        <div className="format-spec-box">
          <span className="spec-title">Especificações aceitas:</span>
          <div className="spec-tags">
            <span className="spec-tag">JPG</span>
            <span className="spec-tag">JPEG</span>
            <span className="spec-tag">PNG</span>
          </div>
          <p className="spec-note">Resolução recomendada: 150 a 300 DPI para maior nitidez de leitura.</p>
        </div>

        <div className="upload-security-note">
          <ShieldCheck size={16} aria-hidden="true" />
          <span>O arquivo é processado localmente e descartado com segurança após a extração.</span>
        </div>
      </div>

      <div className="upload-interactive-column">
        <div
          className={`drop-zone ${preview ? 'has-preview' : ''} ${isDragOver ? 'drag-over' : ''}`}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          tabIndex={0}
          role="button"
          aria-label={preview ? 'Visualização da imagem selecionada' : 'Área de upload de diagrama'}
        >
          {preview ? (
            <div className="preview-container animate-fade-in">
              <img src={preview} alt="Prévia da planta selecionada" className="preview-thumbnail" />
              <div className="preview-meta-bar">
                <div className="file-info-group">
                  <FileImage size={16} className="file-icon" aria-hidden="true" />
                  <div className="file-text-details">
                    <span className="file-name" title={file?.name}>{file?.name}</span>
                    <span className="file-size">{formatFileSize(file?.size)}</span>
                  </div>
                </div>
                <button
                  type="button"
                  className="remove-file-button"
                  onClick={onReset}
                  title="Remover e escolher outro arquivo"
                  aria-label="Remover arquivo selecionado"
                >
                  <X size={15} aria-hidden="true" />
                  <span>Remover</span>
                </button>
              </div>
            </div>
          ) : (
            <div className="drop-prompt">
              <div className="upload-icon-circle pulse-hover">
                <UploadCloud size={32} aria-hidden="true" />
              </div>
              <strong className="drop-title">Arraste e solte o diagrama aqui</strong>
              <span className="drop-subtitle">ou clique no botão abaixo para explorar arquivos</span>
            </div>
          )}

          <input
            id="plant-file-input"
            type="file"
            accept="image/jpeg,image/png,image/jpg"
            onChange={handleChange}
            className="hidden-file-input"
          />
        </div>

        <div className="upload-actions-bar">
          <label htmlFor="plant-file-input" className="secondary-button select-file-label">
            {preview ? 'Trocar Diagrama' : 'Selecionar Arquivo'}
          </label>

          <button
            type="button"
            className="primary-button process-cta-button"
            onClick={onProcess}
            disabled={!file || disabled}
          >
            <span>Processar Planta</span>
            <ArrowRight size={17} aria-hidden="true" />
          </button>
        </div>
      </div>
    </div>
  );
}
