import { useState } from 'react';
import { UploadCloud, FileImage, ShieldCheck, ScanLine, X } from 'lucide-react';

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
    <div className="upload-panel">
      <div className="upload-copy">
        <div className="step-number">01</div>
        <h3>Enviar diagrama P&amp;ID</h3>
        <p>Formatos aceitos: JPG e PNG. Selecione ou arraste a planta que deseja analisar.</p>
        <div className="upload-note">
          <ShieldCheck size={18} /> Seu arquivo é processado e descartado com segurança.
        </div>
      </div>

      <div
        className={`drop-zone ${preview ? 'has-preview' : ''} ${isDragOver ? 'drag-over' : ''}`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        {preview ? (
          <>
            <img src={preview} alt="Prévia da planta selecionada" />
            <div className="preview-footer">
              <FileImage size={17} />
              <span>{file?.name}</span>
              <button
                type="button"
                className="clear-file-btn"
                onClick={onReset}
                title="Remover arquivo"
                aria-label="Remover arquivo"
              >
                <X size={15} />
              </button>
            </div>
          </>
        ) : (
          <>
            <div className="upload-icon"><UploadCloud size={29} /></div>
            <strong>Selecione o arquivo da planta</strong>
            <span>ou arraste-o para esta área (JPG ou PNG)</span>
          </>
        )}
        <input
          id="plant-file"
          type="file"
          accept="image/jpeg,image/png,image/jpg"
          onChange={handleChange}
        />
        <label htmlFor="plant-file" className="secondary-button">
          {preview ? 'Trocar arquivo' : 'Selecionar arquivo'}
        </label>
      </div>

      <button
        type="button"
        className="primary-button process-button"
        onClick={onProcess}
        disabled={!file || disabled}
      >
        Processar planta <ScanLine size={19} />
      </button>
    </div>
  );
}
