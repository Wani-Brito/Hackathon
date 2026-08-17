import cv2
import os
import sys
from image_processing import PIDImageProcessor


def display_images(original, processed):
    
    max_height = 600
    
    if original.shape[0] > max_height:
        scale = max_height / original.shape[0]
        original = cv2.resize(original, None, fx=scale, fy=scale)
        processed = cv2.resize(processed, None, fx=scale, fy=scale)
    
    combined = cv2.hconcat([original, processed])
    
    cv2.imshow("Original vs Processada", combined)
    print("\nPressione qualquer tecla para fechar a janela...")
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def main():
    dataset_path = os.path.join(os.path.dirname(__file__), 'dataset')

    # Pega todas as imagens da pasta
    imagens = [
        arquivo for arquivo in os.listdir(dataset_path)
        if arquivo.lower().endswith(('.png', '.jpg', '.jpeg'))
    ]

    if not imagens:
        print("Nenhuma imagem encontrada na pasta dataset.")
        sys.exit(1)

    print(f"{len(imagens)} imagens encontradas.\n")

    for nome_imagem in imagens:

        caminho = os.path.join(dataset_path, nome_imagem)

        print(f"Processando: {nome_imagem}")

        try:
            processor = PIDImageProcessor(caminho)

            original, processed = processor.process_pipeline(
                threshold_method='otsu',
                min_area=500
            )

            display_images(original, processed)

            # Salva o resultado com outro nome
            nome_resultado = "resultado_" + nome_imagem
            output_path = os.path.join(dataset_path, nome_resultado)

            cv2.imwrite(output_path, processed)

            print(f"Resultado salvo em: {output_path}")
            print("-" * 50)

        except Exception as e:
            print(f"Erro ao processar {nome_imagem}: {e}")


if __name__ == "__main__":
    main()
