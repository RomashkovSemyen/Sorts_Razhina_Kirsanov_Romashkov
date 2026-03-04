#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <random>
#include <chrono>
#include <algorithm>


// запись шага
void recordStep(const std::vector<int>& arr, std::vector<std::vector<int>>& steps) {
    steps.push_back(arr);
}
// Сортировка пузырьком
void bubbleSort(std::vector<int>& arr, std::vector<std::vector<int>>& steps) {
    int n = arr.size();
    for (int i = 0; i < n; ++i) {
        for (int j = 0; j < n - i - 1; ++j) {
            if (arr[j] > arr[j + 1]) {
                std::swap(arr[j], arr[j + 1]);
                recordStep(arr, steps);
            }
        }
    }
}

// Сортировка выбором
void selectionSort(std::vector<int>& arr, std::vector<std::vector<int>>& steps) {
    int n = arr.size();
    for (int i = 0; i < n; ++i) {
        int minIdx = i;
        for (int j = i + 1; j < n; ++j) {
            if (arr[j] < arr[minIdx]) {
                minIdx = j;
            }
        }
        if (minIdx != i) {
            std::swap(arr[i], arr[minIdx]);
            recordStep(arr, steps);
        }
    }
}

// Сортировка вставками
void insertionSort(std::vector<int>& arr, std::vector<std::vector<int>>& steps) {
    int n = arr.size();
    for (int i = 1; i < n; ++i) {
        int key = arr[i];
        int j = i - 1;
        while (j >= 0 && arr[j] > key) {
            arr[j + 1] = arr[j];
            recordStep(arr, steps);
            --j;
        }
        arr[j + 1] = key;
        recordStep(arr, steps);
    }
}

// Быстрая сортировка 
int partition(std::vector<int>& arr, int low, int high, std::vector<std::vector<int>>& steps) {
    int pivot = arr[high];
    int i = low - 1;
    for (int j = low; j < high; ++j) {
        if (arr[j] <= pivot) {
            ++i;
            std::swap(arr[i], arr[j]);
            recordStep(arr, steps);
        }
    }
    std::swap(arr[i + 1], arr[high]);
    recordStep(arr, steps);
    return i + 1;
}

void quickSort(std::vector<int>& arr, int low, int high, std::vector<std::vector<int>>& steps) {
    if (low < high) {
        int pi = partition(arr, low, high, steps);
        quickSort(arr, low, pi - 1, steps);
        quickSort(arr, pi + 1, high, steps);
    }
}

// Сортировка слиянием
void merge(std::vector<int>& arr, int left, int mid, int right, std::vector<std::vector<int>>& steps) {
    std::vector<int> L(arr.begin() + left, arr.begin() + mid + 1);
    std::vector<int> R(arr.begin() + mid + 1, arr.begin() + right + 1);
    int i = 0, j = 0, k = left;
    while (i < L.size() && j < R.size()) {
        if (L[i] <= R[j]) {
            arr[k] = L[i];
            ++i;
        } else {
            arr[k] = R[j];
            ++j;
        }
        recordStep(arr, steps);
        ++k;
    }
    while (i < L.size()) {
        arr[k] = L[i];
        recordStep(arr, steps);
        ++i;
        ++k;
    }
    while (j < R.size()) {
        arr[k] = R[j];
        recordStep(arr, steps);
        ++j;
        ++k;
    }
}

void mergeSort(std::vector<int>& arr, int left, int right, std::vector<std::vector<int>>& steps) {
    if (left < right) {
        int mid = left + (right - left) / 2;
        mergeSort(arr, left, mid, steps);
        mergeSort(arr, mid + 1, right, steps);
        merge(arr, left, mid, right, steps);
    }
}

// сортировка кучей
void heapify(std::vector<int>& arr, int n, int i, std::vector<std::vector<int>>& steps) {
    int largest = i;
    int left = 2 * i + 1;
    int right = 2 * i + 2;

    if (left < n && arr[left] > arr[largest]) {
        largest = left;
    }
    if (right < n && arr[right] > arr[largest]) {
        largest = right;
    }

    if (largest != i) {
        std::swap(arr[i], arr[largest]);
        recordStep(arr, steps);
        heapify(arr, n, largest, steps);
    }
}

void heapSort(std::vector<int>& arr, std::vector<std::vector<int>>& steps) {
    int n = arr.size();

    for (int i = n / 2 - 1; i >= 0; --i) {
        heapify(arr, n, i, steps);
    }
    for (int i = n - 1; i > 0; --i) {
        std::swap(arr[0], arr[i]);
        recordStep(arr, steps);
        heapify(arr, i, 0, steps);
    }
}

// Генерация файлов для всех сортировок
void generateLogs(const std::vector<int>& originalArray, const std::string& outputDir = ".") {
    std::vector<std::pair<std::string, void(*)(std::vector<int>&, std::vector<std::vector<int>>&)>> sorts = {
        {"bubble", bubbleSort},
        {"selection", selectionSort},
        {"insertion", insertionSort},
        {"quick", [](std::vector<int>& arr, std::vector<std::vector<int>>& steps) {
            quickSort(arr, 0, arr.size() - 1, steps);
        }},
        {"merge", [](std::vector<int>& arr, std::vector<std::vector<int>>& steps) {
            mergeSort(arr, 0, arr.size() - 1, steps);
        }},
        {"heap", heapSort}
    };

    for (const auto& [name, sortFunc] : sorts) {
        std::vector<int> arr = originalArray;               
        std::vector<std::vector<int>> steps;                
        recordStep(arr, steps);                              
        sortFunc(arr, steps);                                

        std::string filename = outputDir + "/" + name + ".txt";
        if (outputDir == ".") filename = name + ".txt";

        std::ofstream out(filename);
        if (!out.is_open()) {
            std::cerr << "Не удалось создать файл: " << filename << std::endl;
            continue;
        }
        out << arr.size() << "\n";
        for (const auto& state : steps) {
            for (size_t i = 0; i < state.size(); ++i) {
                out << state[i];
                if (i + 1 < state.size()) out << " ";
            }
            out << "\n";
        }
        out.close();

        std::cout << "Файл " << filename << " создан, шагов: " << steps.size() << std::endl;
    }
}

int main() {
    const int size = 30;
    std::vector<int> original(size);
    for (int i = 0; i < size; ++i) {
        original[i] = i + 1;
    }

    unsigned seed = std::chrono::system_clock::now().time_since_epoch().count();
    std::shuffle(original.begin(), original.end(), std::mt19937(seed));
    for (int v : original) std::cout << v << " ";
    generateLogs(original, ".");
    return 0;
}