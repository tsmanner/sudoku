import numpy
import time


class Board(dict):
    class Row:
        def __init__(self, board, row, start=0, stop=None):
            self.board = board
            self.row = row
            self.start = 0 if stop is None else start
            self.stop = board.unit ** 2 if stop is None else stop

        def __getitem__(self, item):
            return self.board[(self.row, item)]

        def __setitem__(self, col, value):
            self.board[(self.row, col)] = value

        def __delitem__(self, col):
            del self.board[(self.row, col)]

        def __iter__(self):
            for col in range(self.start, self.stop):
                yield self[col]

    class Column:
        def __init__(self, board, col, start=0, stop=None):
            self.board = board
            self.col = col
            self.start = 0 if stop is None else start
            self.stop = board.unit ** 2 if stop is None else stop

        def __getitem__(self, item):
            return self.board[(item, self.col)]

        def __setitem__(self, row, value):
            self.board[(row, self.col)] = value

        def __delitem__(self, row):
            del self.board[(row, self.col)]

        def __iter__(self):
            for row in range(self.start, self.stop):
                yield self[row]

    def __init__(self, unit: int):
        super().__init__()
        self.unit = unit
        self.numbers = {x+1 for x in range(self.unit**2)}

    def __getitem__(self, item):
        if isinstance(item, int):
            return self.Row(self, item)
        return super().__getitem__(item) if item in self else None

    def insert(self, *rows):
        for r, row in enumerate(rows):
            for c, col in enumerate(row):
                self[r][c] = col

    @property
    def rows(self):
        return self.unit ** 2

    @property
    def cols(self):
        return self.unit ** 2

    def row(self, row):
        return self.Row(self, row)

    def col(self, col):
        return self.Column(self, col)

    def block(self, block_number):
        startrow = (block_number // self.unit) * self.unit
        startcol = (block_number  % self.unit) * self.unit
        for row in range(startrow, startrow+self.unit):
            for col in range(startcol, startcol+self.unit):
                yield self[row][col]

    def check(self):
        for i in range(self.unit ** 2):
            # Check Row
            if set(self.row(i)) != self.numbers:
                raise ValueError("Invalid Row {} Values {}!".format(i, list(self.row(i))))
            # Check Column
            if set(self.col(i)) != self.numbers:
                raise ValueError("Invalid Row {} Values {}!".format(i, list(self.col(i))))
            # Check Block
            if set(self.block(i)) != self.numbers:
                raise ValueError("Invalid Block {} Values {}!".format(i, list(self.block(i))))

    def __repr__(self):
        lines = []
        divider = ('+-' + '--' * self.unit) * self.unit + '+'
        for row in range(self.rows):
            if row % self.unit == 0:
                lines.append(divider)
            line = ''
            for col in range(self.cols):
                if col % self.unit == 0:
                    line += '| '
                value = self[row][col]
                line += '{} '.format(value) if value else '  '
            line += '|'
            lines.append(line)
        lines.append(divider)
        return '\n'.join(lines)


def generate_board(unit=3, max_attempts=1000):
    t0 = time.time()
    max_row = 0
    for i in range(1, 1 + max_attempts):
        board = Board(unit)
        count = board.unit ** 2
        try:
            for row in range(count):
                for col in range(count):
                    block = (row // board.unit) * board.unit + (col // board.unit)
                    available = list(board.numbers - (set(board.row(row)) | set(board.col(col)) | set(board.block(block)) ))
                    board[row][col] = numpy.random.choice(available)
            # print()
            # print("Success after {} attempts.".format(i))
            return board
        except ValueError:
            max_row = row if row > max_row else max_row
    #         print("Max Row {:>2}".format(max_row), end='\r')
    # print()
    return None


if __name__ == "__main__":
    board = generate_board(3)
    if board:
        number_to_delete = int(0.6 * (board.unit ** 4))
        for i in range(number_to_delete):
            keys = list(board.keys())
            del board[keys[numpy.random.choice(len(keys))]]
    print(board)
