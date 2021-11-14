import asyncio
import os
import time
import curses
import random
from itertools import cycle

from obstacles import Obstacle, show_obstacles
from settings import BORDER, BORDER_PIXEL, PHRASES
from utils import blink, draw_ship, sleep, get_frame_size, draw_frame, fly_garbage, get_garbage_delay_tics

COROUTINES = []
OBSTACLES = []

YEAR = 1957



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


async def show_messages(canvas):
    message_template = "Year: {} {}"
    global YEAR
    while True:
        yr = message_template.format(YEAR, PHRASES.get(YEAR, ''))
        draw_frame(canvas, BORDER_PIXEL, BORDER_PIXEL, yr)
        await asyncio.sleep(0)
        draw_frame(canvas, BORDER_PIXEL, BORDER_PIXEL, yr, negative=True)


async def fill_orbit_with_garbage(canvas):
    max_row, max_column = canvas.getmaxyx()
    garbage_frames = get_cycle_frames('garbage_frames', need_double=False)
    global YEAR
    global COROUTINES
    while True:
        await sleep(get_garbage_delay_tics(YEAR))
        garbage_frame = next(garbage_frames)
        garbage_column = random.randint(1, max_column + BORDER)
        frame_row, frame_column = get_frame_size(garbage_frame)
        obstacle = Obstacle(0, garbage_column, frame_row, frame_column)
        OBSTACLES.append(obstacle)
        COROUTINES.append(
            fly_garbage(canvas, column=garbage_column,
                        garbage_frame=garbage_frame, obstacle=obstacle, obstacles=OBSTACLES)
        )


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


def draw(canvas):
    global YEAR
    canvas.nodelay(True)
    COROUTINES.append(fill_orbit_with_garbage(canvas))
    COROUTINES.extend(generate_stars_coroutines(canvas))
    ship_frames = get_cycle_frames('rocket_frames')
    COROUTINES.append(show_messages(canvas))
    COROUTINES.append(draw_ship(canvas, ship_frames, COROUTINES, obstacles=OBSTACLES, year=YEAR))
    start_time = time.time()
    while True:
        for coroutine in COROUTINES:
            try:
                coroutine.send(None)
            except StopIteration:
                COROUTINES.remove(coroutine)
        canvas.border()
        canvas.refresh()
        time.sleep(0.1)
        if (time.time() - start_time) // 1.5 > 0:
            YEAR += 1
            start_time = time.time()


if __name__ == '__main__':
    curses.initscr()
    curses.update_lines_cols()
    curses.curs_set(False)
    curses.wrapper(draw)
