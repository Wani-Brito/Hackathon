import { useState, useMemo } from 'react';
import { Search, CheckCircle2, AlertTriangle, X } from 'lucide-react';
import { formatConfidence } from '../utils/formatters';

export default function DetectionList({ detections = [] }) {
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('ALL');

  const filteredDetections = useMemo(() => {
    return detections.filter((item) => {
      const term = searchTerm.trim().toLowerCase();
      const matchesSearch =
        !term ||
        (item.tag && item.tag.toLowerCase().includes(term)) ||
        (item.tipo && item.tipo.toLowerCase().includes(term)) ||
        (item.classe && item.classe.toLowerCase().includes(term)) ||
        (item.grupo && item.grupo.toLowerCase().includes(term));

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
    <div className="detection-list-card" role="region" aria-label="Tabela de TAGs identificadas">
      <div className="detection-list-header">
        <div className="search-bar-wrap">
          <Search size={15} className="search-icon" aria-hidden="true" />
          <input
            type="text"
            placeholder="Filtrar por TAG, tipo, classe ou grupo..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="search-input"
            aria-label="Filtrar TAGs por texto"
          />
          {searchTerm && (
            <button
              type="button"
              onClick={() => setSearchTerm('')}
              className="clear-search-btn"
              title="Limpar busca"
              aria-label="Limpar busca"
            >
              <X size={13} aria-hidden="true" />
            </button>
          )}
        </div>

        <div className="filter-pills-row" role="group" aria-label="Filtros por status">
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
            className={`filter-pill ${statusFilter === 'Possível TAG' || statusFilter === 'Possivel TAG' ? 'active' : ''}`}
            onClick={() => setStatusFilter(statusFilter === 'Possível TAG' ? 'ALL' : 'Possível TAG')}
          >
            Possíveis ({possibleCount})
          </button>
        </div>
      </div>

      {/* Desktop Table View */}
      <div className="table-responsive desktop-only" tabIndex={0} role="region" aria-label="Lista de TAGs">
        <table className="detection-table">
          <thead>
            <tr>
              <th scope="col">TAG</th>
              <th scope="col">Status</th>
              <th scope="col">Tipo</th>
              <th scope="col">Classe</th>
              <th scope="col">Grupo</th>
              <th scope="col" className="text-right">Confiança</th>
            </tr>
          </thead>
          <tbody>
            {filteredDetections.length > 0 ? (
              filteredDetections.map((d, index) => {
                const isIdentified = d.status === 'Identificado';
                const confPercent = Math.min(100, Math.max(0, (d.confidence || 0) * 100));

                return (
                  <tr
                    key={d.tag}
                    className="table-row-animate"
                    style={{ animationDelay: `${Math.min(index * 35, 300)}ms` }}
                  >
                    <td className="tag-cell font-mono">{d.tag}</td>
                    <td>
                      <span className={`status-badge ${isIdentified ? 'identified' : 'possible'}`}>
                        {isIdentified ? (
                          <CheckCircle2 size={11} aria-hidden="true" />
                        ) : (
                          <AlertTriangle size={11} aria-hidden="true" />
                        )}
                        <span>{d.status}</span>
                      </span>
                    </td>
                    <td>{d.tipo}</td>
                    <td>{d.classe}</td>
                    <td>
                      <span className="group-badge">{d.grupo || 'Não cadastrado'}</span>
                    </td>
                    <td className="text-right">
                      <div className="confidence-cell">
                        <span className="confidence-value font-mono">{formatConfidence(d.confidence)}</span>
                        <div className="confidence-bar-bg" aria-hidden="true">
                          <div
                            className={`confidence-bar-fill ${confPercent >= 75 ? 'high' : 'medium'}`}
                            style={{ width: `${confPercent}%` }}
                          />
                        </div>
                      </div>
                    </td>
                  </tr>
                );
              })
            ) : (
              <tr>
                <td colSpan="6" className="empty-table-cell">
                  {detections.length === 0
                    ? 'Nenhum equipamento cadastrado foi identificado nesta imagem.'
                    : 'Nenhuma TAG corresponde aos critérios do filtro ou busca.'}
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {/* Mobile Cards View (<= 640px) */}
      <div className="mobile-cards-list mobile-only" role="region" aria-label="Lista de TAGs em cartões">
        {filteredDetections.length > 0 ? (
          filteredDetections.map((d, index) => {
            const isIdentified = d.status === 'Identificado';
            const confPercent = Math.min(100, Math.max(0, (d.confidence || 0) * 100));

            return (
              <article
                key={d.tag}
                className="mobile-tag-card"
                style={{ animationDelay: `${Math.min(index * 35, 300)}ms` }}
              >
                <div className="mobile-card-top">
                  <span className="mobile-card-tag font-mono">{d.tag}</span>
                  <span className={`status-badge ${isIdentified ? 'identified' : 'possible'}`}>
                    {isIdentified ? (
                      <CheckCircle2 size={10} aria-hidden="true" />
                    ) : (
                      <AlertTriangle size={10} aria-hidden="true" />
                    )}
                    <span>{d.status}</span>
                  </span>
                </div>

                <div className="mobile-card-details">
                  <div className="mobile-detail-row">
                    <span className="detail-label">Tipo:</span>
                    <span className="detail-val">{d.tipo}</span>
                  </div>
                  <div className="mobile-detail-row">
                    <span className="detail-label">Classe:</span>
                    <span className="detail-val">{d.classe}</span>
                  </div>
                  <div className="mobile-detail-row">
                    <span className="detail-label">Grupo:</span>
                    <span className="detail-val">{d.grupo || 'Não cadastrado'}</span>
                  </div>
                </div>

                <div className="mobile-card-footer">
                  <span className="mobile-conf-label">Confiança:</span>
                  <div className="confidence-cell">
                    <span className="confidence-value font-mono">{formatConfidence(d.confidence)}</span>
                    <div className="confidence-bar-bg" aria-hidden="true">
                      <div
                        className={`confidence-bar-fill ${confPercent >= 75 ? 'high' : 'medium'}`}
                        style={{ width: `${confPercent}%` }}
                      />
                    </div>
                  </div>
                </div>
              </article>
            );
          })
        ) : (
          <div className="empty-table-cell">
            {detections.length === 0
              ? 'Nenhum equipamento cadastrado foi identificado nesta imagem.'
              : 'Nenhuma TAG corresponde aos critérios do filtro ou busca.'}
          </div>
        )}
      </div>
    </div>
  );
}
