import os
import time
import curses
import random
from itertools import cycle

from settings import BORDER
from physics import update_speed
from utils import blink, draw_ship, fly_garbage, sleep

COROUTINES = []


def get_cycle_frames(dir_to_frames, need_double=True):
    frames = []
    frame_dirs = [os.path.join(f'frames/{dir_to_frames}', frame) for frame in os.listdir(f'frames/{dir_to_frames}')]
    for frame_dir in frame_dirs:
        with open(frame_dir, "r") as my_file:
            frame = my_file.read()
            frames.append(frame)
            if need_double:
                frames.append(frame)
    return cycle(frames)


def generate_stars_coroutines(canvas, count: int = 200) -> list:
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


async def fill_orbit_with_garbage(canvas):
    max_row, max_column = canvas.getmaxyx()
    garbage_frames = get_cycle_frames('garbage_frames', need_double=False)
    while True:
        await sleep(15)
        global COROUTINES
        garbage_column = random.randint(1, max_column + BORDER)
        COROUTINES.append(
            fly_garbage(canvas, column=garbage_column, garbage_frame=next(garbage_frames))
        )


def draw(canvas):
    canvas.nodelay(True)
    COROUTINES.append(fill_orbit_with_garbage(canvas))
    COROUTINES.extend(generate_stars_coroutines(canvas))
    ship_frames = get_cycle_frames('rocket_frames')
    COROUTINES.append(draw_ship(canvas, ship_frames))
    while True:
        for coroutine in COROUTINES:
            try:
                coroutine.send(None)
            except StopIteration:
                COROUTINES.remove(coroutine)
        canvas.border()
        canvas.refresh()
        time.sleep(0.1)


if __name__ == '__main__':
    curses.initscr()
    curses.update_lines_cols()
    curses.curs_set(False)
    curses.wrapper(draw)
