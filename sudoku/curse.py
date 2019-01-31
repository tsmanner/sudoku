import curses
import getpass
import inspect # For linenumber debugging
from sudoku import Board, InvalidValueError, cull_board, generate_board
import time


class CursesFrame:
    attributes = {
        "window",
        "pary",
        "parx",
        "maxy",
        "maxx",
    }

    def __init__(self, window):
        self.window = window
        self.pary, self.parx = window.getparyx()
        self.maxy, self.maxx = (i - 1 for i in window.getmaxyx())

    def __getattr__(self, attr):
        if attr in CursesFrame.attributes:
            return self.__getattribute__(attr)
        return self.window.__getattribute__(attr)

    def __setattr__(self, key, value):
        if key in CursesFrame.attributes:
            object.__setattr__(self, key, value)
        else:
            self.window.__setattr__(key, value)


class CursesBoard:
    def __init__(self, screen, autostart=True):
        self.screen = screen
        screen.timeout(50)
        curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
        # self.board = Board(3)
        self.board = cull_board(generate_board(), 0.6)
        self.current_board = Board(self.board)
        self.default_message = "WELCOME {}!".format(getpass.getuser()).upper()
        self.message_time = None
        self._row = 0
        self._col = 0
        self.max_row = self.board.rows + self.board.rows // self.board.unit
        self.max_col = 2 * (self.board.cols + self.board.cols // self.board.unit)
        self.board_win = CursesFrame(self.screen.subwin(self.max_row+2, self.max_col+2, 0, 0))
        self.message_win = CursesFrame(self.screen.subwin(1, curses.COLS-1, self.board_win.pary + self.board_win.maxy, 0))
        self.help_win = CursesFrame(self.screen.subwin(1, curses.COLS-1, self.message_win.pary + self.message_win.maxy + 1, 0))
        self.board_win.refresh()
        self.initialize()
        self._message(self.default_message)
        self._run = autostart
        if self._run:
            self.mainloop()

    @property
    def row(self):
        return self._row

    @row.setter
    def row(self, value):
        self._row = value if 0 <= value < self.current_board.rows else self._row
        self.screen.move(*self.cursor())

    @property
    def col(self):
        return self._col

    @col.setter
    def col(self, value):
        self._col = value if 0 <= value < self.current_board.cols else self._col
        self.screen.move(*self.cursor())

    @property
    def coordinate(self):
        return self.row, self.col

    @coordinate.setter
    def coordinate(self, value):
        self.row = value[0]
        self.col = value[1]
        self.screen.move(*self.cursor())

    def cursor(self, row=None, col=None):
        row = row if row is not None else self.row
        col = col if col is not None else self.col
        y = row + 1 + row // self.board.unit
        x = 2 * col + 2 + 2 * (col // self.board.unit)
        return y, x

    def initialize(self):
        for row in range(0, self.board_win.maxy):
            # HORIZONTAL BORDER
            if row % 4 == 0:
                for col in range(self.board_win.maxx):
                    self.board_win.addch(row, col, curses.ACS_HLINE)
                # TOP (UPPER CORNERs and BOTTOM TEEs)
                if row == 0:
                    for col in range(0, self.board_win.maxx, 2 * self.board.unit + 2):
                        self.board_win.addch(row, col, curses.ACS_TTEE)
                    self.board_win.addch(row, 0, curses.ACS_ULCORNER)
                    self.board_win.addch(row, self.board_win.maxx-1, curses.ACS_URCORNER)
                # BOTTOM (LOWER CORNERs and TOP TEEs)
                elif row == self.board_win.maxy - 1:
                    for col in range(0, self.board_win.maxx, 2 * self.board.unit + 2):
                        self.board_win.addch(row, col, curses.ACS_BTEE)
                    self.board_win.addch(row, 0, curses.ACS_LLCORNER)
                    self.board_win.addch(row, self.board_win.maxx-1, curses.ACS_LRCORNER)
                # MIDDLE (PLUSes, LEFT TEE, and RIGHT TEE)
                else:
                    for col in range(0, self.board_win.maxx, 2 * self.board.unit + 2):
                        self.board_win.addch(row, col, curses.ACS_PLUS)
                    self.board_win.addch(row, 0, curses.ACS_LTEE)
                    self.board_win.addch(row, self.board_win.maxx-1, curses.ACS_RTEE)
            # VERTICAL BORDER
            else:
                for col in range(0, self.board_win.maxx, 2 * self.board.unit + 2):
                    self.board_win.addch(row, col, curses.ACS_VLINE)
        self.help_win.addnstr(0, 0, "^ up  v down  < left  > right  q quit", self.help_win.maxx)
        self.refresh()

    def refresh(self):
        failmask = self.current_board.check()
        for row in range(self.current_board.rows):
            for col in range(self.current_board.cols):
                ch = str(self.current_board[(row, col)]) if (row, col) in self.current_board else " "
                cursor = self.cursor(row, col)
                options = 0

                if failmask[(row, col)]:
                    options |= curses.A_UNDERLINE | curses.color_pair(1)
                if (row, col) in self.board:
                    options |= curses.A_BOLD
                self.board_win.addch(*cursor, ch, options)
        self.screen.move(*self.cursor())
        self.help_win.refresh()
        self.board_win.refresh()

    def message(self, message):
        self.message_time = time.time()
        self._message(message)

    def _message(self, message):
        self.message_win.clear()
        self.message_win.addnstr(0, 0, message, self.message_win.maxx)
        self.message_win.refresh()
        self.screen.move(*self.cursor())

    def clear_cell(self):
        if self.coordinate in self.current_board:
            self.message("CLEAR  {}".format(self.coordinate))
            del self.current_board[self.coordinate]
            self.refresh()
            self.current_board.check()

    def quit(self):
        self._run = False

    def mainloop(self):
        self._run = True
        while self._run:
            if self.message_time and (time.time() - self.message_time) > 2:
                self.message_time = None
                self._message(self.default_message)
            try:
                ch = self.screen.getkey()
            except curses.error:  # Handle delay getkey timeout without input
                continue
            if ch == -1:  # Handle delay getkey/getch timeout without input
                continue
            elif ch == 'q':
                self.quit()
            elif ch == 'KEY_UP':
                self.row -= 1
            elif ch == 'KEY_DOWN':
                self.row += 1
            elif ch == 'KEY_LEFT':
                self.col -= 1
            elif ch == 'KEY_RIGHT':
                self.col += 1
            elif self.coordinate not in self.board:
                if ch in {'KEY_DC', 'KEY_BACKSPACE', ' '}:
                    self.clear_cell()
                else:
                    try:
                        i = int(ch)
                        if self.current_board[self.coordinate] == i:
                            self.clear_cell()
                        else:
                            self.current_board[self.coordinate] = i
                            self.refresh()
                            self.message("INSERT {}: {}".format(self.coordinate, i))
                    except ValueError:
                        self.message("UNUSED KEY {}".format(bytes(ch, "utf-8")))
            elif self.coordinate in self.board:
                self.message("Can't Alter Cell {}".format(self.coordinate))
            else:
                self.message("ERROR BAD '{}'".format(self.coordinate))


if __name__ == '__main__':
    curses.wrapper(CursesBoard)
