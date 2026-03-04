import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def read_single_file(filename):
    """Читает один файл, возвращает (n, states)."""
    with open(filename, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]
    if not lines:
        raise ValueError(f"Файл {filename} пуст")
    try:
        n = int(lines[0])
    except ValueError:
        raise ValueError(f"Первая строка файла {filename} должна содержать размер массива")
    states = []
    for line in lines[1:]:
        parts = line.split()
        if len(parts) != n:
            print(f"Предупреждение: файл {filename}, строка '{line}' содержит {len(parts)} элементов, ожидалось {n}. Пропускаем.")
            continue
        try:
            state = list(map(float, parts))
        except ValueError:
            print(f"Предупреждение: файл {filename}, строка '{line}' содержит нечисловые данные. Пропускаем.")
            continue
        states.append(state)
    if not states:
        raise ValueError(f"Файл {filename} не содержит корректных состояний")
    return n, states

def read_all_files(file_list):
    """Читает все файлы, проверяет одинаковость размера, возвращает states_list и n."""
    all_states = []
    n_vals = []
    for fname in file_list:
        n, states = read_single_file(fname)
        n_vals.append(n)
        all_states.append(states)
    if len(set(n_vals)) != 1:
        raise ValueError("Размеры массивов в файлах различаются!")
    return all_states, n_vals[0]

def draw_horizontal_bars(ax, values, global_max, reverse=False, name="", align_title='left'):
    """
    Рисует горизонтальную гистограмму зелёного цвета с чёрными границами.
    Убирает все подписи, тики, сетку и рамки.
    Добавляет название сортировки в указанном углу: 'left' или 'right'.
    """
    n = len(values)
    indices = list(range(1, n + 1))
    
    # Столбцы вплотную друг к другу (height=1.0) с чёрными границами
    bars = ax.barh(indices, values, height=1.0, color='green', 
                   edgecolor='black', linewidth=0.5)
    ax.invert_yaxis()  # первый индекс сверху
    
    if reverse:
        ax.set_xlim(global_max, 0)
    else:
        ax.set_xlim(0, global_max)
    
    # Убираем всё оформление
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_xlabel('')
    ax.set_ylabel('')
    ax.grid(False)
    for spine in ax.spines.values():
        spine.set_visible(False)
    
    # Название сортировки в заданном углу
    if align_title == 'left':
        ax.text(0.02, 0.98, name, transform=ax.transAxes,
                ha='left', va='top', fontsize=10, fontweight='bold', color='black')
    else:  # right
        ax.text(0.98, 0.98, name, transform=ax.transAxes,
                ha='right', va='top', fontsize=10, fontweight='bold', color='black')

def create_frame(states_list, step, global_max, output_dir, filenames, max_steps):
    """
    Создаёт один кадр с 6 зелёными горизонтальными гистограммами в сетке 3x2.
    Расстояние между колонками и строками убрано (wspace=0, hspace=0).
    Надпись с номером шага — в левом нижнем углу всей картинки.
    Под нижней строкой добавлен коричневый прямоугольник (ствол ёлки),
    ширина которого уменьшена вдвое (0.075).
    """
    fig, axes = plt.subplots(3, 2, figsize=(12, 10),
                             gridspec_kw={'wspace': 0, 'hspace': 0})
    
    # Настраиваем отступы: верх увеличен, низ оставлен для ствола и текста
    plt.subplots_adjust(left=0.05, right=0.95, top=0.92, bottom=0.08)
    
    for idx, (states, ax, fname) in enumerate(zip(states_list, axes.flat, filenames)):
        # Текущее состояние (заморозка последнего)
        if step <= len(states):
            current_state = states[step - 1]
        else:
            current_state = states[-1]
        
        # Левый столбец (чётные индексы) – влево, правый (нечётные) – вправо
        reverse = (idx % 2 == 0)
        
        # Имя файла без расширения
        short_name = os.path.splitext(os.path.basename(fname))[0]
        
        # Определяем положение названия: для idx=1,3,5 (файлы 2,4,6) — правый верхний угол
        align = 'right' if idx in (1, 3, 5) else 'left'
        
        draw_horizontal_bars(ax, current_state, global_max, reverse, short_name, align)
    
    # Добавляем коричневый прямоугольник (ствол) под нижней строкой
    trunk_width = 0.05      # ширина ствола (уменьшена вдвое)
    trunk_height = 0.06     # высота ствола
    trunk_x = 0.5 - trunk_width/2  # центрирование
    trunk_y = 0.02             # нижняя граница ствола (немного выше нижнего края)
    
    trunk = patches.Rectangle((trunk_x, trunk_y), trunk_width, trunk_height,
                              linewidth=0, facecolor='brown')
    fig.add_artist(trunk)
    
    # Текст с номером шага в левом нижнем углу фигуры, ниже ствола
    fig.text(0.05, 0.01, f'Шаг {step} из {max_steps}',
             ha='left', va='bottom', fontsize=12, fontweight='bold')
    
    os.makedirs(output_dir, exist_ok=True)
    filename = os.path.join(output_dir, f'frame_{step:04d}.png')
    plt.savefig(filename, dpi=120, bbox_inches='tight')
    plt.close()
    print(f"Сохранено: {filename}")

def main(file_list, output_dir='frames'):
    all_states, n = read_all_files(file_list)
    print(f"Размер массивов: {n}")
    for i, states in enumerate(all_states):
        print(f"Файл {i+1}: {len(states)} состояний")
    
    max_steps = max(len(states) for states in all_states)
    print(f"Максимальное количество шагов: {max_steps}")
    
    all_values = [val for states in all_states for state in states for val in state]
    global_max = max(all_values)
    print(f"Глобальный максимум: {global_max}")
    
    for step in range(1, max_steps + 1):
        create_frame(all_states, step, global_max, output_dir, file_list, max_steps)
    
    print(f"Готово! {max_steps} изображений сохранено в папке '{output_dir}'")

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 7:
        print("Использование: python script.py <файл1> <файл2> <файл3> <файл4> <файл5> <файл6> [выходная_папка]")
        sys.exit(1)
    input_files = sys.argv[1:7]
    output_dir = sys.argv[7] if len(sys.argv) > 7 else 'frames'
    main(input_files, output_dir)