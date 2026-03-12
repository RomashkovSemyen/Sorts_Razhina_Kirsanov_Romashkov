import sys
import os
import glob
from PIL import Image
def main():
    if len(sys.argv) < 4:
        print("использование: make_gif.py <папка_с_кадрами> <выходной_файл.gif> <fps>")
        sys.exit(1)

    frames_dir = sys.argv[1]
    output_gif = sys.argv[2]
    fps = float(sys.argv[3])

    # Ищем все кадры с именем frame_0001.png, frame_0002.png, ...
    pattern = os.path.join(frames_dir, "frame_*.png")
    frame_files = sorted(glob.glob(pattern))

    if not frame_files:
        print(f"в папке {frames_dir} нет кадров вида frame_*.png")
        sys.exit(1)

    #print(f"Найдено {len(frame_files)} кадров. Создаём GIF...")
    images = [Image.open(f) for f in frame_files]
    duration = int(1000 / fps)  # миллисекунд на кадр

    # Сохраняем анимацию
    images[0].save(
        output_gif,
        save_all=True,
        append_images=images[1:],
        duration=duration,
        loop=0,          # бесконечный цикл
        optimize=False
    )
    print(f"GIF сохранён как {output_gif}")

if __name__ == "__main__":
    main()
