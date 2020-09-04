import time
import curses


def draw(canvas):
    row, column = (5, 20)
    for brightness, times in ((curses.A_DIM, 2), (curses.A_NORMAL, 0.3), (curses.A_BOLD, 0.3), (curses.A_NORMAL, 0.5)):
        canvas.addstr(row, column, '*', brightness)
        canvas.border()
        canvas.refresh()
        time.sleep(times)
  
if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
    curses.curs_set(False)
