import cv2
import numpy as np
import easyocr


class PIDImageProcessor:
    
    def __init__(self, image_path):
        # Carrega a imagem com OpenCV
        self.original_image = cv2.imread(image_path)
        if self.original_image is None:
            raise ValueError(f"Não foi possível carregar a imagem: {image_path}")
        
        self.gray_image = None
        self.blurred_image = None
        self.threshold_image = None
        self.contours = None
        self.image_with_boxes = None
        self.detected_tags = []
        
        # Força o uso exclusivo da CPU (evita travamentos de GPU/CUDA)
        self.reader = easyocr.Reader(['en'], gpu=False, verbose=False)
    
    def convert_to_grayscale(self):
        self.gray_image = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2GRAY)
        return self.gray_image
    
    def apply_blur(self, kernel_size=(5, 5)):
        if self.gray_image is None:
            self.convert_to_grayscale()
        
        self.blurred_image = cv2.GaussianBlur(self.gray_image, kernel_size, 0)
        return self.blurred_image
    
    def apply_threshold(self, threshold_value=127, method='binary'):
        if self.blurred_image is None:
            self.apply_blur()
        
        if method == 'otsu':
            _, self.threshold_image = cv2.threshold(
                self.blurred_image, 0, 255, 
                cv2.THRESH_BINARY + cv2.THRESH_OTSU
            )
        else:
            _, self.threshold_image = cv2.threshold(
                self.blurred_image, threshold_value, 255, 
                cv2.THRESH_BINARY
            )
        
        return self.threshold_image
    
    def detect_contours(self):
        if self.threshold_image is None:
            self.apply_threshold()
        
        contours, _ = cv2.findContours(
            self.threshold_image, 
            cv2.RETR_TREE, 
            cv2.CHAIN_APPROX_SIMPLE
        )
        
        self.contours = contours
        return contours
    
    def draw_bounding_boxes(self, min_area=500):
        if self.contours is None:
            self.detect_contours()
        
        self.image_with_boxes = self.original_image.copy()
        self.detected_tags = []
        
        box_count = 0
        for contour in self.contours:
            area = cv2.contourArea(contour)
            
            if area < min_area:
                continue

            x, y, w, h = cv2.boundingRect(contour)
            
            # Recorta a Região de Interesse (ROI)
            roi = self.original_image[y:y+h, x:x+w]
            
            # Leitura com o OCR
            if roi.size > 0:
                try:
                    results = self.reader.readtext(roi)
                    for (_, text, prob) in results:
                        if prob > 0.3:
                            clean_text = text.strip().upper()
                            if clean_text and clean_text not in self.detected_tags:
                                self.detected_tags.append(clean_text)
                except Exception:
                    pass

            cv2.rectangle(self.image_with_boxes, (x, y), (x + w, y + h), 
                         (0, 255, 0), 2)
            
            cv2.putText(self.image_with_boxes, f"Obj {box_count}", 
                       (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 
                       0.5, (0, 255, 0), 2)
            
            box_count += 1
        
        return self.image_with_boxes
    
    def process_pipeline(self, threshold_method='otsu', min_area=500):
        self.convert_to_grayscale()
        self.apply_blur()
        self.apply_threshold(method=threshold_method)
        self.detect_contours()
        self.draw_bounding_boxes(min_area=min_area)
        return self.original_image, self.image_with_boxes
    
    def get_processed_images(self):
        return {
            'original': self.original_image,
            'grayscale': self.gray_image,
            'blurred': self.blurred_image,
            'threshold': self.threshold_image,
            'with_boxes': self.image_with_boxes
        }