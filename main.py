import time
import curses
import random
import asyncio


async def blink(canvas, row, column, symbol='*'):
    while True:
        canvas.addstr(row, column, symbol, curses.A_DIM)
        await asyncio.sleep(0)

        time.sleep(0.01)
        canvas.addstr(row, column, symbol)
        await asyncio.sleep(0)

        time.sleep(0.01)
        canvas.addstr(row, column, symbol, curses.A_BOLD)
        await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        await asyncio.sleep(0)


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


def draw_stars(canvas):
    courutines = []
    max_row, max_column = canvas.getmaxyx()
    positon_stars = []
    for courutine_row in range(1, 100):
        row = random.randint(1, max_row-1)
        column = random.randint(1, max_column-1)
        if [row, column] in positon_stars:
            continue
        symbol = random.choice('+*.:')
        courutine = blink(canvas, row=row, column=column, symbol=symbol)
        courutines.append(courutine)
        positon_stars.append([row, column])
        fire_cour = fire(canvas, 10, 6)

    while True:
        courutine = random.choice(courutines)
        courutine.send(None)
        fire_cour.send(None)
        canvas.refresh()
        canvas.border()
        time.sleep(0.1)


if __name__ == '__main__':
    curses.initscr()
    curses.update_lines_cols()
    curses.curs_set(False)
    curses.wrapper(draw_stars)
