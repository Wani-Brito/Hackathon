import cv2
import numpy as np


class PIDImageProcessor:
    
    def __init__(self, image_path):
        self.original_image = cv2.imread(image_path)
        if self.original_image is None:
            raise ValueError(f"Não foi possível carregar a imagem: {image_path}")
        
        self.gray_image = None
        self.blurred_image = None
        self.threshold_image = None
        self.contours = None
        self.image_with_boxes = None
    
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
        
        box_count = 0
        for contour in self.contours:
            area = cv2.contourArea(contour)
            
            if area < min_area:
                continue

            x, y, w, h = cv2.boundingRect(contour)
        
            cv2.rectangle(self.image_with_boxes, (x, y), (x + w, y + h), 
                         (0, 255, 0), 2)
            
            cv2.putText(self.image_with_boxes, f"Obj {box_count}", 
                       (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 
                       0.5, (0, 255, 0), 2)
            
            box_count += 1
        
        print(f"Total de objetos detectados: {box_count}")
        return self.image_with_boxes
    
    def process_pipeline(self, threshold_method='otsu', min_area=500):
        print("Iniciando pipeline de processamento...")
        print("1. Convertendo para escala de cinza...")
        self.convert_to_grayscale()
        
        print("2. Aplicando desfoque...")
        self.apply_blur()
        
        print("3. Aplicando limiarização...")
        self.apply_threshold(method=threshold_method)
        
        print("4. Detectando contornos...")
        self.detect_contours()
        
        print("5. Desenhando bounding boxes...")
        self.draw_bounding_boxes(min_area=min_area)
        
        print("Pipeline concluído!")
        return self.original_image, self.image_with_boxes
    
    def get_processed_images(self):
        return {
            'original': self.original_image,
            'grayscale': self.gray_image,
            'blurred': self.blurred_image,
            'threshold': self.threshold_image,
            'with_boxes': self.image_with_boxes
        }
