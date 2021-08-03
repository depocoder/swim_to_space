import os
import time
import curses
import random
from itertools import cycle

from utils import blink, read_controls, draw_frame


BORDER = - 1
SHIP_ROW_SIZE = 10
SHIP_COLUMN_SIZE = 6


def get_ship_frames():
    frames = []
    frame_dirs = [os.path.join('rocket_frames', frame) for frame in os.listdir('rocket_frames')]
    for frame_dir in frame_dirs:
        with open(frame_dir, "r") as my_file:
            frames.append(my_file.read())
    return cycle(frames)


def generate_stars_coroutines(canvas, count: int = 1000) -> list:
    coroutines = []
    max_row, max_column = canvas.getmaxyx()
    stars_position = set()
    while len(stars_position) < count:
        row = random.randint(1, max_row + BORDER)
        column = random.randint(1, max_column + BORDER)
        position_star = (row, column)
        if position_star in stars_position:
            continue
        symbol = random.choice('+*.:')
        coroutine = blink(canvas, row=row, column=column, symbol=symbol)
        coroutines.append(coroutine)
        stars_position.add(position_star)
    return coroutines


def change_control(
        max_row, max_column, ship_row, ship_column, rows_direction, columns_direction
):
    if ship_row + BORDER != 0 and rows_direction == -1:
        ship_row += rows_direction
    elif ship_row + SHIP_ROW_SIZE != max_row and rows_direction == 1:
        ship_row += rows_direction
    if ship_column + BORDER != 0 and columns_direction == -1:
        ship_column += columns_direction
    elif ship_column + SHIP_COLUMN_SIZE != max_column and columns_direction == 1:
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
        coroutines.append(draw_frame(canvas, ship_row, ship_column, ship_frame))
        for coroutine in coroutines:
            try:
                coroutine.send(None)
            except StopIteration:
                coroutines.remove(coroutine)
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
