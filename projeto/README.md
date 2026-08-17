# Extração de Informações de P&IDs Industriais - Versão 1.0

## Descrição

Primeira versão de um projeto Python para processamento de imagens de P&ID (Piping and Instrumentation Diagrams) usando OpenCV. Este projeto implementa um pipeline básico de detecção de regiões e contornos em diagramas industriais.

## Estrutura do Projeto

```
projeto/
├── main.py                 # Arquivo principal
├── image_processing.py     # Módulo de processamento de imagens
├── requirements.txt        # Dependências do projeto
├── dataset/               # Pasta para armazenar imagens
│   └── exemplo.png       # Imagem de entrada (deve ser adicionada)
└── README.md              # Este arquivo
```

## Pipeline de Processamento

O projeto implementa as seguintes etapas:

1. **Carregamento da Imagem**: Lê a imagem usando OpenCV
2. **Escala de Cinza**: Converte a imagem para grayscale para facilitar processamento
3. **Desfoque (Blur)**: Aplica Gaussian Blur para reduzir ruído
4. **Limiarização (Threshold)**: Converte em imagem binária usando método Otsu
5. **Detecção de Contornos**: Encontra contornos de objetos na imagem
6. **Bounding Boxes**: Desenha retângulos ao redor dos objetos detectados
7. **Visualização**: Mostra a imagem original e processada lado a lado

## Instalação

### 1. Criar ambiente virtual (recomendado)

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

### 2. Instalar dependências

```bash
pip install -r requirements.txt
```

## Uso

### 1. Adicionar uma Imagem de Teste

Coloque uma imagem de P&ID em formato PNG ou JPG na pasta `dataset` e renomeie-a para `exemplo.png`.

Exemplo de imagem de teste:
- Pode ser um diagrama industrial real
- Uma imagem contendo formas, linhas e símbolos
- Qualquer imagem com elementos bem definidos

### 2. Executar o Pipeline

```bash
python main.py
```

A imagem será processada e exibida em uma janela. Pressione qualquer tecla para fechar.

### 3. Resultado

O programa irá:
- Detectar objetos e desenhar bounding boxes
- Mostrar a imagem original e processada lado a lado
- Salvar a imagem com os bounding boxes em `dataset/resultado.png`
- Imprimir o número total de objetos detectados

## Classe PIDImageProcessor

Classe principal para processamento de imagens:

### Métodos Principais

- `convert_to_grayscale()`: Converte para escala de cinza
- `apply_blur(kernel_size)`: Aplica desfoque Gaussiano
- `apply_threshold(threshold_value, method)`: Aplica limiarização
- `detect_contours()`: Detecta contornos na imagem
- `draw_bounding_boxes(min_area)`: Desenha bounding boxes
- `process_pipeline(threshold_method, min_area)`: Executa todo o pipeline

### Exemplo de Uso Avançado

```python
from image_processing import PIDImageProcessor

# Criar processador
processor = PIDImageProcessor('dataset/exemplo.png')

# Executar pipeline
original, processed = processor.process_pipeline(
    threshold_method='otsu',
    min_area=500
)

# Acessar todas as imagens processadas
images = processor.get_processed_images()
print(images.keys())  # 'original', 'grayscale', 'blurred', 'threshold', 'with_boxes'
```

## Parâmetros Ajustáveis

No arquivo `main.py`, você pode ajustar:

- **`min_area=500`**: Área mínima (em pixels) para considerar um objeto detectado
  - Menor valor = mais objetos detectados (mais ruído)
  - Maior valor = menos objetos (menos sensibilidade)

- **`threshold_method='otsu'`**: Método de limiarização
  - `'otsu'`: Automático (recomendado)
  - `'binary'`: Manual com valor fixo

## Próximas Etapas

Este projeto está preparado para as seguintes melhorias:

1. **OCR para Identificação de TAGs**: Implementar Tesseract OCR para reconhecer tags como `FV210`, `M210`, `LT210`
2. **Classificação de Componentes**: Classificar objetos detectados (válvulas, medidores, etc.)
3. **Extração de Conexões**: Identificar linhas e conexões entre componentes
4. **IA/Deep Learning**: Implementar modelos como YOLO ou Faster R-CNN para detecção mais precisa
5. **Banco de Dados**: Armazenar resultados extraídos

## Dependências

- **opencv-python**: Processamento de imagens
- **numpy**: Operações numéricas
- **Pillow**: Manipulação adicional de imagens

## Troubleshooting

### "Erro: Imagem não encontrada"
- Certifique-se de adicionar a imagem em `dataset/exemplo.png`

### Poucos objetos detectados
- Ajuste o parâmetro `min_area` para um valor menor em `main.py`
- Tente diferentes imagens

### Muitos objetos detectados (ruído)
- Aumente o parâmetro `min_area`
- Ajuste o desfoque: modifique `kernel_size` em `image_processing.py`

## Licença

Este projeto é parte de um hackathon de extração de informações de P&IDs industriais.

## Autor

Desenvolvido como base funcional para o desafio de P&ID.
