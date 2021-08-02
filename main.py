import os
import time
import curses
import random
from itertools import cycle

from utils import blink, read_controls, draw_frame


def get_ship_frames():
    frames = []
    frames_name = os.listdir(os.path.join(os.getcwd(), 'rocket_frames'))
    frames_dirs = [os.path.join(os.getcwd(), 'rocket_frames', frame_dir) for frame_dir in frames_name]
    for frame_dir in frames_dirs:
        with open(frame_dir, "r") as my_file:
            frames.append(my_file.read())
    return cycle(frames)


def generate_stars_coroutines(canvas, count: int = 100) -> list:
    coroutines = []
    max_row, max_column = canvas.getmaxyx()
    position_stars = set()
    for _ in range(1, count):
        row = random.randint(1, max_row - 1)
        column = random.randint(1, max_column - 1)
        position_star = (row, column)
        if position_star in position_stars:
            continue
        symbol = random.choice('+*.:')
        coroutine = blink(canvas, row=row, column=column, symbol=symbol)
        coroutines.append(coroutine)
        position_stars.add(position_star)
    return coroutines


def change_control(
        max_row, max_column, ship_row, ship_column, rows_direction, columns_direction
):
    if ship_row - 1 != 0 and rows_direction == -1:
        ship_row += rows_direction
    elif ship_row + 10 != max_row and rows_direction == 1:
        ship_row += rows_direction
    if ship_column - 1 != 0 and columns_direction == -1:
        ship_column += columns_direction
    elif ship_column + 6 != max_column and columns_direction == 1:
        ship_column += columns_direction
    return ship_row, ship_column


def draw(canvas):
    canvas.nodelay(True)
    coroutines = generate_stars_coroutines(canvas)
    max_row, max_column = canvas.getmaxyx()

    ship_row, ship_column = max_row // 2, max_column // 2
    ship_frames = get_ship_frames()
    ship_frame = next(ship_frames)
    while True:
        rows_direction, columns_direction, space_pressed = read_controls(canvas)
        ship_row, ship_column = change_control(
            max_row, max_column, ship_row,
            ship_column, rows_direction, columns_direction
        )
        draw_frame(canvas, ship_row, ship_column, ship_frame).send(None)
        [coroutine.send(None) for coroutine in coroutines]
        canvas.border()
        canvas.refresh()
        time.sleep(0.1)
        draw_frame(canvas, ship_row, ship_column, ship_frame, negative=True).send(None)
        ship_frame = next(ship_frames)


if __name__ == '__main__':
    curses.initscr()
    curses.update_lines_cols()
    curses.curs_set(False)
    curses.wrapper(draw)
