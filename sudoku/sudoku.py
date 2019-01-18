from collections import defaultdict
import numpy
from typing import Union


class InvalidValueError(BaseException):
    def __init__(self, message, fails):
        super().__init__(message)
        self.fails = fails


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

    def __init__(self, arg: "Union[Board, int]"):
        super().__init__()
        if isinstance(arg, Board):
            self.unit = arg.unit
            for k, v in arg.items():
                self[k] = v
        else:
            self.unit = arg
        self.rows = self.unit ** 2
        self.cols = self.rows
        self.numbers = {x+1 for x in range(self.unit ** 2)}

    def __getitem__(self, item):
        if isinstance(item, int):
            return self.Row(self, item)
        return super().__getitem__(item) if item in self else None

    def __setitem__(self, key, value):
        if not (isinstance(key, tuple) and len(key) == 2):
            raise ValueError(
                "{} keys must be Tuple[int, int], not {}".format(
                    type(self).__name__,
                    type(key).__name__
                )
            )
        if not isinstance(value, (int, numpy.int64)):
            raise ValueError(
                "{} values must be int, not {}".format(
                    type(self).__name__,
                    type(value).__name__
                )
            )
        super().__setitem__(key, value)

    def values(self):
        for row in range(self.rows):
            for value in self.row(row):
                yield value

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

    def block_number(self, row, col):
        return (row // self.unit) * self.unit + (col // self.unit)

    def check(self):
        fails = defaultdict(lambda: False)
        for row in range(self.rows):
            for col in range(self.cols):
                if (row, col) in self:
                    check_value = self[(row, col)]
                    values = set()
                    for value in self.row(row):
                        if value in values and value == check_value:
                            fails[(row, col)] = True
                        else:
                            values.add(value)

                    values = set()
                    for value in self.col(col):
                        if value in values and value == check_value:
                            fails[(row, col)] = True
                        else:
                            values.add(value)

                    values = set()
                    for value in self.block(self.block_number(row, col)):
                        if value in values and value == check_value:
                            fails[(row, col)] = True
                        else:
                            values.add(value)

        if len(fails):
            raise InvalidValueError("Invalid Solution".format(), fails)

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


def generate_board(unit=3, max_attempts=10000):
    max_row = row = i = 0
    for i in range(1, 1 + max_attempts):
        board = Board(unit)
        try:
            for row in range(board.rows):
                for col in range(board.cols):
                    available = list(
                        board.numbers - (
                                set(board.row(row)) |
                                set(board.col(col)) |
                                set(board.block(board.block_number(row, col)))
                        )
                    )
                    board[row][col] = numpy.random.choice(available)
            # print("\rMax Row {:>2} after {} attempts".format(max_row, i))
            return board
        except ValueError:
            max_row = row if row > max_row else max_row
            # print("\rMax Row {:>2} after {} attempts".format(max_row, i), end='')
    # print("\rMax Row {:>2} after {} attempts".format(max_row, i))
    return None


def cull_board(board, cull_value):
    board_copy = Board(board)
    if isinstance(cull_value, float):
        number_to_delete = int(cull_value * (board_copy.unit ** 4))
    elif isinstance(cull_value, int):
        number_to_delete = cull_value
    else:
        raise ValueError(
            "cull_value must be of type int or float, not {}".format(type(cull_value).__name__)
        )
    if number_to_delete > len(board_copy):
        number_to_delete = len(board_copy)
    for i in range(number_to_delete):
        keys = list(board_copy.keys())
        key = keys[numpy.random.choice(len(keys))]
        del board_copy[key]
    return board_copy


if __name__ == "__main__":
    board = generate_board(3, 10000)
    if board:
        print(board)
        print(cull_board(board, 0.6))
    else:
        print("Failed to generate")
