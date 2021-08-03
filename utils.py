import asyncio
import curses
import random

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


async def draw_ship(canvas, ship_frames):
    max_row, max_column = canvas.getmaxyx()

    ship_row, ship_column = max_row // 2, max_column // 2
    while True:
        ship_frame = next(ship_frames)

        draw_frame(canvas, ship_row, ship_column, ship_frame)
        await asyncio.sleep(0)
        draw_frame(canvas, ship_row, ship_column, ship_frame, negative=True)

        rows_direction, columns_direction, space_pressed = read_controls(canvas)
        ship_row, ship_column = change_control(
            max_row, max_column, ship_row,
            ship_column, rows_direction, columns_direction
        )

