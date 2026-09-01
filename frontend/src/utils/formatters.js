/**
 * Deduplica detecções por TAG preservando aquela com maior índice de confiança.
 */
export function getUniqueDetections(detections = []) {
  if (!Array.isArray(detections) || detections.length === 0) {
    return [];
  }

  const map = detections.reduce((acc, item) => {
    const key = item.tag;
    if (!key) return acc;
    if (!acc[key] || item.confidence > acc[key].confidence) {
      acc[key] = item;
    }
    return acc;
  }, {});

  return Object.values(map);
}

/**
 * Formata um valor de confiança (0-1) em porcentagem.
 */
export function formatConfidence(confidence) {
  if (typeof confidence !== 'number' || Number.isNaN(confidence)) return '0%';
  return `${(confidence * 100).toFixed(0)}%`;
}

/**
 * Formata tamanho de arquivo em KB ou MB.
 */
export function formatFileSize(bytes) {
  if (!bytes || typeof bytes !== 'number') return '';
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
}

/**
 * Valida se o arquivo possui formato de imagem suportado (JPG/PNG).
 */
export function isValidImageFile(file) {
  if (!file) return false;
  const validTypes = ['image/jpeg', 'image/png', 'image/jpg'];
  if (file.type && validTypes.includes(file.type.toLowerCase())) {
    return true;
  }
  const ext = file.name ? file.name.split('.').pop().toLowerCase() : '';
  return ['jpg', 'jpeg', 'png'].includes(ext);
}
