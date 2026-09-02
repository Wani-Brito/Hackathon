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
  const { statusDist, groupDist, classDist, typeDist, confDist } = useMemo(() => {
    if (!uniqueDetections.length)
      return { statusDist: [], groupDist: [], classDist: [], typeDist: [], confDist: [] };

    const statusMap = {};
    const groupMap = {};
    const classMap = {};
    const typeMap = {};
    const confBuckets = { Alta: 0, Média: 0, Baixa: 0 };

    uniqueDetections.forEach((d) => {
      // status
      const sk = d.status || 'Desconhecido';
      statusMap[sk] = (statusMap[sk] || 0) + 1;

      // grupo
      const gk = d.grupo || 'Não cadastrado';
      groupMap[gk] = (groupMap[gk] || 0) + 1;

      // classe
      const ck = d.classe || 'Não cadastrado';
      classMap[ck] = (classMap[ck] || 0) + 1;

      // tipo
      const tk = d.tipo || 'Não cadastrado';
      typeMap[tk] = (typeMap[tk] || 0) + 1;

      // confianca
      const pct = (d.confidence || 0) * 100;
      if (pct >= 90) confBuckets['Alta']++;
      else if (pct >= 70) confBuckets['Média']++;
      else confBuckets['Baixa']++;
    });

    return {
      statusDist: toSorted(statusMap),
      groupDist: toSorted(groupMap),
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
      aria-label="Visualizações dos Resultados"
      style={{ animationDelay: '0.06s' }}
    >
      <div className="dataviz-section-header">
        <div className="eyebrow">
          <span className="eyebrow-line" />
          <span>Análise Estatística</span>
        </div>
        <h3>Distribuição das Detecções</h3>
      </div>

      <div className="dataviz-grid">
        <DistributionChart
          title="Por Grupo de Aplicação"
          data={groupDist}
          colorMap={{
            'Instrumentação': '#38ef7d',
            'Válvulas / Atuadores': '#5d8cae',
            'Controle': '#ffd077',
            'Segurança / Proteção': '#ff6166',
            'Equipamentos': '#a855f7',
            'Não cadastrado': '#8fa0b3',
          }}
        />
        <DistributionChart
          title="Por Status de Reconhecimento"
          data={statusDist}
          colorMap={{ Identificado: '#38ef7d', 'Possível TAG': '#ffd077', 'Possivel TAG': '#ffd077' }}
        />
        <DistributionChart
          title="Por Nível de Confiança OCR"
          data={confDist}
          colorMap={{ Alta: '#38ef7d', Média: '#ffd077', Baixa: '#ff6166' }}
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
