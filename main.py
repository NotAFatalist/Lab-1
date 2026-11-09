#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Лабораторная работа №1. Вариант 10.

Страна  : Швейцария
Узор    : j (два кольца, стоящие вплотную)
Функция : y = x / 3
Условие : числа от -3 до 3 и остальные

Запуск:  python main.py [flag|pattern|anim|diagram|graph|all]
         python main.py            # то же, что all

Идея решения: каждое изображение сначала собирается в двумерный "пиксельный"
буфер (список списков), а затем выводится в консоль escape-последовательностями.
Так рисунок действительно генерируется кодом, а не печатается готовыми строками.
"""

from __future__ import annotations

import os          # os.system("cls"/"clear") — очистка консоли
import sys         # sys.argv (режим запуска) и sys.stdout (кодировка)
import time        # time.sleep — пауза между кадрами анимации
from pathlib import Path   # удобный путь к sequence.txt рядом со скриптом

# --- escape-последовательности -------------------------------------------------
RESET = "\033[0m"                      # сброс цвета и стиля
RED_BG = "\033[38;5;160;48;5;160m"     # швейцарский красный (цвет символа и фона)
WHITE_BG = "\033[38;5;231;48;5;231m"   # белый
BLACK_BG = "\033[38;5;16;48;5;16m"     # чёрный (кольца узора)
GREY_BG = "\033[48;5;245m"             # серый фон (резерв)
RED = "\033[38;5;160m"                 # только цвет символа — для полос диаграммы
WHITE = "\033[38;5;231m"

CURSOR_HOME = "\033[H"        # курсор в левый верхний угол экрана
CLEAR_LINE = "\033[K"         # стереть строку от курсора до конца
CLEAR_SCREEN = "\033[2J"      # стереть весь экран

CELL = "██"                   # "пиксель" консоли: один символ занимает 2 знака

HERE = Path(__file__).resolve().parent   # папка, где лежит этот файл


# --- служебное -----------------------------------------------------------------
def enable_ansi() -> None:
    """Включает обработку ANSI-последовательностей в консоли Windows."""
    if os.name != "nt":              # на Linux/macOS VT уже работает — выходим
        return
    try:
        import ctypes                # ctypes даёт доступ к WinAPI
        kernel32 = ctypes.windll.kernel32            # библиотека ядра Windows
        handle = kernel32.GetStdHandle(-11)          # STD_OUTPUT_HANDLE — наша консоль
        mode = ctypes.c_uint32()                     # сюда GetConsoleMode запишет режим
        if kernel32.GetConsoleMode(handle, ctypes.byref(mode)):   # прочитали режим
            kernel32.SetConsoleMode(handle, mode.value | 0x0004)  # включили VT-обработку
    except Exception:
        pass                          # в старых консолях просто не будет цвета

    try:                              # чтобы русский текст не падал при выводе в файл
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


def clear_console() -> None:
    """Очистка консоли: os.system(cls/clear) + сброс курсора в начало."""
    os.system("cls" if os.name == "nt" else "clear")   # системная команда очистки
    print(CURSOR_HOME, end="")                          # курсор в левый верхний угол


def pause(seconds: float) -> None:
    """Короткая пауза — чтобы кадры анимации не мелькали слишком быстро."""
    time.sleep(seconds)


# --- 1. флаг Швейцарии ---------------------------------------------------------
def swiss_flag_grid(size: int = 16, thickness: int = 4, arm: int = 10) -> list[list[str]]:
    """Строит матрицу флага: 'R' — красный фон, 'W' — белый (крест).

    Флаг Швейцарии — квадрат с белым крестом, у которого все лучи одинаковой длины.
    """
    grid = [["R"] * size for _ in range(size)]   # квадрат, полностью красный
    center = size // 2                           # середина флага (столбец и строка)
    half = thickness // 2                        # половина толщины луча
    start = center - arm // 2                    # отступ от края до начала луча

    # вертикальный луч: идём по строкам, красим центральные столбцы в белый
    for row in range(start, start + arm):
        for col in range(center - half, center - half + thickness):
            grid[row][col] = "W"

    # горизонтальный луч: идём по строкам, но красим уже диапазон столбцов
    for row in range(center - half, center - half + thickness):
        for col in range(start, start + arm):
            grid[row][col] = "W"

    return grid                                  # готовая матрица 16x16


def render_grid(grid: list[list[str]], palette: dict[str, str]) -> None:
    """Выводит матрицу в консоль, закрашивая ячейки фоном из palette."""
    for row in grid:                                    # проходим по строкам
        line = "".join(palette.get(cell, "") + CELL for cell in row)  # каждая ячейка — 2 знака
        print(line + RESET)                             # сбрасываем цвет в конце строки


def flag() -> None:
    """Пункт 1: флаг Швейцарии."""
    print("Флаг Швейцарии (вариант 10)")
    print()
    render_grid(swiss_flag_grid(), {"R": RED_BG, "W": WHITE_BG})   # красный + белый крест
    print()


# --- 2. узор «j» ---------------------------------------------------------------
def ring_pattern_grid(radius_px: int = 112, hole_px: int = 64, gap_px: int = 6,
                      gamma: float = 0.85) -> list[list[int]]:
    """Строит узор «j»: два крупных круглых кольца, стоящих рядом, почти вплотную.

    Возвращает сетку, где каждая ячейка — номер серого цвета ANSI (231 — белый,
    232…255 — от почти чёрного к светлому). Чёткость достигается тремя приёмами:
      * большой размер — кольцо занимает 28 символов в диаметре, поэтому силуэт
        почти идеально круглый;
      * сглаживание — символ консоли ≈ 8×16 пикселей, каждая ячейка разбивается
        на субпиксели 8×16 (ровно по 1 px), и по доле субпикселей, попавших
        в кольцо, выбирается один из 24 оттенков серого;
      * gamma < 1 — краевая полоса полутонов сжимается, контур становится резче.
    """
    margin_px = 10                        # белое поле вокруг колец (минимум)
    total_px = 4 * radius_px + gap_px     # ширина пары колец вместе с зазором
    width = (total_px + 2 * margin_px + 7) // 8    # ширина сетки в символах
    height = (2 * radius_px + 2 * margin_px + 15) // 16  # и высота
    offset_x = (width * 8 - total_px) / 2   # ровные поля слева и справа
    offset_y = (height * 16 - 2 * radius_px) / 2  # и сверху/снизу

    center_y = offset_y + radius_px         # центр обоих колец по вертикали
    center_x1 = offset_x + radius_px        # центр левого кольца
    center_x2 = offset_x + 3 * radius_px + gap_px   # центр правого кольца

    sub_x, sub_y = 8, 16                    # субпикселей на символ (8×16 px)
    rows = []
    for row in range(height):               # проходим по строкам сетки
        line = []
        for col in range(width):            # и по столбцам
            inside = 0                      # сколько субпикселей попало в кольцо
            for sub_col in range(sub_x):    # субпиксели по горизонтали
                for sub_row in range(sub_y):   # и по вертикали (квадратные 1×1 px)
                    x = col * 8 + (sub_col + 0.5) * 8 / sub_x   # координаты в пикселях
                    y = row * 16 + (sub_row + 0.5) * 16 / sub_y
                    distance = min(         # расстояние до ближайшего центра
                        ((x - center_x1) ** 2 + (y - center_y) ** 2) ** 0.5,
                        ((x - center_x2) ** 2 + (y - center_y) ** 2) ** 0.5,
                    )
                    if hole_px <= distance <= radius_px:    # попали в кольцо
                        inside += 1
            fraction = inside / (sub_x * sub_y)     # доля клетки, занятая кольцом
            level = round(fraction ** gamma * 24)   # гамма-кривая делает контур резче
            line.append(231 if level == 0 else 232 + (24 - level))  # 231 — белый
        rows.append(line)
    return rows


def pattern(repeats: int = 1) -> None:
    """Пункт 2: узор «j» — два круглых кольца, стоящих рядом, почти вплотную.

    По умолчанию печатается сам элемент узора (два кольца); pattern(3) выведет
    его три раза подряд по вертикали через пустую строку.
    """
    grid = ring_pattern_grid()              # сетка оттенков серого
    print("Узор «j» (вариант 10)")
    print()
    for index in range(repeats):            # сколько раз показать узор
        for row in grid:                    # каждая строка сетки
            # одна ячейка = один символ «█» с фоном и текстом одного оттенка
            print("".join(f"\033[38;5;{grey};48;5;{grey}m█" for grey in row) + RESET)
        if index < repeats - 1:             # пустой ряд между повторами
            print("\033[48;5;231m" + " " * len(grid[0]) + RESET)
    print()


# --- 3. анимация ---------------------------------------------------------------
def animation(frames: int = 4, loops: int = 3, delay: float = 0.35) -> None:
    """Пункт 3: анимация из 3-4 кадров — «пульсирующий» крест на флаге.

    Кадр перерисовывается на месте: курсор возвращается в начало экрана,
    каждая строка перед выводом очищается (CLEAR_LINE).
    """
    thickness = (2, 4, 6, 4)          # толщина креста в каждом кадре
    arms = (8, 10, 12, 10)            # длина лучей в каждом кадре
    height = 16                       # высота флага

    clear_console()                   # начинаем с чистого экрана
    for _ in range(loops):            # несколько проходов, чтобы анимация была видна
        for index in range(min(frames, len(thickness))):     # перебираем кадры
            grid = swiss_flag_grid(                          # строим флаг под кадр
                size=height, thickness=thickness[index], arm=arms[index]
            )
            print(CURSOR_HOME, end="")                       # курсор в начало экрана
            for row in grid:                                 # перерисовываем строки
                line = "".join(
                    (RED_BG if cell == "R" else WHITE_BG) + CELL for cell in row
                )
                print(line + RESET + CLEAR_LINE)             # CLEAR_LINE убирает хвост
            print(CLEAR_LINE + f"Кадр {index + 1}/{frames}   {RESET}",
                  end="", flush=True)                        # подпись кадра
            pause(delay)                                     # ждём перед следующим кадром

    print(CURSOR_HOME, end="")                               # оставляем финальный кадр
    for row in swiss_flag_grid(height):                      # рисуем флаг целиком
        print("".join((RED_BG if c == "R" else WHITE_BG) + CELL for c in row)
              + RESET + CLEAR_LINE)
    print(CLEAR_LINE + "Готово." + RESET)


# --- 4. диаграмма --------------------------------------------------------------
def read_sequence(path: Path | None = None) -> list[float]:
    """Читает числовую последовательность из sequence.txt."""
    path = path or HERE / "sequence.txt"           # файл рядом со скриптом
    numbers = []
    for raw in path.read_text(encoding="utf-8").splitlines():   # по одной строке
        raw = raw.strip().replace(",", ".")        # нормализуем запятую в точку
        if raw:                                    # пропускаем пустые строки
            numbers.append(float(raw))             # строка -> число
    return numbers


def diagram(numbers: list[float] | None = None, width: int = 50) -> None:
    """Пункт 4: диаграмма процентного соотношения.

    Вариант 10: числа от -3 до 3 и остальные (сумма двух групп = 100 %).
    """
    numbers = numbers if numbers is not None else read_sequence()   # читаем данные
    inside = [x for x in numbers if -3.0 <= x <= 3.0]               # попали в диапазон
    outside = [x for x in numbers if not (-3.0 <= x <= 3.0)]        # не попали
    total = len(numbers)                                            # всего чисел

    print("Диаграмма числовой последовательности (вариант 10)")
    print(f"Файл: sequence.txt, всего чисел: {total}")
    print()

    # по очереди выводим две группы: подпись, количество, полоса, процент
    for label, group, color in (
        ("Числа от -3 до 3", inside, RED),
        ("Остальные числа ", outside, WHITE),
    ):
        percent = len(group) / total * 100 if total else 0.0    # доля группы
        length = max(1, round(percent / 100 * width)) if group else 0   # ширина полосы
        bar = "█" * length                                      # сама полоса
        print(f"{label}: {len(group):3d} шт. {color}{bar}{RESET} {percent:5.1f} %")

    print()
    print(f"Проверка: {len(inside)} + {len(outside)} = {len(inside) + len(outside)} чисел")


# --- 5. допзадание: график y = x / 3 ------------------------------------------
def build_plot(rows: int = 10, x_max: float = 9.0) -> list[list[str]]:
    """Строит в двумерном буфере первую четверть графика y = x / 3.

    Каждая точка функции — это ровно одна звёздочка: на каждый целый x = 0..9
    вычисляется y = x / 3, координаты переводятся в строку и столбец сетки,
    и в эту клетку ставится «*». В результате получается линия из точек,
    а не залитые ступеньки.
    """
    points = int(x_max) + 1              # количество точек: x = 0, 1, ..., 9
    y_max = x_max / 3                    # максимум функции на отрезке (y(9) = 3)
    grid = [[" "] * points for _ in range(rows)]   # пустое поле rows x points

    for x in range(points):              # по одной точке на каждый целый x
        y = x / 3                        # значение функции в этой точке
        row = round((1 - y / y_max) * (rows - 1))   # высота -> номер строки (0 — верх)
        grid[row][x] = "*"               # одна звёздочка = одна точка графика

    return grid


def graph(rows: int = 10, x_max: float = 9.0) -> None:
    """Допзадание: график y = x / 3 в первой четверти (линия из точек)."""
    print("График функции y = x / 3 (первая четверть)")
    print()
    grid = build_plot(rows, x_max)       # сначала строим, потом печатаем
    y_max = x_max / 3
    points = len(grid[0])

    # печатаем строки сетки: подпись по оси Y, черта оси и клетки (по 2 знака)
    for index, line in enumerate(grid):
        y_value = y_max * (1 - index / (rows - 1))   # подпись по оси Y
        print(f"{y_value:4.1f} |" + "".join(cell + " " for cell in line))

    print("     +" + "-" * (points * 2))  # ось X под сеткой

    axis = [" "] * (6 + points * 2)       # строка подписей по оси X
    for tick in range(0, int(x_max) + 1, 3):    # подписываем 0, 3, 6, 9
        position = 6 + tick * 2           # позиция подписи под своим столбцом
        for offset, symbol in enumerate(str(tick)):   # вписываем цифры
            axis[position + offset] = symbol
    print("".join(axis).rstrip())


# --- точка входа ---------------------------------------------------------------
# имя режима -> функция, которая его выполняет
TASKS = {
    "flag": flag,
    "pattern": pattern,
    "anim": animation,
    "diagram": diagram,
    "graph": graph,
}


def main(argv: list[str]) -> int:
    enable_ansi()                                  # включаем цвета в консоли
    mode = argv[1] if len(argv) > 1 else "all"     # режим из аргумента командной строки

    if mode == "all":                              # всё подряд, с паузами между пунктами
        flag()
        pause(1)
        pattern()
        pause(1)
        diagram()
        pause(1)
        graph()
        pause(1)
        animation()
        return 0

    task = TASKS.get(mode)                         # функция выбранного режима
    if task is None:                               # неизвестный режим — подсказка
        print(__doc__)
        print("Доступные режимы:", ", ".join(TASKS), "или all")
        return 2

    task()                                         # выполняем один пункт
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))               # запуск только при прямом вызове
