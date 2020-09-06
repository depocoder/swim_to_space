import time
import curses
import asyncio


async def blink(canvas, symbol='*'):
    row, column = (5, 20)
    while True:
        canvas.addstr(row, column, symbol, curses.A_DIM)
        await asyncio.sleep(2)

        canvas.addstr(row, column, symbol)
        await asyncio.sleep(0.3)

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        await asyncio.sleep(0.3)

        canvas.addstr(row, column, symbol)
        await asyncio.sleep(0.5)


"""def draw(canvas):
    row, column = (5, 20)
    for brightness, times in ((curses.A_DIM, 2), (curses.A_NORMAL, 0.3), (curses.A_BOLD, 0.3), (curses.A_NORMAL, 0.5)):
        canvas.addstr(row, column, '*****', brightness)
        canvas.border()
        canvas.refresh()
        time.sleep(times)"""
  

if __name__ == '__main__':
    while True:
        curses.update_lines_cols()
        curses.wrapper(blink)
        curses.curs_set(False)
