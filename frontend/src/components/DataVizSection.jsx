import { useMemo } from 'react';
import DistributionChart from './DistributionChart';

const TOP = 6;

function toSorted(map, top = TOP) {
  return Object.entries(map)
    .map(([label, value]) => ({ label, value }))
    .sort((a, b) => b.value - a.value)
    .slice(0, top);
}

/**
 * Secao de visualizacoes de dados — apenas campos reais da API:
 * status, tipo, classe e confidence.
 */
export default function DataVizSection({ uniqueDetections }) {
  const { statusDist, classDist, typeDist, confDist } = useMemo(() => {
    if (!uniqueDetections.length)
      return { statusDist: [], classDist: [], typeDist: [], confDist: [] };

    const statusMap = {};
    const classMap = {};
    const typeMap = {};
    const confBuckets = { Alta: 0, 'M\u00e9dia': 0, Baixa: 0 };

    uniqueDetections.forEach((d) => {
      // status
      const sk = d.status || 'Desconhecido';
      statusMap[sk] = (statusMap[sk] || 0) + 1;

      // classe
      const ck = d.classe || 'N\u00e3o cadastrado';
      classMap[ck] = (classMap[ck] || 0) + 1;

      // tipo
      const tk = d.tipo || 'N\u00e3o cadastrado';
      typeMap[tk] = (typeMap[tk] || 0) + 1;

      // confianca
      const pct = (d.confidence || 0) * 100;
      if (pct >= 90) confBuckets['Alta']++;
      else if (pct >= 70) confBuckets['M\u00e9dia']++;
      else confBuckets['Baixa']++;
    });

    return {
      statusDist: toSorted(statusMap),
      classDist: toSorted(classMap),
      typeDist: toSorted(typeMap),
      confDist: Object.entries(confBuckets)
        .filter(([, v]) => v > 0)
        .map(([label, value]) => ({ label, value })),
    };
  }, [uniqueDetections]);

  if (!uniqueDetections.length) return null;

  return (
    <section
      className="dataviz-section animate-fade-in-up"
      aria-label="Visualiza\u00e7\u00f5es dos Resultados"
      style={{ animationDelay: '0.06s' }}
    >
      <div className="dataviz-section-header">
        <div className="eyebrow">
          <span className="eyebrow-line" />
          <span>An\u00e1lise Estat\u00edstica</span>
        </div>
        <h3>Distribui\u00e7\u00e3o das Detec\u00e7\u00f5es</h3>
      </div>

      <div className="dataviz-grid">
        <DistributionChart
          title="Por Status de Reconhecimento"
          data={statusDist}
          colorMap={{ Identificado: '#38ef7d', 'Poss\u00edvel TAG': '#ffd077', 'Possivel TAG': '#ffd077' }}
        />
        <DistributionChart
          title="Por N\u00edvel de Confian\u00e7a OCR"
          data={confDist}
          colorMap={{ Alta: '#38ef7d', 'M\u00e9dia': '#ffd077', Baixa: '#ff6166' }}
        />
        <DistributionChart
          title="Por Classe do Equipamento"
          data={classDist}
        />
        <DistributionChart
          title="Por Tipo do Equipamento"
          data={typeDist}
        />
      </div>
    </section>
  );
}
