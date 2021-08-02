import os
import time
import asyncio
import curses
import random
from itertools import cycle

SPACE_KEY_CODE = 32
LEFT_KEY_CODE = 260
RIGHT_KEY_CODE = 261
UP_KEY_CODE = 259
DOWN_KEY_CODE = 258


def read_controls(canvas):
    """Read keys pressed and returns tuple witl controls state."""

    rows_direction = columns_direction = 0
    space_pressed = False

    while True:
        pressed_key_code = canvas.getch()

        if pressed_key_code == -1:
            # https://docs.python.org/3/library/curses.html#curses.window.getch
            break

        if pressed_key_code == UP_KEY_CODE:
            rows_direction = -1

        if pressed_key_code == DOWN_KEY_CODE:
            rows_direction = 1

        if pressed_key_code == RIGHT_KEY_CODE:
            columns_direction = 1

        if pressed_key_code == LEFT_KEY_CODE:
            columns_direction = -1

        if pressed_key_code == SPACE_KEY_CODE:
            space_pressed = True

    return rows_direction, columns_direction, space_pressed


async def draw_frame(canvas, start_row, start_column, text, negative=False):
    """Draw multiline text fragment on canvas, erase text instead of drawing if negative=True is specified."""
    while True:
        rows_number, columns_number = canvas.getmaxyx()

        for row, line in enumerate(text.splitlines(), round(start_row)):
            if row < 0:
                continue

            if row >= rows_number:
                break

            for column, symbol in enumerate(line, round(start_column)):
                if column < 0:
                    continue

                if column >= columns_number:
                    break

                if symbol == ' ':
                    continue

                # Check that current position it is not in a lower right corner of the window
                # Curses will raise exception in that case. Don`t ask why…
                # https://docs.python.org/3/library/curses.html#curses.window.addch
                if row == rows_number - 1 and column == columns_number - 1:
                    continue

                symbol = symbol if not negative else ' '
                canvas.addch(row, column, symbol)
        await asyncio.sleep(0)


def get_ship_frames():
    frames = []
    frames_name = os.listdir(os.path.join(os.getcwd(), 'rocket_frames'))
    frames_dirs = [os.path.join(os.getcwd(), 'rocket_frames', frame_dir) for frame_dir in frames_name]
    for frame_dir in frames_dirs:
        with open(frame_dir, "r") as my_file:
            frames.append(my_file.read())
    return cycle(frames)


async def sleep(times: int):
    for _ in range(times):
        await asyncio.sleep(0)


async def blink(canvas, row, column, symbol='*'):
    canvas.addstr(row, column, symbol, curses.A_DIM)
    await sleep(random.randint(1, 100))

    while True:
        canvas.addstr(row, column, symbol, curses.A_DIM)
        await sleep(20)

        canvas.addstr(row, column, symbol)
        await sleep(3)

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        await sleep(5)

        canvas.addstr(row, column, symbol)
        await sleep(3)


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


async def fire(canvas, start_row, start_column, rows_speed=-0.3, columns_speed=0):
    """Display animation of gun shot, direction and speed can be specified."""

    row, column = start_row, start_column

    canvas.addstr(round(row), round(column), '*')
    await asyncio.sleep(0)

    canvas.addstr(round(row), round(column), 'O')
    await asyncio.sleep(0)
    canvas.addstr(round(row), round(column), ' ')

    row += rows_speed
    column += columns_speed

    symbol = '-' if columns_speed else '|'

    rows, columns = canvas.getmaxyx()
    max_row, max_column = rows - 1, columns - 1

    curses.beep()

    while 0 < row < max_row and 0 < column < max_column:
        canvas.addstr(round(row), round(column), symbol)
        await asyncio.sleep(0)
        canvas.addstr(round(row), round(column), ' ')
        row += rows_speed
        column += columns_speed


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
    fire_coroutines = []
    max_row, max_column = canvas.getmaxyx()

    ship_row, ship_column = max_row // 2, max_column // 2
    fire_coroutines.append(fire(canvas, 10, 6))
    fire_coroutines.append(fire(canvas, 5, 3))
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
