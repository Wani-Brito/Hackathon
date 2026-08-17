"""
Script para gerar uma imagem de teste que simula um P&ID básico.
Útil para testar o pipeline sem ter uma imagem real.
"""

import cv2
import numpy as np
import os


def create_test_pid_image(output_path='dataset/exemplo.png'):
    """
    Cria uma imagem de teste que simula um P&ID básico com componentes.
    
    Args:
        output_path (str): Caminho onde salvar a imagem
    """
    # Cria uma imagem branca (altura, largura, canais)
    height, width = 600, 800
    image = np.ones((height, width, 3), dtype=np.uint8) * 255
    
    # Cores em BGR (OpenCV usa BGR, não RGB)
    black = (0, 0, 0)
    gray = (128, 128, 128)
    
    # Desenha retângulos para simular componentes (válvulas, medidores, etc.)
    
    # Componente 1: Tanque/Reservatório (retângulo grande)
    cv2.rectangle(image, (50, 50), (200, 200), black, 2)
    cv2.putText(image, 'T210', (80, 130), cv2.FONT_HERSHEY_SIMPLEX, 1, black, 2)
    
    # Componente 2: Válvula 1 (círculo)
    cv2.circle(image, (400, 100), 30, black, 2)
    cv2.putText(image, 'V210', (370, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.7, black, 2)
    
    # Componente 3: Medidor de Fluxo (retângulo pequeno)
    cv2.rectangle(image, (300, 250), (450, 320), black, 2)
    cv2.putText(image, 'FV210', (340, 290), cv2.FONT_HERSHEY_SIMPLEX, 0.8, black, 2)
    
    # Componente 4: Motor (retângulo)
    cv2.rectangle(image, (500, 150), (620, 280), black, 2)
    cv2.putText(image, 'M210', (530, 220), cv2.FONT_HERSHEY_SIMPLEX, 0.8, black, 2)
    
    # Componente 5: Transmissor de Temperatura (retângulo pequeno)
    cv2.rectangle(image, (600, 400), (700, 480), black, 2)
    cv2.putText(image, 'LT210', (615, 445), cv2.FONT_HERSHEY_SIMPLEX, 0.7, black, 2)
    
    # Componente 6: Controlador (retângulo)
    cv2.rectangle(image, (100, 350), (250, 450), black, 2)
    cv2.putText(image, 'LC201', (120, 405), cv2.FONT_HERSHEY_SIMPLEX, 0.8, black, 2)
    
    # Linhas de conexão (simula tubulações)
    # Linha do tanque para válvula
    cv2.line(image, (200, 100), (370, 100), black, 2)
    
    # Linha da válvula para medidor de fluxo
    cv2.line(image, (400, 130), (400, 250), black, 2)
    
    # Linha do medidor para motor
    cv2.line(image, (450, 280), (500, 230), black, 2)
    
    # Linha do motor para transmissor
    cv2.line(image, (620, 200), (650, 400), black, 2)
    
    # Linha do transmissor para controlador
    cv2.line(image, (600, 440), (250, 410), black, 2)
    
    # Alguns pequenos círculos para simular conexões
    cv2.circle(image, (200, 100), 5, black, -1)
    cv2.circle(image, (400, 130), 5, black, -1)
    cv2.circle(image, (450, 280), 5, black, -1)
    cv2.circle(image, (620, 200), 5, black, -1)
    cv2.circle(image, (650, 400), 5, black, -1)
    
    # Cria pasta dataset se não existir
    os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
    
    # Salva a imagem
    cv2.imwrite(output_path, image)
    print(f"Imagem de teste criada com sucesso: {output_path}")
    print(f"Dimensões: {width}x{height} pixels")
    print("\nComponentes simulados:")
    print("  - T210: Tanque")
    print("  - V210: Válvula")
    print("  - FV210: Medidor de Fluxo")
    print("  - M210: Motor")
    print("  - LT210: Transmissor de Temperatura")
    print("  - LC201: Controlador de Nível")


if __name__ == "__main__":
    create_test_pid_image()
