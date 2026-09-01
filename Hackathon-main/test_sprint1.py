import time
import os
import json
import pandas as pd
from projeto.image_processing import PIDImageProcessor, OCRReaderCache

def carregar_catalogo_tags(csv_path):
    df_referencia = pd.read_csv(csv_path)
    catalogo = {}
    for _, row in df_referencia.iterrows():
        tag = str(row["TAG"]).strip().upper()
        if tag:
            catalogo[tag] = {
                "tipo": row["TIPO"],
                "classe": row["CLASSE"],
            }
    return catalogo

def test_image(image_name, reader, catalogo):
    pasta_projeto = "projeto"
    dataset_path = os.path.join(pasta_projeto, "dataset")
    image_path = os.path.join(dataset_path, image_name)
    
    if not os.path.exists(image_path):
        print(f"Erro: {image_path} não encontrado.")
        return

    print(f"\n--- Testando {image_name} ---")
    start_time = time.time()
    
    try:
        processor = PIDImageProcessor(image_path, reader=reader, tag_catalog=catalogo)
        processor.process_pipeline(threshold_method="otsu", min_area=500)
        
        elapsed_time = time.time() - start_time
        stats = processor.region_stats
        detections = processor.detections
        
        identificados = [d for d in detections if d["status"] == "Identificado"]
        possiveis = [d for d in detections if d["status"] == "Possível TAG"]
        
        print(f"Regiões candidatas: {stats['contours_total']}")
        print(f"Enviadas ao OCR: {stats['regions_sent_to_ocr']}")
        print(f"Detecções 'Identificado': {len(identificados)}")
        print(f"Detecções 'Possível TAG': {len(possiveis)}")
        
        tags_identificadas = [d["tag"] for d in identificados]
        print(f"TAGs identificadas: {tags_identificadas}")
        print(f"Tempo: {elapsed_time:.2f}s")
        
        return {
            "image": image_name,
            "identificados": tags_identificadas,
            "success": True
        }
    except Exception as e:
        print(f"Erro ao processar {image_name}: {e}")
        return {"image": image_name, "success": False}

def main():
    csv_path = "tabela_equipamentos.csv"
    catalogo = carregar_catalogo_tags(csv_path)
    reader = OCRReaderCache.get_reader()
    
    results = []
    results.append(test_image("0.jpg", reader, catalogo))
    results.append(test_image("216.jpg", reader, catalogo))
    
    # Verificação de TAGs conhecidas (FC, FO, FL)
    tags_procuradas = {"FC", "FO", "FL"}
    tags_encontradas = set()
    for res in results:
        if res and res["success"]:
            for tag in res["identificados"]:
                if tag in tags_procuradas:
                    tags_encontradas.add(tag)
    
    perdidas = tags_procuradas - tags_encontradas
    print(f"\nTAGs conhecidas perdidas: {perdidas if perdidas else 'Nenhuma'}")

if __name__ == "__main__":
    main()
