# Framework de Avaliação Real do Pipeline OCR / P&ID

Este módulo fornece uma avaliação quantitativa rigorosa, reproduzível e sem dados inventados para o pipeline de visão computacional e OCR em diagramas P&ID.

---

## 1. Estrutura de Arquivos

```
projeto/evaluation/
├── ground_truth.csv        # Tabela com as anotações reais de referência (Ground Truth)
├── evaluate.py             # Script de cálculo de métricas e matriz de confusão
├── README.md               # Esta documentação
└── results/                # Pasta onde os relatórios gerados são salvos (ignorada no Git)
    ├── metrics_summary.json
    ├── evaluation_per_image.csv
    └── confusion_matrix_status.csv
```

---

## 2. Como Rotular o `ground_truth.csv`

Para cada TAG visível em uma imagem do dataset (`projeto/dataset/`), adicione uma linha no arquivo `ground_truth.csv`:

| Coluna | Descrição | Exemplo |
|---|---|---|
| `image` | Nome do arquivo de imagem na pasta `dataset` | `0.jpg` |
| `tag` | Identificador textual exato da TAG | `FO` ou `FV210` |
| `tipo` | Tipo do componente conforme catálogo ou norma | `Fail Open` ou `Válvula` |
| `classe` | Classe do componente conforme catálogo ou norma | `Falha de Válvula` ou `Instrumento` |
| `status` | `Identificado` (se cadastrada) ou `Possível TAG` (se não cadastrada) | `Identificado` |

### Exemplo de Preenchimento:
```csv
image,tag,tipo,classe,status
0.jpg,FO,Fail Open,Falha de Válvula,Identificado
0.jpg,FC,Fail Close,Falha de Válvula,Identificado
0.jpg,FL,Fail Locked,Falha de Válvula,Identificado
```

> **Atenção**: Nunca invente dados. Registre apenas TAGs que foram verificadas visualmente na imagem.

---

## 3. Como Executar a Avaliação

Com o ambiente virtual ativado:

```bash
# Executa a avaliação sobre todas as imagens presentes no ground_truth.csv
python projeto/evaluation/evaluate.py
```

### Opções Disponíveis:
* `--ground-truth PATH`: Caminho customizado para o CSV de ground truth (padrão: `projeto/evaluation/ground_truth.csv`).
* `--dataset PATH`: Diretório de imagens (padrão: `projeto/dataset`).
* `--output-dir PATH`: Diretório para salvar relatórios (padrão: `projeto/evaluation/results`).

---

## 4. Métricas Calculadas

Para cada imagem e no consolidado global:

* **True Positives (TP)**: TAGs presentes no Ground Truth que foram corretamente detectadas pelo pipeline.
* **False Positives (FP)**: TAGs detectadas pelo pipeline que NÃO existem no Ground Truth (alarmes falsos/ruídos).
* **False Negatives (FN)**: TAGs presentes no Ground Truth que o pipeline NÃO conseguiu detectar (omissões).
* **Precision**: $\frac{\text{TP}}{\text{TP} + \text{FP}}$
* **Recall**: $\frac{\text{TP}}{\text{TP} + \text{FN}}$
* **F1-Score**: $2 \times \frac{\text{Precision} \times \text{Recall}}{\text{Precision} + \text{Recall}}$

Quando houver instâncias rotuladas com tipo/classe, o script também calcula a acurácia de classificação de metadados para os TPs e gera matriz de confusão tabular.
