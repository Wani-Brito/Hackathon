import re

import cv2
import easyocr


class OCRReaderCache:
    _reader = None

    @classmethod
    def get_reader(cls):
        if cls._reader is None:
            cls._reader = easyocr.Reader(["en"], gpu=False, verbose=False)
        return cls._reader


class PIDImageProcessor:
    # Lista explícita e documentada de prefixos técnicos comuns em P&ID (ISA-5.1 e equipamentos industriais).
    TECHNICAL_PREFIXES = {
        # Pressão
        "PT", "PSL", "PSLL", "PSV", "PSE", "PAL", "PAH", "PAHH", "PC", "PI", "PIT", "PDT", "PDS", "PDSH",
        # Nível
        "LT", "LSH", "LSL", "LSHL", "LAH", "LAL", "LAHH", "LALL", "LC", "LI", "LG", "LIT", "LS", "LDT",
        # Temperatura
        "TT", "TE", "TY", "TSH", "TSL", "TAH", "TAL", "TC", "TI", "TIT", "TW", "TD", "TDT",
        # Vazão
        "FT", "FE", "FC", "FI", "FIT", "FAH", "FAL", "FV", "FS", "FQ", "FQT", "FQI", "FF",
        # Válvulas e Atuadores
        "HV", "XV", "PV", "TV", "LV", "FV", "ASV", "CV", "SDV", "BDV", "MOV", "SOV", "PRV",
        # Controladores e Intertravamentos
        "ASC", "TIC", "PIC", "LIC", "FIC", "AIC", "SIC", "YIC", "KOD", "CSO", "CSC", "PY",
        # Posição / Analisadores / Chaves
        "ZSH", "ZSL", "ZT", "ZC", "ZI", "AT", "AC", "AI", "ASH", "ASL", "AF", "AS",
        # Equipamentos Mecânicos
        "V", "P", "E", "T", "C", "K", "M", "TK", "B", "R", "D", "S",
        # Estados de Falha de Válvula
        "FO", "FC", "FL", "FL/DO", "FL/DC",
    }

    # TAGs / Abreviações técnicas válidas para emissão como TAG autônoma (sem necessidade de número de malha)
    STANDALONE_TECHNICAL_TAGS = {
        "FO", "FC", "FL", "FL/DO", "FL/DC",
        "TC", "FC", "PC", "LC", "FE", "HV",
        "ASC", "ASV", "CSO", "CSC", "KOD",
    }

    # Palavras e textos técnicos comuns em diagramas que NÃO devem ser promovidos a TAG
    STOPWORDS = {
        "NOTE", "WATER", "PUMP", "TANK", "SAFE", "VENT", "DRAIN", "FLARE", "EAU",
        "TEMP", "LEVEL", "FLOW", "VALVE", "OPEN", "CLOSE", "MOTOR", "USING", "BARREL",
        "TOTAL", "AREA", "DATE", "DRAW", "SCALE", "PAGE", "TYPE", "LINE", "INCH",
        "SPEC", "PIPE", "FROM", "TO", "BY", "FOR", "AND", "THE", "ALL", "SET",
        "MAX", "MIN", "HIGH", "LOW", "AUTO", "MAN", "MANUAL", "SUPPLY", "RETURN",
        "INLET", "OUTLET", "SAMPLE", "GAUGE", "PANEL", "FIELD", "LOCAL", "ALARM",
        "TRIP", "STOP", "START", "RUN", "FAIL", "POWER", "HEAT", "AIR", "GAS", "OIL",
        "CHEMICAL", "PRODUCT", "STORAGE", "VENDOR", "COMPRESSOR", "LOCATION", "AFTERCOOLER",
        "SUCTION", "DISCHARGE", "INTERMITTENT", "BLOWDOWN", "RECIRCULATION",
    }

    TECHNICAL_TAG_PATTERN = re.compile(
        r"^(?:[A-Z]{1,4}[-_]?\d{1,5}[A-Z]?|[A-Z]{1,4}[/-][A-Z]{1,3}|FL/DC|FL/DO|FO|FC|FL)$"
    )

    def __init__(self, image_path, reader=None, tag_catalog=None, logger=print):
        self.original_image = cv2.imread(image_path)
        if self.original_image is None:
            raise ValueError(f"Não foi possível carregar a imagem: {image_path}")

        self.gray_image = None
        self.blurred_image = None
        self.threshold_image = None
        self.contours = None
        self.image_with_boxes = None
        self.detected_tags = []
        self.detections = []
        self.ocr_results = []
        self.ocr_errors = []
        self.region_stats = self._empty_region_stats()

        self.reader = reader or OCRReaderCache.get_reader()
        self.tag_catalog = tag_catalog or {}
        self.logger = logger

    @staticmethod
    def _empty_region_stats():
        return {
            "contours_total": 0,
            "regions_sent_to_ocr": 0,
            "regions_rejected": 0,
            "ocr_texts": 0,
            "valid_detections": 0,
        }

    def convert_to_grayscale(self):
        self.gray_image = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2GRAY)
        return self.gray_image

    def apply_blur(self, kernel_size=(5, 5)):
        if self.gray_image is None:
            self.convert_to_grayscale()

        self.blurred_image = cv2.GaussianBlur(self.gray_image, kernel_size, 0)
        return self.blurred_image

    def apply_threshold(self, threshold_value=127, method="binary"):
        if self.blurred_image is None:
            self.apply_blur()

        if method == "otsu":
            _, self.threshold_image = cv2.threshold(
                self.blurred_image,
                0,
                255,
                cv2.THRESH_BINARY + cv2.THRESH_OTSU,
            )
        else:
            _, self.threshold_image = cv2.threshold(
                self.blurred_image,
                threshold_value,
                255,
                cv2.THRESH_BINARY,
            )

        return self.threshold_image

    def detect_contours(self):
        if self.threshold_image is None:
            self.apply_threshold()

        contours, _ = cv2.findContours(
            self.threshold_image,
            cv2.RETR_TREE,
            cv2.CHAIN_APPROX_SIMPLE,
        )

        self.contours = contours
        return contours

    @classmethod
    def _clean_ocr_text(cls, text):
        t = re.sub(r"\s+", " ", text or "").strip().upper()
        # Normalização contextual segura para falhas de válvula com barra (ex: FLIDO -> FL/DO)
        t = re.sub(r"\bFL[I1/|]D[O0]\b", "FL/DO", t)
        t = re.sub(r"\bFL[I1/|]DC\b", "FL/DC", t)
        # Unifica espaços em hífens para tags compostas (ex: PT - 0004 -> PT-0004)
        t = re.sub(r"([A-Z]{1,4})\s*[-_]\s*(\d{1,5}[A-Z]?)", r"\1-\2", t)
        # Correção contextual segura: loop de 4 dígitos terminado em 8 lido no lugar de B (ex: PSLL-00168 -> PSLL-0016B)
        t = re.sub(r"^(PSLL|PSL|PSV|PT|LT|TT|FT|LSH|LSL|LAH|LAL)-(\d{4})8$", r"\1-\2B", t)
        return t

    @classmethod
    def _normalize_tag(cls, text):
        return re.sub(r"[^A-Z0-9/.-]", "", cls._clean_ocr_text(text))

    def _extract_known_tag(self, text):
        normalized_text = self._clean_ocr_text(text)
        compact_text = self._normalize_tag(text)

        if compact_text in self.tag_catalog:
            return compact_text

        tokens = re.findall(r"[A-Z0-9]+(?:/[A-Z0-9]+)?", normalized_text)
        for token in tokens:
            if token in self.tag_catalog:
                return token

        return None

    @classmethod
    def _is_possible_technical_tag(cls, text):
        tag = cls._normalize_tag(text)
        if len(tag) < 2 or len(tag) > 15:
            return False
        if tag in cls.STOPWORDS:
            return False
        if tag.isdigit():
            return False

        # Rejeita palavras comuns compostas com números (ex: TANK2, PUMP1, NOTE3)
        base_letters = re.match(r"^[A-Z]+", tag)
        if base_letters and base_letters.group(0) in cls.STOPWORDS:
            return False

        # Caso 1: TAG com sufixo numérico (ex: PT-0004, PSL-0003, V-001, LT210, ZSH1, AF2)
        if any(c.isdigit() for c in tag):
            m = re.match(r"^([A-Z]{1,4})[-_]?(\d{1,5}[A-Z]?)$", tag)
            if m:
                prefix = m.group(1)
                # Prefixo deve ser estritamente técnico
                if prefix in cls.TECHNICAL_PREFIXES:
                    # Para equipamentos mecânicos de letra única (V, P, E, T, C, K, M), exige hífen (ex: V-001, P-101)
                    if len(prefix) == 1:
                        return "-" in tag
                    return True
            return False

        # Caso 2: Abreviação técnica autônoma sem número (ex: TC, PC, FC, LC, FE, HV, ASC, ASV, KOD, CSO, FO, FC, FL)
        if tag in cls.STANDALONE_TECHNICAL_TAGS:
            return True

        return False

    def _region_looks_useful_for_ocr(self, x, y, w, h, contour_area, min_area):
        image_h, image_w = self.original_image.shape[:2]
        image_area = image_w * image_h
        box_area = w * h

        min_width = max(18, int(image_w * 0.004))
        min_height = max(8, int(image_h * 0.004))
        max_width = int(image_w * 0.60)
        max_height = int(image_h * 0.35)
        max_box_area = image_area * 0.22

        if contour_area < min_area:
            return False
        if box_area <= 0 or box_area > max_box_area:
            return False
        if w < min_width or h < min_height:
            return False
        if w > max_width or h > max_height:
            return False

        aspect_ratio = w / float(h)
        if aspect_ratio < 0.25 or aspect_ratio > 14:
            return False

        fill_ratio = contour_area / float(box_area)
        if fill_ratio < 0.01:
            return False

        return True

    @classmethod
    def _infer_group(cls, tag, status, tipo=None, classe=None):
        tag_norm = cls._normalize_tag(tag)

        if status == "Identificado":
            if classe == "Equipamento" or tipo == "Motor":
                return "Equipamentos"
            if classe == "Falha de Válvula" or tipo == "Válvula":
                return "Válvulas / Atuadores"
            if classe == "Instrumento":
                return "Instrumentação"
            return "Instrumentação"

        m = re.match(r"^([A-Z]{1,4})", tag_norm)
        if not m:
            return "Não cadastrado"
        prefix = m.group(1)

        # 1. Segurança / Proteção
        if prefix in {
            "PSV", "PSE", "SDV", "BDV", "PRV", "KOD", "CSO", "CSC", "PAHH", "LAHH", "LALL"
        }:
            return "Segurança / Proteção"

        # 2. Válvulas / Atuadores
        if prefix in {
            "FV", "HV", "XV", "PV", "TV", "LV", "CV", "MOV", "SOV", "ASV",
            "FO", "FC", "FL"
        }:
            return "Válvulas / Atuadores"

        # 3. Controle
        if prefix in {
            "FIC", "TIC", "PIC", "LIC", "AIC", "SIC", "YIC", "ASC", "TC", "PC", "FC", "LC", "AC", "PY"
        }:
            return "Controle"

        # 4. Instrumentação
        if prefix in {
            "PT", "PSL", "PSLL", "PAL", "PAH", "PI", "PIT", "PDT", "PDS", "PDSH",
            "LT", "LSH", "LSL", "LSHL", "LAH", "LAL", "LG", "LIT", "LS", "LDT",
            "TT", "TE", "TY", "TSH", "TSL", "TAH", "TAL", "TI", "TIT", "TW", "TD", "TDT",
            "FT", "FE", "FI", "FIT", "FAH", "FAL", "FS", "FQ", "FQT", "FQI", "FF",
            "ZSH", "ZSL", "ZT", "ZC", "ZI", "AT", "AI", "ASH", "ASL", "AF", "AS"
        }:
            return "Instrumentação"

        # 5. Equipamentos
        if prefix in {"V", "P", "E", "T", "C", "K", "M", "TK", "B", "R", "D", "S"}:
            return "Equipamentos"

        return "Não cadastrado"

    def _build_detection(self, text, confidence, bbox, is_recomposed=False):
        texto_ocr = self._clean_ocr_text(text)
        known_tag = self._extract_known_tag(texto_ocr)

        # 1. Catálogo exato -> Identificado
        if known_tag:
            reference = self.tag_catalog[known_tag]
            tipo = reference.get("tipo", "Não cadastrado")
            classe = reference.get("classe", "Não cadastrado")
            grupo = reference.get("grupo") or self._infer_group(known_tag, "Identificado", tipo, classe)
            return {
                "texto_ocr": texto_ocr,
                "tag": known_tag,
                "tipo": tipo,
                "classe": classe,
                "grupo": grupo,
                "status": "Identificado",
                "confidence": round(float(confidence), 4),
                "bbox": bbox,
                "is_recomposed": is_recomposed,
            }

        # 2. Fora do catálogo mas sintaticamente válida -> Possível TAG
        possible_tag = self._normalize_tag(texto_ocr)
        if self._is_possible_technical_tag(texto_ocr):
            grupo = self._infer_group(possible_tag, "Possível TAG")
            return {
                "texto_ocr": texto_ocr,
                "tag": possible_tag,
                "tipo": "Não cadastrado",
                "classe": "Não cadastrado",
                "grupo": grupo,
                "status": "Possível TAG",
                "confidence": round(float(confidence), 4),
                "bbox": bbox,
                "is_recomposed": is_recomposed,
            }

        return None

    @classmethod
    def _recompose_split_tags(cls, raw_items, tag_catalog=None):
        if not raw_items:
            return []

        tag_catalog = tag_catalog or {}
        complete_items = []
        prefix_items = []
        number_items = []

        for item in raw_items:
            norm = item["norm"]
            clean = item["text"]

            # 1. Catálogo
            if norm in tag_catalog or clean in tag_catalog:
                complete_items.append(item)
                continue

            # 2. TAG completa contendo letras e números
            if any(c.isalpha() for c in norm) and any(c.isdigit() for c in norm):
                if cls._is_possible_technical_tag(norm):
                    complete_items.append(item)
                continue

            # 3. Sufixo numérico puro (1 a 5 dígitos ou dígitos com letra sufixo ex: 0016B, 0004)
            if re.match(r"^\d{1,5}[A-Z]?$", norm):
                if not re.search(r'["\'#]|PO\d|PA\d|\d+["\']', clean):
                    number_items.append(item)
                continue

            # 4. Prefixo técnico de instrumento
            if norm in cls.TECHNICAL_PREFIXES and norm not in cls.STOPWORDS:
                prefix_items.append(item)

        used_prefix_indices = set()
        recomposed_detections = []

        for p_idx, p in enumerate(prefix_items):
            best_n = None
            best_dist = float("inf")

            p_box = p["bbox"]
            p_cx = p_box["x"] + p_box["width"] / 2.0
            p_cy = p_box["y"] + p_box["height"] / 2.0

            for n in number_items:
                n_box = n["bbox"]
                n_cx = n_box["x"] + n_box["width"] / 2.0
                n_cy = n_box["y"] + n_box["height"] / 2.0
                candidate_tag = cls._clean_ocr_text(f"{p['norm']}-{n['norm']}")
                catalog_bonus = 120 if candidate_tag in tag_catalog else 0
                suffix_bonus = 40 if re.search(r"\d[A-Z]$", n["norm"]) else 0

                # Cenário A: Alinhamento Vertical (ISA Bubble)
                dy = n_box["y"] - (p_box["y"] + p_box["height"])
                dx_center = abs(p_cx - n_cx)
                max_dy = max(p_box["height"] * 1.8, 35)
                max_dx = max(p_box["width"], n_box["width"]) * 0.9

                if -5 <= dy <= max_dy and dx_center <= max_dx:
                    dist = dx_center * 1.5 + dy - catalog_bonus - suffix_bonus
                    if dist < best_dist:
                        best_dist = dist
                        best_n = n
                    continue

                # Cenário B: Alinhamento Horizontal (Prefixo + Número)
                dx = n_box["x"] - (p_box["x"] + p_box["width"])
                dy_center = abs(p_cy - n_cy)
                max_dx_h = max(p_box["width"] * 1.5, 30)
                max_dy_h = max(p_box["height"], n_box["height"]) * 0.6

                if -5 <= dx <= max_dx_h and dy_center <= max_dy_h:
                    dist = dx + dy_center * 1.5 - catalog_bonus - suffix_bonus
                    if dist < best_dist:
                        best_dist = dist
                        best_n = n

            if best_n is not None:
                used_prefix_indices.add(p_idx)

                composed_raw = f"{p['norm']}-{best_n['norm']}"
                composed_tag = cls._clean_ocr_text(composed_raw)
                n_box = best_n["bbox"]

                combined_x = min(p_box["x"], n_box["x"])
                combined_y = min(p_box["y"], n_box["y"])
                combined_w = max(p_box["x"] + p_box["width"], n_box["x"] + n_box["width"]) - combined_x
                combined_h = max(p_box["y"] + p_box["height"], n_box["y"] + n_box["height"]) - combined_y
                combined_bbox = {
                    "x": int(combined_x),
                    "y": int(combined_y),
                    "width": int(combined_w),
                    "height": int(combined_h),
                }

                combined_conf = round((p["prob"] + best_n["prob"]) / 2.0, 4)

                recomposed_detections.append({
                    "texto_ocr": f"{p['text']} {best_n['text']}",
                    "tag": composed_tag,
                    "confidence": combined_conf,
                    "bbox": combined_bbox,
                    "is_recomposed": True,
                })

        final_detections = []

        for item in complete_items:
            final_detections.append({
                "texto_ocr": item["text"],
                "tag": item["norm"],
                "confidence": item["prob"],
                "bbox": item["bbox"],
                "is_recomposed": False,
            })

        final_detections.extend(recomposed_detections)

        # Apenas prefixos pertencentes a STANDALONE_TECHNICAL_TAGS são emitidos isoladamente
        for p_idx, p in enumerate(prefix_items):
            if p_idx not in used_prefix_indices:
                if p["norm"] in cls.STANDALONE_TECHNICAL_TAGS or p["norm"] in tag_catalog:
                    final_detections.append({
                        "texto_ocr": p["text"],
                        "tag": p["norm"],
                        "confidence": p["prob"],
                        "bbox": p["bbox"],
                        "is_recomposed": False,
                    })

        return final_detections

    def draw_bounding_boxes(self, min_area=500):
        if self.contours is None:
            self.detect_contours()

        self.image_with_boxes = self.original_image.copy()
        self.detected_tags = []
        self.detections = []
        self.ocr_results = []
        self.ocr_errors = []
        self.region_stats = self._empty_region_stats()
        self.region_stats["contours_total"] = len(self.contours)

        raw_ocr_items = []
        box_count = 0

        for contour in self.contours:
            area = cv2.contourArea(contour)
            x, y, w, h = cv2.boundingRect(contour)

            if not self._region_looks_useful_for_ocr(x, y, w, h, area, min_area):
                self.region_stats["regions_rejected"] += 1
                continue

            roi = self.original_image[y : y + h, x : x + w]
            bbox = {
                "x": int(x),
                "y": int(y),
                "width": int(w),
                "height": int(h),
            }

            if roi.size > 0:
                try:
                    self.region_stats["regions_sent_to_ocr"] += 1
                    results = self.reader.readtext(roi)
                    for sub_box, text, prob in results:
                        clean_text = self._clean_ocr_text(text)
                        if not clean_text or prob < 0.35:
                            continue

                        # Strip pontuação inicial/final (ex: "(LSHL" → "LSHL")
                        # Rejeita apenas se brackets/chars estranhos forem INTERNOS ao token
                        text_stripped = re.sub(r"^[()\[\]<>.,\-_\s]+|[()\[\]<>.,\-_\s]+$", "", text)
                        if not text_stripped:
                            continue
                        if re.search(r"[\]\[\{\}\<\>]", text_stripped):
                            continue
                        # Usa o texto sem pontuação exterior daqui em diante
                        text = text_stripped

                        # Rejeita códigos de linha com polegadas / tubulação
                        if re.search(r'["\'#]|PO\d|PA\d|\d+["\']', text):
                            continue

                        if sub_box and len(sub_box) == 4:
                            sub_xs = [pt[0] for pt in sub_box]
                            sub_ys = [pt[1] for pt in sub_box]
                            gx = int(x + min(sub_xs))
                            gy = int(y + min(sub_ys))
                            gw = int(max(sub_xs) - min(sub_xs))
                            gh = int(max(sub_ys) - min(sub_ys))
                            item_bbox = {"x": gx, "y": gy, "width": gw, "height": gh}
                        else:
                            item_bbox = bbox

                        self.region_stats["ocr_texts"] += 1
                        self.ocr_results.append(
                            {
                                "texto_ocr": clean_text,
                                "confidence": round(float(prob), 4),
                                "bbox": item_bbox,
                            }
                        )

                        raw_ocr_items.append({
                            "text": clean_text,
                            "norm": self._normalize_tag(clean_text),
                            "prob": round(float(prob), 4),
                            "bbox": item_bbox,
                        })

                except Exception as exc:
                    message = f"OCR falhou na bbox {bbox}: {exc}"
                    self.ocr_errors.append(message)
                    if self.logger:
                        self.logger(f"    AVISO: {message}")

        recomposed_items = self._recompose_split_tags(raw_ocr_items, tag_catalog=self.tag_catalog)

        seen_detections = set()
        for item in recomposed_items:
            detection = self._build_detection(
                item["tag"],
                item["confidence"],
                item["bbox"],
                is_recomposed=item.get("is_recomposed", False),
            )
            if detection is None:
                continue

            detection_key = (detection["tag"], detection["bbox"]["x"], detection["bbox"]["y"])
            if detection_key in seen_detections:
                continue

            seen_detections.add(detection_key)
            self.detections.append(detection)
            self.region_stats["valid_detections"] += 1
            if detection["tag"] not in self.detected_tags:
                self.detected_tags.append(detection["tag"])

            color = (0, 255, 0) if detection["status"] == "Identificado" else (0, 180, 255)
            dx = detection["bbox"]["x"]
            dy = detection["bbox"]["y"]
            dw = detection["bbox"]["width"]
            dh = detection["bbox"]["height"]
            cv2.rectangle(self.image_with_boxes, (dx, dy), (dx + dw, dy + dh), color, 2)
            cv2.putText(
                self.image_with_boxes,
                detection["tag"],
                (dx, max(15, dy - 6)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                color,
                2,
            )
            box_count += 1

        return self.image_with_boxes

    def process_pipeline(self, threshold_method="otsu", min_area=500):
        self.convert_to_grayscale()
        self.apply_blur()
        self.apply_threshold(method=threshold_method)
        self.detect_contours()
        self.draw_bounding_boxes(min_area=min_area)
        return self.original_image, self.image_with_boxes

    def get_processed_images(self):
        return {
            "original": self.original_image,
            "grayscale": self.gray_image,
            "blurred": self.blurred_image,
            "threshold": self.threshold_image,
            "with_boxes": self.image_with_boxes,
            "detections": self.detections,
            "ocr_results": self.ocr_results,
            "ocr_errors": self.ocr_errors,
            "region_stats": self.region_stats,
        }
