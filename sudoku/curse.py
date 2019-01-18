import curses
from sudoku import InvalidValueError, cull_board, generate_board


class CursesBoard:
    def __init__(self, screen):
        self.screen = screen
        curses.init_pair(1, 1, 0)
        self.board = cull_board(generate_board(), 0.6)
        self._row = 0
        self._col = 0
        self.initialize()
        self.mainloop()

    @property
    def row(self):
        return self._row

    @row.setter
    def row(self, value):
        self._row = value if 0 <= value < self.board.rows else self._row
        self.screen.move(*self.cursor())

    @property
    def col(self):
        return self._col

    @col.setter
    def col(self, value):
        self._col = value if 0 <= value < self.board.cols else self._col
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
        y = row + 1 + row // 3
        x = 2 * col + 2 + 2 * (col // 3)
        return y, x

    def initialize(self):
        self.screen.addstr( 0, 0, "+-------+-------+-------+")
        self.screen.addstr( 1, 0, "|       |       |       |")
        self.screen.addstr( 2, 0, "|       |       |       |")
        self.screen.addstr( 3, 0, "|       |       |       |")
        self.screen.addstr( 4, 0, "+-------+-------+-------+")
        self.screen.addstr( 5, 0, "|       |       |       |")
        self.screen.addstr( 6, 0, "|       |       |       |")
        self.screen.addstr( 7, 0, "|       |       |       |")
        self.screen.addstr( 8, 0, "+-------+-------+-------+")
        self.screen.addstr( 9, 0, "|       |       |       |")
        self.screen.addstr(10, 0, "|       |       |       |")
        self.screen.addstr(11, 0, "|       |       |       |")
        self.screen.addstr(12, 0, "+-------+-------+-------+")
        self.refresh()

    def refresh(self):
        for col in range(self.board.cols):
            for row in range(self.board.rows):
                ch = str(self.board[(row, col)]) if (row, col) in self.board else " "
                y = row + 1 + row // 3
                x = 2 * col + 2 + 2 * (col // 3)
                self.screen.addch(y, x, ch)
        self.screen.move(*self.cursor())
        self.screen.refresh()

    def mainloop(self):
        while True:
            ch = self.screen.getkey()
            if ch == 'q':
                break
            elif ch == '\n':
                continue
            elif ch == 'KEY_UP':
                self.row -= 1
            elif ch == 'KEY_DOWN':
                self.row += 1
            elif ch == 'KEY_LEFT':
                self.col -= 1
            elif ch == 'KEY_RIGHT':
                self.col += 1
            elif ch in {'KEY_DC', 'KEY_BACKSPACE', ' '}:
                del self.board[self.coordinate]
                self.refresh()
                self.board.check()
            else:
                try:
                    i = int(ch)
                    self.board[self.coordinate] = i
                    self.refresh()
                    self.board.check()
                except ValueError:
                    continue
                except InvalidValueError as ive:
                    for row, col in ive.fails:
                        if ive.fails[(row, col)]:
                            ch = str(self.board[(row, col)]) if (row, col) in self.board else " "
                            self.screen.addch(*self.cursor(row, col), ch, curses.color_pair(1))
            self.screen.move(*self.cursor())


if __name__ == '__main__':
    curses.wrapper(CursesBoard)
