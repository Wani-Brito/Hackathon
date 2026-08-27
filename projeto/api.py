import os

import uuid
import shutil
import time
import pandas as pd
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from projeto.image_processing import PIDImageProcessor, OCRReaderCache

app = FastAPI(title="P&ID TAG OCR API")

# Configuração de diretórios
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMP_DIR = os.path.join(BASE_DIR, "temp")
RESULTS_DIR = os.path.join(BASE_DIR, "results_api")
CSV_PATH = os.path.join(os.path.dirname(BASE_DIR), "tabela_equipamentos.csv")

os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

# Servir arquivos estáticos (resultados)
app.mount("/results", StaticFiles(directory=RESULTS_DIR), name="results")

# Configuração de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cache do catálogo de TAGs
def carregar_catalogo():
    if not os.path.exists(CSV_PATH):
        return {}
    df = pd.read_csv(CSV_PATH)
    catalogo = {}
    for _, row in df.iterrows():
        tag = str(row["TAG"]).strip().upper()
        if tag:
            catalogo[tag] = {
                "tipo": row["TIPO"],
                "classe": row["CLASSE"],
            }
    return catalogo

CATALOGO = carregar_catalogo()

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.post("/process-image")
async def process_image(file: UploadFile = File(...)):
    # Validação de formato
    if not file.content_type in ["image/jpeg", "image/png", "image/jpg"]:
        raise HTTPException(status_code=400, detail="Formato de arquivo inválido. Use JPG ou PNG.")

    file_id = str(uuid.uuid4())
    extension = os.path.splitext(file.filename)[1]
    if not extension:
        extension = ".jpg"
    
    temp_filename = f"{file_id}{extension}"
    temp_path = os.path.join(TEMP_DIR, temp_filename)
    
    try:
        # Salva upload temporariamente
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        start_time = time.time()
        
        # Inicializa processador
        reader = OCRReaderCache.get_reader()
        processor = PIDImageProcessor(temp_path, reader=reader, tag_catalog=CATALOGO)
        
        # Executa pipeline
        original, processed = processor.process_pipeline(threshold_method="otsu", min_area=500)
        
        # Salva imagem processada
        result_filename = f"res_{temp_filename}"
        result_path = os.path.join(RESULTS_DIR, result_filename)
        import cv2
        cv2.imwrite(result_path, processed)
        
        elapsed_time = time.time() - start_time
        
        # Prepara resposta
        response = {
            "success": True,
            "original_image": file.filename,
            "processed_image_url": f"/results/{result_filename}",
            "detections": processor.detections,
            "stats": {
                "regions_total": processor.region_stats.get("contours_total", 0),
                "regions_sent_to_ocr": processor.region_stats.get("regions_sent_to_ocr", 0),
                "processing_time_seconds": round(elapsed_time, 2)
            }
        }
        
        return response

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erro no processamento: {str(e)}")
    
    finally:
        # Limpeza simples do arquivo temporário de upload
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except:
                pass

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
