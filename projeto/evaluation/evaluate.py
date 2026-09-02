import argparse
import csv
import json
import os
import pathlib
import sys
import time
from collections import defaultdict

# Garante importação dos módulos do projeto
BASE_DIR = pathlib.Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

from projeto.api import carregar_catalogo
from projeto.image_processing import OCRReaderCache, PIDImageProcessor


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Avaliação quantitativa do pipeline OCR/P&ID contra Ground Truth real."
    )
    parser.add_argument(
        "--ground-truth",
        type=str,
        default=str(BASE_DIR / "projeto" / "evaluation" / "ground_truth.csv"),
        help="Caminho para o CSV de Ground Truth.",
    )
    parser.add_argument(
        "--dataset",
        type=str,
        default=str(BASE_DIR / "projeto" / "dataset"),
        help="Diretório onde estão as imagens do dataset.",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=str(BASE_DIR / "projeto" / "evaluation" / "results"),
        help="Diretório de saída para os resultados da avaliação.",
    )
    return parser.parse_args()


def carregar_ground_truth(gt_path):
    """
    Carrega anotações de Ground Truth agrupadas por nome de arquivo de imagem.
    Retorna dict: { image_name: [ {tag, tipo, classe, status}, ... ] }
    """
    if not os.path.exists(gt_path):
        return {}

    gt_data = defaultdict(list)
    with open(gt_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            img = row.get("image", "").strip()
            tag = row.get("tag", "").strip().upper()
            if not img or not tag:
                continue
            gt_data[img].append({
                "tag": tag,
                "tipo": row.get("tipo", "").strip(),
                "classe": row.get("classe", "").strip(),
                "status": row.get("status", "").strip(),
            })

    return gt_data


def extrair_unique_detections(detections):
    """Deduplica detecções por TAG mantendo a maior confiança."""
    unique = {}
    for d in detections:
        tag = d.get("tag", "").strip().upper()
        if not tag:
            continue
        if tag not in unique or d.get("confidence", 0) > unique[tag].get("confidence", 0):
            unique[tag] = d
    return unique


def calcular_metricas_binarias(tp, fp, fn):
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    return {
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1_score": round(f1, 4),
    }


def gerar_matriz_confusao(y_true, y_pred, labels):
    """Gera matriz de confusão tabular estruturada."""
    matriz = {l_true: {l_pred: 0 for l_pred in labels} for l_true in labels}
    for t, p in zip(y_true, y_pred):
        if t in matriz and p in matriz[t]:
            matriz[t][p] += 1
    return matriz


def main():
    args = parse_arguments()
    gt_path = pathlib.Path(args.ground_truth)
    dataset_dir = pathlib.Path(args.dataset)
    out_dir = pathlib.Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 70)
    print("SISTEMA DE AVALIAÇÃO QUANTITATIVA — TAGVision P&ID")
    print("=" * 70)
    print(f"Ground Truth: {gt_path}")
    print(f"Dataset:      {dataset_dir}")
    print(f"Resultados:   {out_dir}")
    print("-" * 70)

    gt_data = carregar_ground_truth(gt_path)
    total_imagens_gt = len(gt_data)
    total_tags_gt = sum(len(items) for items in gt_data.values())

    if total_imagens_gt == 0:
        print("\n[AVISO] O arquivo de ground_truth.csv está vazio ou não possui anotações válidas.")
        print("Para realizar uma avaliação quantitativa real, adicione anotações em:")
        print(f"  {gt_path}")
        print("\nEstrutura esperada:")
        print("  image,tag,tipo,classe,status")
        print("  0.jpg,FO,Fail Open,Falha de Válvula,Identificado")
        
        # Salva sumário vazio consistente
        empty_summary = {
            "status": "empty_ground_truth",
            "evaluated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "total_images_in_ground_truth": 0,
            "total_ground_truth_tags": 0,
            "metrics": {
                "tp": 0,
                "fp": 0,
                "fn": 0,
                "precision": 0.0,
                "recall": 0.0,
                "f1_score": 0.0,
            },
            "per_image_results": [],
            "recommendation": "Rotule uma amostra inicial de imagens em ground_truth.csv para gerar métricas reais.",
        }
        with open(out_dir / "metrics_summary.json", "w", encoding="utf-8") as f:
            json.dump(empty_summary, f, indent=2, ensure_ascii=False)
        return

    print(f"Imagens anotadas no Ground Truth: {total_imagens_gt}")
    print(f"Total de TAGs no Ground Truth:    {total_tags_gt}")
    print("-" * 70)

    # Carrega catálogo e inicializa OCR Reader
    catalogo = carregar_catalogo()
    reader = OCRReaderCache.get_reader()

    per_image_results = []
    global_tp = 0
    global_fp = 0
    global_fn = 0
    global_detected_count = 0

    y_true_status = []
    y_pred_status = []

    for img_name, gt_items in gt_data.items():
        img_path = dataset_dir / img_name
        if not img_path.exists():
            print(f"[PULADO] Imagem não encontrada: {img_path}")
            continue

        print(f"Processando imagem: {img_name} ({len(gt_items)} TAGs de ground truth)...")
        processor = PIDImageProcessor(str(img_path), reader=reader, tag_catalog=catalogo)
        processor.process_pipeline(threshold_method="otsu", min_area=500)

        detected_map = extrair_unique_detections(processor.detections)
        gt_tags_set = {item["tag"].upper() for item in gt_items}
        detected_tags_set = set(detected_map.keys())

        # Cálculo de TP, FP, FN
        tp_tags = gt_tags_set & detected_tags_set
        fp_tags = detected_tags_set - gt_tags_set
        fn_tags = gt_tags_set - detected_tags_set

        tp = len(tp_tags)
        fp = len(fp_tags)
        fn = len(fn_tags)

        global_tp += tp
        global_fp += fp
        global_fn += fn
        global_detected_count += len(detected_tags_set)

        img_metrics = calcular_metricas_binarias(tp, fp, fn)

        # Matriz de confusão de Status para TPs
        gt_status_map = {item["tag"].upper(): item.get("status", "Desconhecido") for item in gt_items}
        for tag in tp_tags:
            y_true_status.append(gt_status_map.get(tag, "Desconhecido"))
            y_pred_status.append(detected_map[tag].get("status", "Desconhecido"))

        per_image_results.append({
            "image": img_name,
            "gt_tags_count": len(gt_tags_set),
            "detected_tags_count": len(detected_tags_set),
            "tp": tp,
            "fp": fp,
            "fn": fn,
            "precision": img_metrics["precision"],
            "recall": img_metrics["recall"],
            "f1_score": img_metrics["f1_score"],
            "tp_tags": sorted(list(tp_tags)),
            "fp_tags": sorted(list(fp_tags)),
            "fn_tags": sorted(list(fn_tags)),
        })

    # Métricas Globais
    global_metrics = calcular_metricas_binarias(global_tp, global_fp, global_fn)

    print("-" * 70)
    print("RESULTADOS GLOBAIS DE DETECÇÃO DE TAGs:")
    print(f"  True Positives (TP):  {global_tp}")
    print(f"  False Positives (FP): {global_fp}")
    print(f"  False Negatives (FN): {global_fn}")
    print(f"  Precision:            {global_metrics['precision']:.4f} ({global_metrics['precision']*100:.1f}%)")
    print(f"  Recall:               {global_metrics['recall']:.4f} ({global_metrics['recall']*100:.1f}%)")
    print(f"  F1-Score:             {global_metrics['f1_score']:.4f}")
    print("-" * 70)

    # 1. Salva metrics_summary.json
    summary_output = {
        "status": "success",
        "evaluated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "total_images_evaluated": len(per_image_results),
        "total_ground_truth_tags": total_tags_gt,
        "total_detected_tags": global_detected_count,
        "global_metrics": {
            "tp": global_tp,
            "fp": global_fp,
            "fn": global_fn,
            "precision": global_metrics["precision"],
            "recall": global_metrics["recall"],
            "f1_score": global_metrics["f1_score"],
        },
        "per_image_results": per_image_results,
    }

    with open(out_dir / "metrics_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary_output, f, indent=2, ensure_ascii=False)
    print(f"[OK] Salvo: {out_dir / 'metrics_summary.json'}")

    # 2. Salva evaluation_per_image.csv
    csv_per_image = out_dir / "evaluation_per_image.csv"
    with open(csv_per_image, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "image",
                "gt_tags_count",
                "detected_tags_count",
                "tp",
                "fp",
                "fn",
                "precision",
                "recall",
                "f1_score",
                "tp_tags",
                "fp_tags",
                "fn_tags",
            ],
        )
        writer.writeheader()
        for row in per_image_results:
            row_copy = row.copy()
            row_copy["tp_tags"] = "; ".join(row["tp_tags"])
            row_copy["fp_tags"] = "; ".join(row["fp_tags"])
            row_copy["fn_tags"] = "; ".join(row["fn_tags"])
            writer.writerow(row_copy)
    print(f"[OK] Salvo: {csv_per_image}")

    # 3. Salva Matriz de Confusão de Status (se houver dados suficientes)
    if y_true_status and y_pred_status:
        labels_status = ["Identificado", "Possível TAG", "Desconhecido"]
        cm = gerar_matriz_confusao(y_true_status, y_pred_status, labels_status)
        cm_csv = out_dir / "confusion_matrix_status.csv"
        with open(cm_csv, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["True_Status \\ Pred_Status"] + labels_status)
            for l_true in labels_status:
                writer.writerow([l_true] + [cm[l_true][l_pred] for l_pred in labels_status])
        print(f"[OK] Salva: {cm_csv}")

    print("=" * 70)
    print("AVALIAÇÃO CONCLUÍDA COM SUCESSO!")
    print("=" * 70)


if __name__ == "__main__":
    main()
