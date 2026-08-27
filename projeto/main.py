import cv2
import os
import sys
import re
import json
import pandas as pd
from image_processing import OCRReaderCache, PIDImageProcessor


def extrair_numero(nome_arquivo):
    """Extrai os números do nome do arquivo para ordenar numericamente (ex: 1, 2... 10, 11... 100)."""
    numeros = re.findall(r'\d+', nome_arquivo)
    return int(numeros[0]) if numeros else float('inf')


def carregar_catalogo_tags(csv_path):
    df_referencia = pd.read_csv(csv_path)
    colunas_obrigatorias = {"TAG", "TIPO", "CLASSE"}
    colunas_faltantes = colunas_obrigatorias.difference(df_referencia.columns)

    if colunas_faltantes:
        raise ValueError(
            "Colunas ausentes em tabela_equipamentos.csv: "
            + ", ".join(sorted(colunas_faltantes))
        )

    catalogo = {}
    for _, row in df_referencia.iterrows():
        tag = str(row["TAG"]).strip().upper()
        if tag:
            catalogo[tag] = {
                "tipo": row["TIPO"],
                "classe": row["CLASSE"],
            }

    return df_referencia, catalogo


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
        df_referencia, catalogo_tags = carregar_catalogo_tags(csv_path)
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
    pdfs = []

    for arquivo in todos_itens:
        caminho_completo = os.path.join(dataset_path, arquivo)
        
        # Garante que é um ARQUIVO (e não uma pasta) e que tem extensão de imagem
        if os.path.isfile(caminho_completo) and arquivo.lower().endswith(('.png', '.jpg', '.jpeg')):
            imagens.append(arquivo)
        elif os.path.isfile(caminho_completo) and arquivo.lower().endswith('.pdf'):
            pdfs.append(arquivo)

    # Ordenação REALMENTE NUMÉRICA (1, 2, 3... 9, 10, 11... 100)
    imagens.sort(key=extrair_numero)

    if not imagens:
        print("\nNenhuma imagem encontrada na pasta dataset.")
        sys.exit(1)

    print(f"\n{len(imagens)} imagens encontradas para processar.")
    if pdfs:
        pdfs.sort(key=extrair_numero)
        print(
            f"{len(pdfs)} PDF(s) encontrado(s), ainda não processados nesta sprint: "
            + ", ".join(pdfs)
        )
    print(f"Resultados serão salvos em: {output_path}")
    print("=" * 60)

    relatorio_dados = []
    processadas = 0
    erros = 0
    totais = {
        "contours_total": 0,
        "regions_sent_to_ocr": 0,
        "regions_rejected": 0,
        "ocr_texts": 0,
        "valid_detections": 0,
    }

    reader = OCRReaderCache.get_reader()

    for indice, nome_imagem in enumerate(imagens, start=1):
        caminho_imagem = os.path.join(dataset_path, nome_imagem)
        print(f"[{indice}/{len(imagens)}] Processando imagem: {nome_imagem}")

        try:
            processor = PIDImageProcessor(
                caminho_imagem,
                reader=reader,
                tag_catalog=catalogo_tags,
            )

            original, processed = processor.process_pipeline(
                threshold_method="otsu",
                min_area=500
            )

            detections = getattr(processor, 'detections', [])
            stats = getattr(processor, 'region_stats', {})
            for chave in totais:
                totais[chave] += stats.get(chave, 0)

            nome_resultado_png = "resultado_" + nome_imagem

            if detections:
                for detection in detections:
                    bbox = detection["bbox"]
                    relatorio_dados.append({
                        "Imagem_Original": nome_imagem,
                        "Imagem_Resultado": nome_resultado_png,
                        "texto_ocr": detection["texto_ocr"],
                        "tag": detection["tag"],
                        "tipo": detection["tipo"],
                        "classe": detection["classe"],
                        "status": detection["status"],
                        "confidence": detection["confidence"],
                        "bbox": json.dumps(bbox, ensure_ascii=False),
                        "bbox_x": bbox["x"],
                        "bbox_y": bbox["y"],
                        "bbox_width": bbox["width"],
                        "bbox_height": bbox["height"],
                    })
                    print(
                        f"    -> {detection['status']}: {detection['tag']} | "
                        f"Tipo: {detection['tipo']} | Classe: {detection['classe']} | "
                        f"Confiança: {detection['confidence']}"
                    )
            else:
                relatorio_dados.append({
                    "Imagem_Original": nome_imagem,
                    "Imagem_Resultado": nome_resultado_png,
                    "texto_ocr": "",
                    "tag": "",
                    "tipo": "N/A",
                    "classe": "N/A",
                    "status": "Sem detecção válida",
                    "confidence": "",
                    "bbox": "",
                    "bbox_x": "",
                    "bbox_y": "",
                    "bbox_width": "",
                    "bbox_height": "",
                })
                print("    Nenhuma TAG técnica válida identificada.")

            print(
                "    Estatísticas: "
                f"{stats.get('contours_total', 0)} contornos, "
                f"{stats.get('regions_sent_to_ocr', 0)} regiões no OCR, "
                f"{stats.get('ocr_texts', 0)} textos OCR, "
                f"{stats.get('valid_detections', 0)} detecções válidas"
            )

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
    print(
        "Totais: "
        f"{totais['contours_total']} contornos, "
        f"{totais['regions_sent_to_ocr']} regiões no OCR, "
        f"{totais['ocr_texts']} textos OCR, "
        f"{totais['valid_detections']} detecções válidas"
    )
    print(f"Relatório gerado em: {os.path.join(output_path, 'relatorio_final.csv')}")
    print("=" * 60)


if __name__ == "__main__":
    main()
