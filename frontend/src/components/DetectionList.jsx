import { useState, useMemo } from 'react';
import { Search, CheckCircle, AlertCircle } from 'lucide-react';
import { formatConfidence } from '../utils/formatters';

export default function DetectionList({ detections = [] }) {
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('ALL');

  const filteredDetections = useMemo(() => {
    return detections.filter((item) => {
      const term = searchTerm.toLowerCase();
      const matchesSearch =
        !searchTerm ||
        (item.tag && item.tag.toLowerCase().includes(term)) ||
        (item.tipo && item.tipo.toLowerCase().includes(term)) ||
        (item.classe && item.classe.toLowerCase().includes(term));

      const matchesStatus =
        statusFilter === 'ALL' || item.status === statusFilter;

      return matchesSearch && matchesStatus;
    });
  }, [detections, searchTerm, statusFilter]);

  const identifiedCount = useMemo(
    () => detections.filter((d) => d.status === 'Identificado').length,
    [detections]
  );
  const possibleCount = useMemo(
    () => detections.filter((d) => d.status === 'Possível TAG' || d.status === 'Possivel TAG').length,
    [detections]
  );

  return (
    <div className="detection-list-card">
      <div className="detection-list-header">
        <div className="search-box">
          <Search size={15} className="search-icon" />
          <input
            type="text"
            placeholder="Buscar por TAG, Tipo ou Classe..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="search-input"
          />
          {searchTerm && (
            <button
              type="button"
              onClick={() => setSearchTerm('')}
              className="clear-search"
              aria-label="Limpar busca"
            >
              ×
            </button>
          )}
        </div>

        <div className="filter-group">
          <button
            type="button"
            className={`filter-pill ${statusFilter === 'ALL' ? 'active' : ''}`}
            onClick={() => setStatusFilter('ALL')}
          >
            Todas ({detections.length})
          </button>
          <button
            type="button"
            className={`filter-pill ${statusFilter === 'Identificado' ? 'active' : ''}`}
            onClick={() => setStatusFilter('Identificado')}
          >
            Identificadas ({identifiedCount})
          </button>
          <button
            type="button"
            className={`filter-pill ${statusFilter === 'Possível TAG' ? 'active' : ''}`}
            onClick={() => setStatusFilter(statusFilter === 'Possível TAG' ? 'ALL' : 'Possível TAG')}
          >
            Possíveis ({possibleCount})
          </button>
        </div>
      </div>

      <div className="table-responsive">
        <table className="detection-table">
          <thead>
            <tr>
              <th>TAG</th>
              <th>Status</th>
              <th>Tipo</th>
              <th>Classe</th>
              <th className="text-right">Confiança</th>
            </tr>
          </thead>
          <tbody>
            {filteredDetections.length > 0 ? (
              filteredDetections.map((d) => (
                <tr key={d.tag}>
                  <td className="tag-cell">{d.tag}</td>
                  <td>
                    <span className={`status-badge ${d.status === 'Identificado' ? 'identified' : 'possible'}`}>
                      {d.status === 'Identificado' ? <CheckCircle size={11} /> : <AlertCircle size={11} />}
                      {d.status}
                    </span>
                  </td>
                  <td>{d.tipo}</td>
                  <td>{d.classe}</td>
                  <td className="text-right">
                    <div className="confidence-cell">
                      <span>{formatConfidence(d.confidence)}</span>
                      <div className="confidence-bar-bg">
                        <div
                          className="confidence-bar-fill"
                          style={{ width: `${Math.min(100, Math.max(0, d.confidence * 100))}%` }}
                        />
                      </div>
                    </div>
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan="5" className="empty-table-cell">
                  {detections.length === 0
                    ? 'Nenhum equipamento cadastrado foi identificado nesta imagem.'
                    : 'Nenhuma TAG corresponde aos critérios de busca ou filtro.'}
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
