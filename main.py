#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Лабораторная работа №1. Вариант 10.

Страна  : Швейцария
Узор    : j (два кольца, стоящие вплотную)
Функция : y = x / 3
Условие : числа от -3 до 3 и остальные

Запуск:  python main.py [flag|pattern|anim|diagram|graph|all]
         python main.py            # то же, что all

Все изображения строятся в двумерном буфере и выводятся escape-последовательностями
(цвет фона, управление курсором), а не "вручную" подобранными строками.
"""

from __future__ import annotations

import os
import sys
import time
from pathlib import Path

# --- escape-последовательности -------------------------------------------------
RESET = "\033[0m"
RED_BG = "\033[38;5;160;48;5;160m"     # швейцарский красный
WHITE_BG = "\033[38;5;231;48;5;231m"   # белый
BLACK_BG = "\033[38;5;16;48;5;16m"     # чёрный (узор)
GREY_BG = "\033[48;5;245m"             # серый фон для диаграммы
RED = "\033[38;5;160m"
WHITE = "\033[38;5;231m"

CURSOR_HOME = "\033[H"        # курсор в левый верхний угол
CLEAR_LINE = "\033[K"         # стереть строку до конца
CLEAR_SCREEN = "\033[2J"      # стереть весь экран

CELL = "██"                   # "пиксель" консоли

HERE = Path(__file__).resolve().parent


# --- служебное -----------------------------------------------------------------
def enable_ansi() -> None:
    """Включает обработку ANSI-последовательностей в консоли Windows."""
    if os.name != "nt":
        return
    try:
        import ctypes

        kernel32 = ctypes.windll.kernel32
        handle = kernel32.GetStdHandle(-11)  # STD_OUTPUT_HANDLE
        mode = ctypes.c_uint32()
        if kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
            kernel32.SetConsoleMode(handle, mode.value | 0x0004)  # ENABLE_VIRTUAL_TERMINAL_PROCESSING
    except Exception:
        pass

    try:  # чтобы русский текст не падал при перенаправлении вывода в файл
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


def clear_console() -> None:
    """Очистка консоли: os.system(cls/clear) + сброс курсора."""
    os.system("cls" if os.name == "nt" else "clear")
    print(CURSOR_HOME, end="")


def pause(seconds: float) -> None:
    time.sleep(seconds)


# --- 1. флаг Швейцарии ---------------------------------------------------------
def swiss_flag_grid(size: int = 16, thickness: int = 4, arm: int = 10) -> list[list[str]]:
    """Строит матрицу флага: 'R' — красный фон, 'W' — белый (крест).

    Флаг Швейцарии — квадрат с белым крестом, у которого лучи одинаковой длины.
    """
    grid = [["R"] * size for _ in range(size)]
    center = size // 2
    half = thickness // 2
    start = center - arm // 2

    for row in range(start, start + arm):          # вертикальный луч
        for col in range(center - half, center - half + thickness):
            grid[row][col] = "W"

    for row in range(center - half, center - half + thickness):  # горизонтальный луч
        for col in range(start, start + arm):
            grid[row][col] = "W"

    return grid


def render_grid(grid: list[list[str]], palette: dict[str, str]) -> None:
    """Выводит матрицу в консоль, закрашивая ячейки фоном из palette."""
    for row in grid:
        line = "".join(palette.get(cell, "") + CELL for cell in row)
        print(line + RESET)


def flag() -> None:
    """Пункт 1: флаг Швейцарии."""
    print("Флаг Швейцарии (вариант 10)")
    print()
    render_grid(swiss_flag_grid(), {"R": RED_BG, "W": WHITE_BG})
    print()


# --- 2. узор «j» ---------------------------------------------------------------
def ring_tile(height: int = 7, hole: float = 1.6) -> list[list[str]]:
    """Один элемент узора «j»: два кольца, касающихся друг друга.

    Каждая ячейка — точка с координатами центра; кольцо — множество точек,
    расстояние от которых до центра одного из кругов лежит в (hole, radius).
    """
    radius = height / 2
    width = 2 * height
    centers = (
        (radius, radius),
        (radius + width / 2, radius),
    )

    tile = []
    for row in range(height):
        line = []
        for col in range(width):
            px, py = col + 0.5, row + 0.5
            distance = min(((px - cx) ** 2 + (py - cy) ** 2) ** 0.5 for cx, cy in centers)
            line.append("#" if hole <= distance <= radius else ".")
        tile.append(line)
    return tile


def pattern(tile_cols: int = 2, tile_rows: int = 2) -> None:
    """Пункт 2: повторяющийся узор «j»."""
    tile = ring_tile()
    palette = {"#": BLACK_BG, ".": WHITE_BG}

    print("Узор «j» (вариант 10)")
    print()
    for _ in range(tile_rows):
        for row in tile:
            print("".join(palette[cell] + CELL for cell in row) * tile_cols + RESET)
    print()


# --- 3. анимация ---------------------------------------------------------------
def animation(frames: int = 4, loops: int = 3, delay: float = 0.35) -> None:
    """Пункт 3: анимация из 3-4 кадров — «пульсирующий» крест на флаге.

    Кадр перерисовывается на месте: курсор возвращается в начало экрана,
    каждая строка перед выводом очищается (CLEAR_LINE).
    """
    thickness = (2, 4, 6, 4)          # толщина креста в кадрах
    arms = (8, 10, 12, 10)            # длина лучей в кадрах
    height = 16

    clear_console()
    for _ in range(loops):
        for index in range(min(frames, len(thickness))):
            grid = swiss_flag_grid(size=height, thickness=thickness[index], arm=arms[index])
            print(CURSOR_HOME, end="")
            for row in grid:
                line = "".join(
                    (RED_BG if cell == "R" else WHITE_BG) + CELL for cell in row
                )
                print(line + RESET + CLEAR_LINE)
            print(CLEAR_LINE + f"Кадр {index + 1}/{frames}   {RESET}", end="", flush=True)
            pause(delay)

    print(CURSOR_HOME, end="")
    for row in swiss_flag_grid(height):
        print("".join((RED_BG if c == "R" else WHITE_BG) + CELL for c in row) + RESET + CLEAR_LINE)
    print(CLEAR_LINE + "Готово." + RESET)


# --- 4. диаграмма --------------------------------------------------------------
def read_sequence(path: Path | None = None) -> list[float]:
    """Читает числовую последовательность из sequence.txt."""
    path = path or HERE / "sequence.txt"
    numbers = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        raw = raw.strip().replace(",", ".")
        if raw:
            numbers.append(float(raw))
    return numbers


def diagram(numbers: list[float] | None = None, width: int = 50) -> None:
    """Пункт 4: диаграмма процентного соотношения.

    Вариант 10: числа от -3 до 3 и остальные (сумма двух групп = 100 %).
    """
    numbers = numbers if numbers is not None else read_sequence()
    inside = [x for x in numbers if -3.0 <= x <= 3.0]
    outside = [x for x in numbers if not (-3.0 <= x <= 3.0)]
    total = len(numbers)

    print("Диаграмма числовой последовательности (вариант 10)")
    print(f"Файл: sequence.txt, всего чисел: {total}")
    print()

    for label, group, color in (
        ("Числа от -3 до 3", inside, RED),
        ("Остальные числа ", outside, WHITE),
    ):
        percent = len(group) / total * 100 if total else 0.0
        length = max(1, round(percent / 100 * width)) if group else 0   # ширина бара
        bar = "█" * length
        print(f"{label}: {len(group):3d} шт. {color}{bar}{RESET} {percent:5.1f} %")

    print()
    print(f"Проверка: {len(inside)} + {len(outside)} = {len(inside) + len(outside)} чисел")


# --- 5. допзадание: график y = x / 3 ------------------------------------------
def build_plot(rows: int = 9, cols: int = 41, x_max: float = 9.0) -> list[list[str]]:
    """Строит в двумерном буфере первую четверть графика y = x / 3.

    rows >= 9 — по требованию задания; буфер заполняется точками кривой,
    оси рисуются отдельно, поэтому график именно генерируется, а не печатается.
    """
    y_max = x_max / 3
    buffer = [[" "] * cols for _ in range(rows)]

    for row in range(rows):                     # ось Y
        buffer[row][0] = "|"
    for col in range(cols):                     # ось X
        buffer[rows - 1][col] = "-"
    buffer[rows - 1][0] = "+"

    steps = 4 * cols
    for step in range(steps + 1):
        x = x_max * step / steps
        y = x / 3
        col = round(x / x_max * (cols - 1))
        row = round((1 - y / y_max) * (rows - 1))
        if row == rows - 1 and col == 0:        # начало координат не затираем
            continue
        buffer[row][col] = "*"

    return buffer


def graph(rows: int = 9, cols: int = 41, x_max: float = 9.0) -> None:
    """Допзадание: график y = x / 3 в первой четверти (9 строк в высоту)."""
    print("График функции y = x / 3 (первая четверть)")
    print()
    buffer = build_plot(rows, cols, x_max)
    y_max = x_max / 3

    for index, row in enumerate(buffer):
        y_value = y_max * (1 - index / (rows - 1))
        print(f"{y_value:4.1f} " + "".join(row))

    axis = [" "] * (cols + 5)
    for tick in range(0, int(x_max) + 1, 3):
        position = 5 + round(tick / x_max * (cols - 1))
        for offset, symbol in enumerate(str(tick)):
            axis[position + offset] = symbol
    print("".join(axis).rstrip())


# --- точка входа ---------------------------------------------------------------
TASKS = {
    "flag": flag,
    "pattern": pattern,
    "anim": animation,
    "diagram": diagram,
    "graph": graph,
}


def main(argv: list[str]) -> int:
    enable_ansi()
    mode = argv[1] if len(argv) > 1 else "all"

    if mode == "all":
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

    task = TASKS.get(mode)
    if task is None:
        print(__doc__)
        print("Доступные режимы:", ", ".join(TASKS), "или all")
        return 2

    task()
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
