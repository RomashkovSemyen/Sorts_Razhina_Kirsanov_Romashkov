import os
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# Словарь цветов для элементов на основе их наиболее ярких спектральных линий
# (для первых 20 элементов, где есть надежные данные)
ELEMENT_COLORS = {
    1: '#FF4D4D',   # H - красный (656 нм) [citation:1][citation:9]
    2: '#FFD700',   # He - желтый (587 нм) [citation:9]
    3: '#FF69B4',   # Li - красный/розовый (671 нм) [citation:9]
    4: '#C0C0C0',   # Be - серебристый (нет ярких линий в видимом)
    5: '#32CD32',   # B - зеленый (но слабые линии)
    6: '#000000',   # C - черный (спектр в УФ)
    7: '#4169E1',   # N - синий/голубой (500 нм, 463 нм) [citation:9]
    8: '#1E90FF',   # O - голубой (441 нм) [citation:9]
    9: '#FFFF00',   # F - желтый (686 нм) [citation:9]
    10: '#FFA500',  # Ne - оранжевый (640 нм, 585 нм) [citation:9]
    11: '#FF8C00',  # Na - оранжевый/желтый (589 нм) [citation:1][citation:9]
    12: '#32CD32',  # Mg - зеленый (518 нм) [citation:9]
    13: '#C0C0C0',  # Al - серебристый (624 нм линия есть) [citation:9]
    14: '#808080',  # Si - серый (спектр в основном в УФ)
    15: '#FFA07A',  # P - светло-оранжевый
    16: '#FFFF00',  # S - желтый (469 нм) [citation:9]
    17: '#00FF00',  # Cl - зеленый (482 нм, 480 нм) [citation:9]
    18: '#9400D3',  # Ar - фиолетовый (696 нм, но чаще фиолетовый) [citation:9]
    19: '#800080',  # K - фиолетовый (580 нм, 404 нм) [citation:9]
    20: '#FF6347',  # Ca - красно-оранжевый (644 нм, 422 нм) [citation:9]
}

def get_element_color(atomic_number):
    """
    Возвращает цвет для элемента по его атомному номеру.
    Для известных элементов - спектральный цвет,
    для остальных - цвет на основе номера (для визуального разнообразия)
    """
    if atomic_number in ELEMENT_COLORS:
        return ELEMENT_COLORS[atomic_number]
    else:
        # Генерируем цвет на основе номера (чтобы все элементы были различимы)
        # Используем HSV: меняем оттенок, сохраняя насыщенность и яркость
        hue = (atomic_number * 37) % 360  # 37 - простое число для равномерного распределения
        return f'hsv({hue}, 70%, 90%)'  # Насыщенность 70%, яркость 90%

def format_element_label(atomic_number):
    """
    Форматирует подпись элемента в стиле таблицы Менделеева:
    верхний индекс - зарядовое число (массовое число, для простоты используем 2*номер),
    нижний индекс - атомный номер,
    основной символ - символ элемента.
    """
    # Символы элементов (первые 110)
    symbols = [
        'H', 'He', 'Li', 'Be', 'B', 'C', 'N', 'O', 'F', 'Ne',
        'Na', 'Mg', 'Al', 'Si', 'P', 'S', 'Cl', 'Ar', 'K', 'Ca',
        'Sc', 'Ti', 'V', 'Cr', 'Mn', 'Fe', 'Co', 'Ni', 'Cu', 'Zn',
        'Ga', 'Ge', 'As', 'Se', 'Br', 'Kr', 'Rb', 'Sr', 'Y', 'Zr',
        'Nb', 'Mo', 'Tc', 'Ru', 'Rh', 'Pd', 'Ag', 'Cd', 'In', 'Sn',
        'Sb', 'Te', 'I', 'Xe', 'Cs', 'Ba', 'La', 'Ce', 'Pr', 'Nd',
        'Pm', 'Sm', 'Eu', 'Gd', 'Tb', 'Dy', 'Ho', 'Er', 'Tm', 'Yb',
        'Lu', 'Hf', 'Ta', 'W', 'Re', 'Os', 'Ir', 'Pt', 'Au', 'Hg',
        'Tl', 'Pb', 'Bi', 'Po', 'At', 'Rn', 'Fr', 'Ra', 'Ac', 'Th',
        'Pa', 'U', 'Np', 'Pu', 'Am', 'Cm', 'Bk', 'Cf', 'Es', 'Fm',
        'Md', 'No', 'Lr', 'Rf', 'Db', 'Sg', 'Bh', 'Hs', 'Mt', 'Ds'
    ]
    
    if 1 <= atomic_number <= len(symbols):
        symbol = symbols[atomic_number - 1]
        # Зарядовое число (массовое) - для простоты используем округленную атомную массу
        # В реальности нужно брать из таблицы, здесь используем приближение: массовое число ≈ 2 * номер
        mass_number = atomic_number * 2
        # Для водорода корректируем
        if atomic_number == 1:
            mass_number = 1
        elif atomic_number == 2:
            mass_number = 4
            
        # Форматируем с использованием LaTeX-стиля (matplotlib поддерживает)
        return f'$^{{{mass_number}}}_{{{atomic_number}}}{symbol}$'
    else:
        return str(atomic_number)

def read_states(filename):
    """Читает файл, возвращает n и список состояний."""
    with open(filename, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]

    if not lines:
        raise ValueError("Файл пуст")

    try:
        n = int(lines[0])
    except ValueError:
        raise ValueError("Первая строка должна содержать размер массива")

    states = []
    for line in lines[1:]:
        parts = line.split()
        if len(parts) != n:
            print(f"Предупреждение: строка '{line}' содержит {len(parts)} элементов, ожидалось {n}. Пропускаем.")
            continue
        try:
            state = list(map(float, parts))
        except ValueError:
            print(f"Предупреждение: строка '{line}' содержит нечисловые данные. Пропускаем.")
            continue
        states.append(state)

    if not states:
        raise ValueError("Нет корректных состояний массива")

    return n, states

def plot_histogram(state, global_max, step, output_dir='frames'):
    """Строит цветную гистограмму с подписями элементов."""
    n = len(state)
    indices = range(1, n + 1)
    
    # Создаем фигуру с большим размером для читаемости
    plt.figure(figsize=(min(20, max(10, n * 0.3)), 8))
    
    # Строим столбцы с индивидуальными цветами
    bars = []
    for i, val in enumerate(state):
        atomic_number = int(val) if val.is_integer() and 1 <= val <= 110 else None
        color = get_element_color(atomic_number) if atomic_number else '#808080'  # серый для не-элементов
        bar = plt.bar(i + 1, val, width=0.8, color=color, edgecolor='black', alpha=0.8)
        bars.extend(bar)
    
    # Верхняя граница с запасом для подписей
    y_top = global_max + max(2, global_max * 0.15)  # увеличен запас для двухстрочных подписей
    plt.ylim(0, y_top)
    
    # Настройка осей
    plt.xlabel('Индекс элемента', fontsize=12)
    plt.ylabel('Значение (атомный номер)', fontsize=12)
    plt.title(f'Периодическая визуализация сортировки (шаг {step})', fontsize=14, fontweight='bold')
    plt.grid(axis='y', linestyle='--', alpha=0.3)
    
    # Подписи над столбцами
    for i, val in enumerate(state):
        atomic_number = int(val) if val.is_integer() and 1 <= val <= 110 else None
        if atomic_number:
            label = format_element_label(atomic_number)
            # Двухстрочная подпись: элемент сверху, число снизу
            label_y = val + y_top * 0.03
            plt.text(i + 1, label_y, label, 
                    ha='center', va='bottom',
                    fontsize=11, fontweight='bold',
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.7, edgecolor='gray'))
        else:
            # Для не-целых или выходящих за диапазон значений
            label_y = val + y_top * 0.02
            plt.text(i + 1, label_y, f'{val:.1f}',
                    ha='center', va='bottom',
                    fontsize=10, fontweight='normal',
                    bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.7, edgecolor='gray'))
    
    # Добавляем легенду для первых нескольких элементов (если нужно)
    if step == 1:  # только для первого кадра, чтобы не загромождать
        legend_elements = []
        for i, val in enumerate(state[:min(5, len(state))]):  # первые 5 элементов
            if val.is_integer() and 1 <= int(val) <= 110:
                atomic_number = int(val)
                color = get_element_color(atomic_number)
                symbols = ['H', 'He', 'Li', 'Be', 'B', 'C', 'N', 'O', 'F', 'Ne']
                if atomic_number <= len(symbols):
                    legend_elements.append(mpatches.Patch(color=color, label=f'{atomic_number}: {symbols[atomic_number-1]}'))
        
        if legend_elements:
            plt.legend(handles=legend_elements, loc='upper right', fontsize=9, 
                      title="Элементы", title_fontsize=10)
    
    # Сохраняем
    os.makedirs(output_dir, exist_ok=True)
    filename = os.path.join(output_dir, f'frame_{step:04d}.png')
    plt.savefig(filename, dpi=120, bbox_inches='tight')
    plt.close()
    print(f"Сохранено: {filename}")

def main(input_file, output_dir='frames'):
    n, states = read_states(input_file)
    print(f"Размер массива: {n}")
    print(f"Количество состояний: {len(states)}")
    
    # Проверяем, что значения - целые числа в диапазоне 1-110
    all_values = [val for state in states for val in state]
    for val in all_values:
        if not (val.is_integer() and 1 <= val <= 110):
            print(f"Предупреждение: значение {val} не является целым числом от 1 до 110")
    
    global_max = max(all_values)
    print(f"Глобальный максимум: {global_max}")
    
    for i, state in enumerate(states, start=1):
        plot_histogram(state, global_max, i, output_dir)
    
    print(f"Готово! {len(states)} изображений сохранено в папке '{output_dir}'")

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print("Использование: python script.py <имя_файла> [выходная_папка]")
        print("Пример: python script.py sorting_states.txt frames")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else 'frames'
    main(input_file, output_dir)