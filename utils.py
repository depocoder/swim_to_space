import asyncio
import curses
import random

from physics import update_speed
from settings import *


def get_garbage_delay_tics(year):
    if year < 1961:
        return 25
    elif year < 1969:
        return 20
    elif year < 1981:
        return 14
    elif year < 1995:
        return 10
    elif year < 2010:
        return 8
    elif year < 2020:
        return 6
    else:
        return 2


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


async def fire(canvas, start_row, start_column, obstacles: list, rows_speed=-0.3, columns_speed=0):
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
        for obstacle in obstacles:
            if obstacle.has_collision(row, column):
                obstacle.is_hit = True
                return


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
    if (ship_row + BORDER + rows_direction) > 0 > rows_direction:
        ship_row += rows_direction
    elif (ship_row + SHIP_ROW_SIZE + rows_direction) < max_row and rows_direction > 0:
        ship_row += rows_direction
    if (ship_column + BORDER + columns_direction) > 0 > columns_direction:
        ship_column += columns_direction
    elif (ship_column + SHIP_COLUMN_SIZE + columns_direction) < max_column and columns_direction > 1:
        ship_column += columns_direction
    return ship_row, ship_column


async def draw_ship(canvas, ship_frames, coroutines: list, obstacles: list, year: int):
    max_row, max_column = canvas.getmaxyx()

    ship_row, ship_column = max_row // 2, max_column // 2
    row_speed = column_speed = 0
    while True:
        ship_frame = next(ship_frames)

        draw_frame(canvas, ship_row, ship_column, ship_frame)
        await asyncio.sleep(0)
        draw_frame(canvas, ship_row, ship_column, ship_frame, negative=True)

        rows_direction, columns_direction, space_pressed = read_controls(canvas)

        row_speed, column_speed = update_speed(
            row_speed, column_speed, rows_direction, columns_direction
        )

        rows_direction += rows_direction + row_speed
        columns_direction = columns_direction + column_speed

        ship_row, ship_column = change_control(
            max_row, max_column, ship_row,
            ship_column, rows_direction, columns_direction
        )

        if space_pressed and year >= 2020:
            coroutines.append(fire(canvas, ship_row, ship_column + PIXELS_TO_CENTER, obstacles))
        for obstacle in obstacles:
            if obstacle.has_collision(ship_row, ship_column):
                await show_gameover(canvas)


async def show_gameover(canvas):
    with open('frames/gameover.txt') as file:
        gameover_frame = file.read()
    frame_row, frame_column = get_frame_size(gameover_frame)
    max_row, max_column = canvas.getmaxyx()
    gameover_row, gameover_column = max_row // 2 - frame_row // 2, max_column // 2 - frame_column // 2
    while True:
        draw_frame(canvas, gameover_row, gameover_column, gameover_frame)
        await asyncio.sleep(0)


def get_frame_size(text):
    """Calculate size of multiline text fragment, return pair — number of rows and colums."""

    lines = text.splitlines()
    rows = len(lines)
    columns = max([len(line) for line in lines])
    return rows, columns


async def fly_garbage(canvas, column, garbage_frame, obstacle, obstacles, speed=0.5):
    """Animate garbage, flying from top to bottom. Column position will stay same, as specified on start."""
    rows_number, columns_number = canvas.getmaxyx()

    column = max(column, 0)
    column = min(column, columns_number - 1)

    row = 0
    frame_row, frame_column = get_frame_size(garbage_frame)
    while row < rows_number:
        draw_frame(canvas, row, column, garbage_frame)
        await asyncio.sleep(0)
        draw_frame(canvas, row, column, garbage_frame, negative=True)
        row += speed
        obstacle.row = row
        if obstacle.is_hit:
            await explode(canvas, row + frame_row // 2, column + frame_column // 2)
            break
    obstacles.remove(obstacle)


EXPLOSION_FRAMES = [
    """\
           (_)
       (  (   (  (
      () (  (  )
        ( )  ()
    """,
    """\
           (_)
       (  (   (
         (  (  )
          )  (
    """,
    """\
            (
          (   (
         (     (
          )  (
    """,
    """\
            (
              (
            (
    """,
]


async def explode(canvas, center_row, center_column):
    rows, columns = get_frame_size(EXPLOSION_FRAMES[0])
    corner_row = center_row - rows / 2
    corner_column = center_column - columns / 2

    curses.beep()
    for frame in EXPLOSION_FRAMES:

        draw_frame(canvas, corner_row, corner_column, frame)

        await asyncio.sleep(0)
        draw_frame(canvas, corner_row, corner_column, frame, negative=True)
        await asyncio.sleep(0)
