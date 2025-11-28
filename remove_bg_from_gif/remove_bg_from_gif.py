import cv2
import numpy as np
import os
from PIL import Image, ImageSequence
import argparse

def remove_white_background_gif(gif_path, output_webp_path, threshold=240):
    """
    Удаляет белый фон из GIF и сохраняет как анимированный WebP с прозрачностью
    """
    try:
        # Проверяем существование файла
        if not os.path.exists(gif_path):
            print(f"❌ Файл {gif_path} не найден!")
            return False
        
        print(f"🔄 Обрабатываю: {gif_path}")
        
        # Открываем GIF с помощью PIL
        gif = Image.open(gif_path)
        frames = []
        
        print(f"📊 Количество кадров: {gif.n_frames}")
        
        for i, frame in enumerate(ImageSequence.Iterator(gif)):
            print(f"🎞️  Обрабатываю кадр {i+1}/{gif.n_frames}")
            
            # Конвертируем в RGBA если нужно
            if frame.mode != 'RGBA':
                frame = frame.convert('RGBA')
            
            # Конвертируем PIL Image в numpy array для OpenCV
            frame_cv = cv2.cvtColor(np.array(frame), cv2.COLOR_RGBA2BGRA)
            
            # Создаем маску для белого цвета
            white_mask = np.all(frame_cv[:, :, :3] > [threshold, threshold, threshold], axis=2)
            
            # Создаем альфа-канал: 0 где белый фон, 255 где не белый
            alpha_channel = np.where(white_mask, 0, 255).astype(np.uint8)
            
            # Применяем альфа-канал
            frame_cv[:, :, 3] = alpha_channel
            
            # Конвертируем обратно в PIL Image
            result_frame = Image.fromarray(cv2.cvtColor(frame_cv, cv2.COLOR_BGRA2RGBA))
            frames.append(result_frame)
        
        # Сохраняем как анимированный WebP
        if frames:
            print("💾 Сохраняю как WebP...")
            frames[0].save(
                output_webp_path,
                format='WEBP',
                save_all=True,
                append_images=frames[1:],
                duration=30, #gif.info.get('duration', 100),
                loop=0,
                quality=80
            )
            print(f"✅ Успешно сохранено: {output_webp_path}")
            return True
        else:
            print("❌ Не удалось обработать кадры")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Конвертер GIF в WebP с удалением белого фона')
    parser.add_argument('input', help='Путь к входному GIF файлу')
    parser.add_argument('-o', '--output', help='Путь для выходного WebP файла')
    parser.add_argument('-t', '--threshold', type=int, default=240, 
                       help='Порог для белого цвета (0-255, по умолчанию 240)')
    
    args = parser.parse_args()
    
    # Если выходной файл не указан, создаем автоматически
    if not args.output:
        base_name = os.path.splitext(args.input)[0]
        args.output = f"{base_name}.webp"
    
    print("🚀 Запуск конвертации...")
    print(f"📁 Входной файл: {args.input}")
    print(f"💾 Выходной файл: {args.output}")
    print(f"🎚️  Порог: {args.threshold}")
    print("-" * 40)
    
    success = remove_white_background_gif(args.input, args.output, args.threshold)
    
    if success:
        print("🎉 Конвертация завершена успешно!")
    else:
        print("💥 Конвертация не удалась")

if __name__ == "__main__":
    main()