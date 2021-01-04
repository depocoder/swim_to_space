import time
import curses
import asyncio


async def blink(canvas, row, column, symbol='*'):
    while True:
        canvas.addstr(row, column, symbol, curses.A_DIM)
        await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        await asyncio.sleep(0)

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        await asyncio.sleep(0)


def draw_stars(canvas):
    courutines = []
    for courutine_row in range(1, 19):
        courutines.append(blink(canvas, row=courutine_row, column=20))
    while True:
        for courutine in courutines:
            courutine.send(None)
            draw_border(canvas)
            canvas.border()
            canvas.refresh()
            time.sleep(0.01)


if __name__ == '__main__':
    curses.initscr()
    curses.update_lines_cols()
    curses.curs_set(False)
    curses.wrapper(draw_stars)
