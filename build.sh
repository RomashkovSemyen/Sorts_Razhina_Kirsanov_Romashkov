#!/bin/bash
DATA_FILES=("bubble.txt" "heap.txt" "insertion.txt" "merge.txt" "quick.txt" "selection.txt")
SORT_EXE="./a.out"
SORT_SRC="sorts.cpp"
DRAW_SCRIPT="draw.py"
GIF_SCRIPT="make_gif.py"
FRAMES_DIR="frames"
OUTPUT_GIF="sorting_visualization.gif"
FPS=10
compile_sorts() {
	if [ ! -f "$SORT_SRC" ]; then
		echo "Ошибка: $SORT_SRC не найден"
		exit 1
	fi
	need_compile=0
	if [ ! -f "$SORT_EXE" ]; then
		need_compile=1
	else
		if [ "$SORT_SRC" -nt "$SORT_EXE" ]; then
			need_compile=1
		fi
	fi
	if [ $need_compile -eq 1 ]; then
		echo "Компиляция $SORT_SRC ..."
		g++ "$SORT_SRC" -o "$SORT_EXE"
		if [ $? -ne 0 ]; then
			echo "Ошибка компиляции"
			exit 1
		fi
		echo "Компиляция завершена"
	else
		echo "Исполняемый файл $SORT_EXE уже актуален"
	fi
}
run_sorts() {
	if [ ! -f "$SORT_EXE" ]; then
		echo "Ошибка: $SORT_EXE не найден. Сначала выполните компиляцию."
		exit 1
	fi
	echo "Запуск сортировок..."
	"$SORT_EXE"
	if [ $? -ne 0 ]; then
		echo "Ошибка при выполнении сортировок"
		exit 1
	fi
	echo "Файлы данных сгенерированы"
}
run_draw() {
	for f in "${DATA_FILES[@]}"; do
		if [ ! -f "$f" ]; then
			echo "Ошибка: файл данных $f не найден. Запустите сортировки."
			exit 1
		fi
	done
	if [ -d "$FRAMES_DIR" ]; then
		echo "Очистка папки $FRAMES_DIR ..."
		rm -rf "$FRAMES_DIR"/*
	else
		mkdir -p "$FRAMES_DIR"
	fi
	echo "Запуск отрисовки..."
	python3 "$DRAW_SCRIPT" "${DATA_FILES[@]}"
	if [ $? -ne 0 ]; then
		echo "Ошибка отрисовки"
		exit 1
	fi
	echo "Кадры сохранены в $FRAMES_DIR"
}
make_gif() {
	if [ ! -d "$FRAMES_DIR" ]; then
		echo "Ошибка: папка $FRAMES_DIR не найдена"
		exit 1
	fi
	if [ -z "$(ls -A "$FRAMES_DIR")" ]; then
		echo "Ошибка: папка $FRAMES_DIR пуста"
		exit 1
	fi
	echo "Создание GIF..."
	python3 "$GIF_SCRIPT" "$FRAMES_DIR" "$OUTPUT_GIF" "$FPS"
	if [ $? -ne 0 ]; then
		echo "Ошибка при создании GIF"
		exit 1
	fi
	echo "GIF создан: $OUTPUT_GIF"
}
clean() {
	echo "Очистка временных файлов..."
	for f in "${DATA_FILES[@]}"; do
		if [ -f "$f" ]; then
			rm "$f"
			echo "Удалён $f"
		fi
	done
	if [ -d "$FRAMES_DIR" ]; then
		rm -rf "$FRAMES_DIR"
		echo "Удалена папка $FRAMES_DIR"
	fi
	echo "Очистка завершена"
}
if [ "$1" == "--help" ] || [ "$1" == "-h" ]; then
	echo "Использование: $0 [--compile] [--run] [--draw] [--gif] [--clean]"
	echo "  --compile    только компиляция sorts.cpp"
	echo "  --run        только запуск сортировок (генерация данных)"
	echo "  --draw       только отрисовка кадров"
	echo "  --gif        только создание GIF из имеющихся кадров"
	echo "  --clean      удалить все файлы данных и папку с кадрами"
	echo "  без аргументов: полный цикл (компиляция + сортировки + отрисовка + GIF)"
	exit 0
fi
if [ "$1" == "--clean" ]; then
	clean
	exit 0
fi
if [ $# -eq 0 ]; then
	echo "Запуск полного цикла..."
	compile_sorts
	run_sorts
	run_draw
	make_gif
	echo "Готово!"
	exit 0
fi
while [ $# -gt 0 ]; do
	case "$1" in
		--compile)
			compile_sorts
			;;
		--run)
			run_sorts
			;;
		--draw)
			run_draw
			;;
		--gif)
			make_gif
			;;
		*)
			echo "Неизвестный аргумент: $1"
			exit 1
			;;
	esac
	shift
done
EOF

