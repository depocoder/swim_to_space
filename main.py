import os
import time
import curses
import random
from itertools import cycle

from settings import BORDER
from utils import blink, draw_ship


def get_ship_frames():
    frames = []
    frame_dirs = [os.path.join('rocket_frames', frame) for frame in os.listdir('rocket_frames')]
    for frame_dir in frame_dirs:
        with open(frame_dir, "r") as my_file:
            frame = my_file.read()
            frames.append(frame)
            frames.append(frame)
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


def draw(canvas):
    canvas.nodelay(True)
    coroutines = generate_stars_coroutines(canvas)
    ship_frames = get_ship_frames()
    coroutines.append(draw_ship(canvas, ship_frames))
    while True:
        for coroutine in coroutines:
            try:
                coroutine.send(None)
            except StopIteration:
                coroutines.remove(coroutine)
        canvas.border()
        canvas.refresh()
        time.sleep(0.1)


if __name__ == '__main__':
    curses.initscr()
    curses.update_lines_cols()
    curses.curs_set(False)
    curses.wrapper(draw)
