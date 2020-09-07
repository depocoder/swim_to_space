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


def draw(canvas):
    courutine = blink(canvas, row=5, column=20)
    for i in range(5):
        courutine.send(None)
        canvas.border()
        canvas.refresh()
        time.sleep(1)
  

if __name__ == '__main__':
    while True:
        curses.update_lines_cols()
        curses.wrapper(draw)
        curses.curs_set(False)
