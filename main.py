import time
import curses
import asyncio


async def blink(canvas, row, column, symbol='*'):
    while True:
        canvas.addstr(row, column, symbol, curses.A_DIM)
        await asyncio.sleep(0)

        time.sleep(2)
        canvas.addstr(row, column, symbol)
        await asyncio.sleep(0)

        time.sleep(0.3)
        canvas.addstr(row, column, symbol, curses.A_BOLD)
        await asyncio.sleep(0)

        time.sleep(0.5)
        canvas.addstr(row, column, symbol)
        await asyncio.sleep(0)
        time.sleep(0.3)


def draw_stars(canvas):
    courutines = []
    for courutine_row in range(1, 19):
        courutines.append(blink(canvas, row=courutine_row, column=20))
    while True:
        for courutine in courutines:
            courutine.send(None)
            canvas.border()
            canvas.refresh()


if __name__ == '__main__':
    curses.initscr()
    curses.update_lines_cols()
    curses.curs_set(False)
    curses.wrapper(draw_stars)
