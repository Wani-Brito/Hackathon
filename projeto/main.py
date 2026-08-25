import cv2
import os
import sys
import re
import pandas as pd
from image_processing import PIDImageProcessor


def extrair_numero(nome_arquivo):
    """Extrai os números do nome do arquivo para ordenar numericamente (ex: 1, 2... 10, 11... 100)."""
    numeros = re.findall(r'\d+', nome_arquivo)
    return int(numeros[0]) if numeros else float('inf')


def main():
    pasta_projeto = os.path.dirname(__file__)
    raiz_projeto = os.path.dirname(pasta_projeto)

    dataset_path = os.path.join(pasta_projeto, "dataset")
    output_path = os.path.join(raiz_projeto, "resultados")
    csv_path = os.path.join(raiz_projeto, "tabela_equipamentos.csv")

    os.makedirs(output_path, exist_ok=True)

    print("=" * 60)
    print("PROCESSAMENTO DO DATASET E GERAÇÃO DE RELATÓRIO")
    print("=" * 60)

    if os.path.exists(csv_path):
        df_referencia = pd.read_csv(csv_path)
        print(f"Planilha de referência carregada: {csv_path}")
    else:
        print(f"\nERRO: O arquivo '{csv_path}' não foi encontrado na raiz.")
        sys.exit(1)

    if not os.path.exists(dataset_path):
        print(f"\nERRO: A pasta dataset não foi encontrada em: {dataset_path}")
        sys.exit(1)

    # Filtra APENAS arquivos válidos contidos estritamente na pasta dataset
    todos_itens = os.listdir(dataset_path)
    imagens = []

    for arquivo in todos_itens:
        caminho_completo = os.path.join(dataset_path, arquivo)
        
        # Garante que é um ARQUIVO (e não uma pasta) e que tem extensão de imagem
        if os.path.isfile(caminho_completo) and arquivo.lower().endswith(('.png', '.jpg', '.jpeg')):
            imagens.append(arquivo)

    # Ordenação REALMENTE NUMÉRICA (1, 2, 3... 9, 10, 11... 100)
    imagens.sort(key=extrair_numero)

    if not imagens:
        print("\nNenhuma imagem encontrada na pasta dataset.")
        sys.exit(1)

    print(f"\n{len(imagens)} imagens encontradas para processar.")
    print(f"Resultados serão salvos em: {output_path}")
    print("=" * 60)

    relatorio_dados = []
    processadas = 0
    erros = 0

    for indice, nome_imagem in enumerate(imagens, start=1):
        caminho_imagem = os.path.join(dataset_path, nome_imagem)
        print(f"[{indice}/{len(imagens)}] Processando imagem: {nome_imagem}")

        try:
            processor = PIDImageProcessor(caminho_imagem)

            original, processed = processor.process_pipeline(
                threshold_method="otsu",
                min_area=500
            )

            tags_encontradas = getattr(processor, 'detected_tags', [])
            nome_resultado_png = "resultado_" + nome_imagem

            if tags_encontradas:
                for tag in tags_encontradas:
                    match = df_referencia[df_referencia['TAG'].str.upper() == tag.upper()]
                    
                    if not match.empty:
                        tipo = match.iloc[0]['TIPO']
                        classe = match.iloc[0]['CLASSE']
                        status = "Identificado"
                    else:
                        tipo = "Não cadastrado"
                        classe = "Não cadastrado"
                        status = "Desconhecido"

                    relatorio_dados.append({
                        "Imagem_Original": nome_imagem,
                        "Imagem_Resultado": nome_resultado_png,
                        "TAG_Lida": tag,
                        "Tipo": tipo,
                        "Classe": classe,
                        "Status": status
                    })
                    print(f"    -> TAG: {tag} | Tipo: {tipo} | Classe: {classe}")
            else:
                relatorio_dados.append({
                    "Imagem_Original": nome_imagem,
                    "Imagem_Resultado": nome_resultado_png,
                    "TAG_Lida": "Nenhuma",
                    "Tipo": "N/A",
                    "Classe": "N/A",
                    "Status": "Sem leitura"
                })
                print("    Nenhuma TAG identificada.")

            # Salva a imagem estritamente no diretório /resultados da raiz
            caminho_saida_png = os.path.join(output_path, nome_resultado_png)
            sucesso = cv2.imwrite(caminho_saida_png, processed)

            if sucesso:
                processadas += 1
                print(f"    OK - Salvo em resultados/{nome_resultado_png}")
            else:
                erros += 1

        except Exception as e:
            erros += 1
            import traceback
            print(f"    ERRO ao processar {nome_imagem}: {e}")
            traceback.print_exc()

    # Salva a planilha final de resultados em CSV
    if relatorio_dados:
        df_relatorio = pd.DataFrame(relatorio_dados)
        caminho_csv_final = os.path.join(output_path, "relatorio_final.csv")
        df_relatorio.to_csv(caminho_csv_final, index=False, encoding="utf-8-sig")

    print("\n" + "=" * 60)
    print("PROCESSAMENTO FINALIZADO")
    print("=" * 60)
    print(f"Imagens processadas com sucesso: {processadas}/{len(imagens)}")
    print(f"Relatório gerado em: {os.path.join(output_path, 'relatorio_final.csv')}")
    print("=" * 60)


if __name__ == "__main__":
    main()