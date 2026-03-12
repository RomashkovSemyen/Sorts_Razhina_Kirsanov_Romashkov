import os
import sys
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

def read_single_file(filename):
    """Читает файл данных: первая строка N, далее строки по N чисел."""
    with open(filename, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f if line.strip()]
    if not lines:
        raise ValueError(f"Файл {filename} пуст")
    try:
        n = int(lines[0])
    except ValueError:
        raise ValueError(f"Первая строка файла {filename} должна быть числом N")
    
    states = []
    for line in lines[1:]:
        parts = line.split()
        if len(parts) == n:
            try:
                states.append(list(map(float, parts)))
            except ValueError:
                continue
    return n, states

def read_all_files(file_list):
    all_states = []
    n_vals = []
    for fname in file_list:
        n, states = read_single_file(fname)
        n_vals.append(n)
        all_states.append(states)
    if len(set(n_vals)) != 1:
        raise ValueError("Размеры массивов в файлах должны быть одинаковыми!")
    return all_states, n_vals[0]

def draw_branch(ax, values, global_max, scale, color, reverse=False, name=""):
    """Рисует одну сторону веток (левую или правую)."""
    n = len(values)
    indices = list(range(1, n + 1))
    
    # Рисуем столбцы (zorder=3 — поверх ствола)
    ax.barh(indices, values, height=1.0, color=color, 
            edgecolor='#002200', linewidth=0.4, zorder=3)
    
    ax.invert_yaxis()
    
    # Ограничение оси X создает эффект сужения
    ax.set_xlim(0, global_max / scale)
    if reverse:
        ax.set_xlim(ax.get_xlim()[1], 0)
    
    ax.axis('off')
    ax.set_facecolor('none')

    # 🎬 ПОДПИСЬ АЛГОРИТМА — УВЕЛИЧЕННЫЙ ШРИФТ
    ax.text(0.95 if not reverse else 0.05, 0.95, name, transform=ax.transAxes,
            ha='right' if not reverse else 'left', va='top', 
            fontsize=16, fontweight='bold', color='white', alpha=0.9)  # Было: 9, alpha=0.4
def create_frame(states_list, step, global_max, output_dir, filenames, max_steps):
    # Фон всей картинки — темно-серый/черный
    fig = plt.figure(figsize=(10, 12), facecolor='#111111')
    
    # 🎬 GridSpec с явным отступом сверху (15% фигуры свободно)
    gs = fig.add_gridspec(3, 2, hspace=0, wspace=0,
                          top=0.85, bottom=0.05, left=0.05, right=0.95)
    
    axes = np.empty((3, 2), dtype=object)
    for i in range(3):
        for j in range(2):
            axes[i, j] = fig.add_subplot(gs[i, j])

    # Параметры ярусов
    tier_colors = ['#4CAF50', '#388E3C', '#1B5E20']
    tier_scales = [0.7, 0.8, 0.9]

    # --- СТВОЛ ---
    trunk_width = 0.035
    # Ствол заканчивается на y=0.85 (граница зоны монтажа)
    trunk = patches.Rectangle((0.5 - trunk_width/2, 0.05), trunk_width, 0.80,
                             transform=fig.transFigure, color='#3D2314', 
                             zorder=0)
    fig.add_artist(trunk)

    for idx, (states, ax, fname) in enumerate(zip(states_list, axes.flat, filenames)):
        ax.patch.set_alpha(0)
        ax.set_zorder(2)
        
        row = idx // 2
        is_left = (idx % 2 == 0)
        
        current_state = states[step - 1] if step <= len(states) else states[-1]
        name = os.path.splitext(os.path.basename(fname))[0]
        
        draw_branch(ax, current_state, global_max, 
                    tier_scales[row], tier_colors[row], 
                    reverse=is_left, name=name)
    
    # Текст внизу
    fig.text(0.5, 0.02, f"Шаг {step} / {max_steps}", ha='center', 
             color='white', fontsize=10, alpha=0.5, zorder=4)

    os.makedirs(output_dir, exist_ok=True)
    save_path = os.path.join(output_dir, f'frame_{step:04d}.png')
    
    # 🎬 ВАЖНО: убираем bbox_inches='tight', иначе отступы исчезнут!
    plt.savefig(save_path, dpi=100, facecolor=fig.get_facecolor())
    plt.close()    
def main():
    if len(sys.argv) < 7:
        print("Нужно 6 файлов. Пример: python script.py 1.txt 2.txt 3.txt 4.txt 5.txt 6.txt")
        return

    files = sys.argv[1:7]
    all_states, n = read_all_files(files)
    
    max_steps = max(len(s) for s in all_states)
    # Находим самый большой элемент во всех данных для масштаба
    global_max = max(max(state) for states in all_states for state in states)
    
    print(f"Генерация {max_steps} кадров...")
    for step in range(1, max_steps + 1):
        create_frame(all_states, step, global_max, 'frames', files, max_steps)
        if step % 20 == 0: print(f"Выполнено: {step}/{max_steps}")
    
    print("Готово! Проверьте папку 'frames'.")

if __name__ == "__main__":
    main()