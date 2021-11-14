import asyncio
import curses
import random

from physics import update_speed
from settings import *


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


def draw_frame(canvas, start_row, start_column, text, negative=False):
    """Draw multiline text fragment on canvas, erase text instead of drawing if negative=True is specified."""

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


async def draw_ship(canvas, ship_frames, coroutines: list):
    max_row, max_column = canvas.getmaxyx()

    ship_row, ship_column = max_row // 2, max_column // 2
    row_speed = column_speed = 0
    while True:
        ship_frame = next(ship_frames)

        draw_frame(canvas, ship_row, ship_column, ship_frame)
        await asyncio.sleep(0)
        await asyncio.sleep(0)
        draw_frame(canvas, ship_row, ship_column, ship_frame, negative=True)

        rows_direction, columns_direction, space_pressed = read_controls(canvas)

        ship_row_before, ship_column_before = ship_row, ship_column
        ship_row, ship_column = change_control(
            max_row, max_column, ship_row,
            ship_column, rows_direction, columns_direction
        )
        row_speed, column_speed = update_speed(
            row_speed, column_speed, ship_row - ship_row_before, ship_column - ship_column_before
        )
        ship_row += row_speed
        ship_column += column_speed

        if space_pressed:
            coroutines.append(fire(canvas, ship_row, ship_column + PIXELS_TO_CENTER))


async def fly_garbage(canvas, column, garbage_frame, speed=0.5):
    """Animate garbage, flying from top to bottom. Сolumn position will stay same, as specified on start."""
    rows_number, columns_number = canvas.getmaxyx()

    column = max(column, 0)
    column = min(column, columns_number - 1)

    row = 0

    while row < rows_number:
        draw_frame(canvas, row, column, garbage_frame)
        await asyncio.sleep(0)
        draw_frame(canvas, row, column, garbage_frame, negative=True)
        row += speed

