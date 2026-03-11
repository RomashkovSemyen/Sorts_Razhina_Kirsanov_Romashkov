import subprocess
import sys
import os
import glob
import shutil
data_files = [
    'bubble.txt',
    'heap.txt',
    'insertion.txt',
    'merge.txt',
    'quick.txt',
    'selection.txt'
]
sort_exe = './a.out'               # исполняемый файл сортировок
sort_source = 'sorts.cpp'           # исходник
draw_script = 'draw.py'             # отрисовщик
frames_dir = 'frames'                # папка с кадрами
output_gif = 'sorting_visualization.gif'
framerate = 10                       # кадров в секунду
import os
import shutil
def clear_frames(frames_dir='frames'):
    if os.path.exists(frames_dir):
        # удаляем все файлы
        for filename in os.listdir(frames_dir):
            file_path = os.path.join(frames_dir, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)  # удаляем файл или ссылку
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)  # удаляем вложенную папку
            except Exception as e:
                print(f"не удалось удалить {file_path}: {e}")
    else:
        # если папки нет, создаём её
        os.makedirs(frames_dir, exist_ok=True)
        print(f"папка {frames_dir} создана")
def compile_sorts():
    if not os.path.exists(sort_source):
        print(f"{sort_source} не найден")
        sys.exit(1)

    need_compile = False
    if not os.path.exists(sort_exe):
        need_compile = True
    else:
        if os.path.getmtime(sort_source) > os.path.getmtime(sort_exe):
            need_compile = True

    if need_compile:
        print("компиляция sorts.cpp")
        try:
            subprocess.run(['g++', sort_source, '-o', 'a.out'], check=True)
            print("компиляция завершена")
        except subprocess.CalledProcessError:
            print("ошибка компиляции")
            sys.exit(1)
    else:
        print("исполняемый файл уже актуален")

def run_sorts():
    if not os.path.exists(sort_exe):
        print(f"{sort_exe} не найден. сначала выполните компиляцию.")
        sys.exit(1)

    print("запуск сортировок")
    try:
        subprocess.run([sort_exe], check=True)
        print("файлы данных сгенерированы")
    except subprocess.CalledProcessError:
        print("ошибка при выполнении сортировок")
        sys.exit(1)

def run_draw():
    missing = [f for f in data_files if not os.path.exists(f)]
    if missing:
        print(f"отсутствуют файлы данных: {missing}. запустите сортировки")
        sys.exit(1)
    clear_frames(frames_dir)
    print("запуск отрисовки")
    try:
        subprocess.run([sys.executable, draw_script] + data_files, check=True)
        print("кадры созданы в папке 'frames'")
    except subprocess.CalledProcessError:
        print("ошибка отрисовки")
        sys.exit(1)

def create_gif():
    try:
        from PIL import Image
    except ImportError:
        print("библиотека Pillow не установлена. установите её: pip install pillow")
        sys.exit(1)

    if not os.path.isdir(frames_dir):
        print(f"папка '{frames_dir}' не найдена")
        return

    # Ищем все кадры, отсортированные по номеру
    frame_pattern = os.path.join(frames_dir, 'frame_*.png')
    frame_files = sorted(glob.glob(frame_pattern))
    if not frame_files:
        print(f"в папке '{frames_dir}' нет кадров вида frame_*.png")
        return

    print(f"создаём GIF")

    # Длительность одного кадра в миллисекундах
    duration_ms = int(3000 / framerate)

    # Открываем все изображения
    images = [Image.open(f) for f in frame_files]

    # Сохраняем анимацию
    images[0].save(
        output_gif,
        save_all=True,
        append_images=images[1:],
        duration=duration_ms,
        loop=0,          # бесконечный цикл
        optimize=False   # можно включить, если нужна оптимизация размера
    )
    print(f"GIF сохранён как {output_gif}")
if __name__ == '__main__':
    # Обработка аргументов командной строки
    args = sys.argv[1:]
    if not args:
        compile_sorts()
        run_sorts()
        run_draw()
        create_gif()
    else:
        if 'compile' in args:
            compile_sorts()
        if 'run' in args:
            run_sorts()
        if 'draw' in args:
            run_draw()
        if 'gif' in args or 'video' in args:
            create_gif()
        if 'all' in args:
            compile_sorts()
            run_sorts()
            run_draw()
            create_gif()
