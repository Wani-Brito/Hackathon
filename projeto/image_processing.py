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
    TECHNICAL_TAG_PATTERN = re.compile(
        r"^(?:[A-Z]{1,4}\d{2,4}[A-Z]?|[A-Z]{1,4}[/-][A-Z]{1,3}|FL/DC|FL/DO|FO|FC|FL)$"
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
        self.tag_prefixes = self._build_tag_prefixes(self.tag_catalog)
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

    @staticmethod
    def _build_tag_prefixes(tag_catalog):
        prefixes = set()
        for tag in tag_catalog:
            match = re.match(r"[A-Z]+", tag)
            if match:
                prefixes.add(match.group(0))
        return prefixes

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

    @staticmethod
    def _clean_ocr_text(text):
        return re.sub(r"\s+", " ", text or "").strip().upper()

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

    def _is_possible_technical_tag(self, text):
        tag = self._normalize_tag(text)
        if len(tag) < 2 or len(tag) > 12:
            return False
        if tag.isdigit():
            return False
        prefix_match = re.match(r"[A-Z]+", tag)
        if self.tag_prefixes and (not prefix_match or prefix_match.group(0) not in self.tag_prefixes):
            return False
        return bool(self.TECHNICAL_TAG_PATTERN.match(tag))

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

    def _build_detection(self, text, confidence, bbox):
        texto_ocr = self._clean_ocr_text(text)
        known_tag = self._extract_known_tag(texto_ocr)

        if known_tag:
            reference = self.tag_catalog[known_tag]
            return {
                "texto_ocr": texto_ocr,
                "tag": known_tag,
                "tipo": reference["tipo"],
                "classe": reference["classe"],
                "status": "Identificado",
                "confidence": round(float(confidence), 4),
                "bbox": bbox,
            }

        possible_tag = self._normalize_tag(texto_ocr)
        if self._is_possible_technical_tag(texto_ocr):
            return {
                "texto_ocr": texto_ocr,
                "tag": possible_tag,
                "tipo": "Não cadastrado",
                "classe": "Não cadastrado",
                "status": "Possível TAG",
                "confidence": round(float(confidence), 4),
                "bbox": bbox,
            }

        return None

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

        seen_detections = set()
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
                    for _, text, prob in results:
                        clean_text = self._clean_ocr_text(text)
                        if not clean_text or prob < 0.35:
                            continue

                        self.region_stats["ocr_texts"] += 1
                        self.ocr_results.append(
                            {
                                "texto_ocr": clean_text,
                                "confidence": round(float(prob), 4),
                                "bbox": bbox,
                            }
                        )

                        detection = self._build_detection(clean_text, prob, bbox)
                        if detection is None:
                            continue

                        detection_key = (detection["tag"], bbox["x"], bbox["y"])
                        if detection_key in seen_detections:
                            continue

                        seen_detections.add(detection_key)
                        self.detections.append(detection)
                        self.region_stats["valid_detections"] += 1
                        if detection["tag"] not in self.detected_tags:
                            self.detected_tags.append(detection["tag"])
                except Exception as exc:
                    message = f"OCR falhou na bbox {bbox}: {exc}"
                    self.ocr_errors.append(message)
                    if self.logger:
                        self.logger(f"    AVISO: {message}")

            has_valid_detection = any(item["bbox"] == bbox for item in self.detections)
            color = (0, 255, 0) if has_valid_detection else (0, 180, 255)
            cv2.rectangle(self.image_with_boxes, (x, y), (x + w, y + h), color, 2)
            cv2.putText(
                self.image_with_boxes,
                f"Obj {box_count}",
                (x, y - 10),
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




