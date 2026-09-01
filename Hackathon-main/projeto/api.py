import os

import uuid
import shutil
import time
import pandas as pd
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from projeto.image_processing import PIDImageProcessor, OCRReaderCache

app = FastAPI(title="P&ID TAG OCR API")

# Configuração de diretórios
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMP_DIR = os.path.join(BASE_DIR, "temp")
RESULTS_DIR = os.path.join(BASE_DIR, "results_api")
REPORTS_DIR = os.path.join(BASE_DIR, "reports_api")
CSV_PATH = os.path.join(os.path.dirname(BASE_DIR), "tabela_equipamentos.csv")

os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)

# Resultados ficam disponíveis enquanto o servidor estiver em execução para
# que o relatório seja gerado sem reprocessar a imagem enviada pelo usuário.
REPORTS = {}

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


def gerar_relatorio_pdf(report_path, report_data):
    """Gera um relatório visual de uma análise já concluída."""
    page_width, page_height = A4
    pdf = canvas.Canvas(report_path, pagesize=A4)
    margin = 18 * mm
    red = colors.HexColor("#ED161D")
    navy = colors.HexColor("#07142A")
    muted = colors.HexColor("#586A7D")

    # Cabeçalho
    pdf.setFillColor(navy)
    pdf.rect(0, page_height - 42 * mm, page_width, 42 * mm, fill=1, stroke=0)
    pdf.setFillColor(red)
    pdf.rect(0, page_height - 42 * mm, page_width, 3 * mm, fill=1, stroke=0)
    pdf.setFillColor(colors.white)
    pdf.setFont("Helvetica-BoldOblique", 25)
    pdf.drawString(margin, page_height - 20 * mm, "IASTECH")
    pdf.setFont("Helvetica", 9)
    pdf.drawString(margin, page_height - 27 * mm, "Industrial Automation")
    pdf.setFont("Helvetica-Bold", 13)
    pdf.drawRightString(page_width - margin, page_height - 20 * mm, "RELATORIO TAGVISION P&ID")
    pdf.setFont("Helvetica", 8)
    pdf.drawRightString(page_width - margin, page_height - 27 * mm, "Analise automatizada de planta industrial")

    y = page_height - 54 * mm
    pdf.setFillColor(navy)
    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(margin, y, "Resultado da analise")
    y -= 7 * mm
    pdf.setFont("Helvetica", 9)
    pdf.setFillColor(muted)
    pdf.drawString(margin, y, f"Arquivo analisado: {report_data['original_filename']}")
    y -= 10 * mm

    stats = report_data["stats"]
    cards = [
        ("TAGs identificadas", str(len(report_data["detections"]))),
        ("Regioes analisadas", str(stats.get("regions_sent_to_ocr", 0))),
        ("Tempo de processamento", f"{stats.get('processing_time_seconds', 0)} s"),
    ]
    card_width = (page_width - 2 * margin - 8 * mm) / 3
    for index, (label, value) in enumerate(cards):
        x = margin + index * (card_width + 4 * mm)
        pdf.setFillColor(colors.HexColor("#F2F5F7"))
        pdf.roundRect(x, y - 18 * mm, card_width, 18 * mm, 2 * mm, fill=1, stroke=0)
        pdf.setFillColor(red)
        pdf.setFont("Helvetica-Bold", 15)
        pdf.drawString(x + 4 * mm, y - 8 * mm, value)
        pdf.setFillColor(muted)
        pdf.setFont("Helvetica", 7.5)
        pdf.drawString(x + 4 * mm, y - 13 * mm, label)
    y -= 28 * mm

    image_path = report_data["processed_image_path"]
    if os.path.exists(image_path):
        image_width = page_width - 2 * margin
        image_height = min(82 * mm, y - 45 * mm)
        pdf.setFillColor(colors.HexColor("#F2F5F7"))
        pdf.rect(margin, y - image_height, image_width, image_height, fill=1, stroke=0)
        pdf.drawImage(
            image_path,
            margin,
            y - image_height,
            width=image_width,
            height=image_height,
            preserveAspectRatio=True,
            anchor="c",
        )
        y -= image_height + 10 * mm

    pdf.setFillColor(navy)
    pdf.setFont("Helvetica-Bold", 13)
    pdf.drawString(margin, y, "TAGs detectadas")
    y -= 7 * mm

    detections = report_data["detections"]
    if not detections:
        pdf.setFillColor(muted)
        pdf.setFont("Helvetica", 9)
        pdf.drawString(margin, y, "Nenhum equipamento cadastrado foi identificado nesta imagem.")
    else:
        columns = [margin, margin + 34 * mm, margin + 88 * mm, margin + 135 * mm]
        pdf.setFillColor(navy)
        pdf.rect(margin, y - 6 * mm, page_width - 2 * margin, 6 * mm, fill=1, stroke=0)
        pdf.setFillColor(colors.white)
        pdf.setFont("Helvetica-Bold", 7)
        for x, title in zip(columns, ["TAG", "TIPO", "CLASSE", "CONFIANCA"]):
            pdf.drawString(x + 2 * mm, y - 4 * mm, title)
        y -= 11 * mm

        for index, detection in enumerate(detections):
            if y < 25 * mm:
                pdf.showPage()
                y = page_height - 25 * mm
            if index % 2 == 0:
                pdf.setFillColor(colors.HexColor("#F4F6F8"))
                pdf.rect(margin, y - 5 * mm, page_width - 2 * margin, 6 * mm, fill=1, stroke=0)
            pdf.setFillColor(navy)
            pdf.setFont("Helvetica-Bold", 8)
            pdf.drawString(columns[0] + 2 * mm, y - 3.7 * mm, str(detection.get("tag", "-"))[:17])
            pdf.setFont("Helvetica", 7.5)
            pdf.drawString(columns[1] + 2 * mm, y - 3.7 * mm, str(detection.get("tipo", "-"))[:28])
            pdf.drawString(columns[2] + 2 * mm, y - 3.7 * mm, str(detection.get("classe", "-"))[:24])
            confidence = float(detection.get("confidence", 0)) * 100
            pdf.drawString(columns[3] + 2 * mm, y - 3.7 * mm, f"{confidence:.0f}%")
            y -= 6 * mm

    pdf.setFillColor(muted)
    pdf.setFont("Helvetica", 7)
    pdf.drawCentredString(page_width / 2, 12 * mm, "IASTECH - Solucoes em automacao industrial")
    pdf.save()

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
        report_id = str(uuid.uuid4())
        REPORTS[report_id] = {
            "original_filename": file.filename,
            "processed_image_path": result_path,
            "detections": processor.detections,
            "stats": {
                "regions_sent_to_ocr": processor.region_stats.get("regions_sent_to_ocr", 0),
                "processing_time_seconds": round(elapsed_time, 2),
            },
        }

        response = {
            "success": True,
            "report_id": report_id,
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


@app.get("/download-report/{report_id}")
async def download_report(report_id: str):
    report_data = REPORTS.get(report_id)
    if not report_data:
        raise HTTPException(status_code=404, detail="Resultado não encontrado. Faça uma nova análise para gerar o relatório.")

    report_path = os.path.join(REPORTS_DIR, f"relatorio_tagvision_{report_id}.pdf")
    gerar_relatorio_pdf(report_path, report_data)
    return FileResponse(
        report_path,
        media_type="application/pdf",
        filename="relatorio_tagvision_pid.pdf",
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
