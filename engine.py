from __future__ import unicode_literals

import copy
from random import sample


class Board(object):
    def __init__(self, initial=None, *args, **kwargs):
        super(Board, self).__init__(*args, **kwargs)
        self.initial = initial if initial else self._make_empty_board()
        self.board = (
            copy.deepcopy(self.initial) if self.initial
            else self._make_empty_board()
        )

    def __getitem__(self, key):
        return self.board[key]

    def __unicode__(self):
        # print column headers
        board = "\n   #| {}\n".format(
            " ".join(unicode(column) for column in range(1, 10))
        )
        # print divider
        board += "{}\n".format("-" * len(board))
        for row_count, row in enumerate(self.board, 1):
            # print rows
            board += "   {}| {}\n".format(
                row_count,
                " ".join(unicode(column or '-') for column in row),
            )
        return board

    __str__ = __unicode__
    __repr__ = __unicode__

    def _make_empty_board(self):
        return [[None for empty in range(9)] for row in range(9)]


class UnableToInsert(Exception):
    pass


def pattern(row, column):
    return (3 * (row % 3) + row // 3 + column) % 9


def shuffle(sequence):
    return sample(sequence, len(sequence))


class SudokuEngine(object):
    EASY = 1
    MEDIUM = 2
    HARD = 3

    DIFFICULTY = {
        EASY: 36,  # number of hints
        MEDIUM: 30,
        HARD: 25,
    }

    def __init__(self, initial_board=None):
        self.board = initial_board if initial_board else Board()

    def __unicode__(self):
        return unicode(self.board)

    __str__ = __unicode__

    def can_insert(self, column, row, value):
        for _row in range(9):
            # check in column
            if self.board[_row][column] == value:
                return False
        for _column in range(9):
            # check in row
            if self.board[row][_column] == value:
                return False
        # check in box
        row0 = (row // 3) * 3
        column0 = (column // 3) * 3
        for _column in range(3):
            for _row in range(3):
                if self.board[row0 + _row][column0 + _column] == value:
                    return False
        return True

    def insert(self, column, row, value):
        if not self.can_insert(column=column, row=row, value=value):
            raise UnableToInsert(
                "Can't insert value into column={}, row={}, value={}".format(
                    column, row, value
                )
            )
        self.board[row][column] = value

    def get(self, column, row):
        return self.board[row][column]

    def clear(self, column, row):
        if self.board.initial[row][column]:
            return
        self.board[row][column] = None

    @classmethod
    def generate(cls, difficulty):
        # shuffle the rows and columns but we always want to randomize
        # rows and columns around this base
        base = [0, 1, 2]
        rows = [g * 3 + row for g in shuffle(base) for row in shuffle(base)]
        columns = [
            g * 3 + column for g in shuffle(base) for column in shuffle(base)
        ]
        randomized_values = shuffle(range(1, 10))

        # when we have randomized columns and rows with values, we want to
        # randomize the whole board by pattern so it won't be broken
        board = [
            [randomized_values[pattern(row, column)] for column in columns]
            for row in rows
        ]

        make_empty = 81 - cls.DIFFICULTY[difficulty]
        # clean random cells, basically we are making it into matrix where
        # cell_index // 9 is row and cell_index % 9 gives column
        for cell_index in sample(range(81), make_empty):
            board[cell_index // 9][cell_index % 9] = 0

        engine = cls(initial_board=Board(initial=board))
        return engine

    def is_solved(self):
        """Check for values inside the row for all rows if they exist it means
        that it is done.
        """
        return all(all(row) for row in self.board)


class BacktrackingSolver(object):
    def __init__(self, sudoku_engine):
        self.sudoku_engine = sudoku_engine
        self.possible_solutions = []

    def solve(self):
        """Use simple backtracking to solve the sudoku brute force way."""
        for column in range(9):
            for row in range(9):
                if self.sudoku_engine.get(column=column, row=row) in [None, 0]:
                    for value in range(1, 10):
                        if self.sudoku_engine.can_insert(
                            column=column, row=row, value=value
                        ):
                            self.sudoku_engine.board[row][column] = value
                            self.solve()
                            self.sudoku_engine.board[row][column] = None
                    return
        self.possible_solutions.append(copy.deepcopy(self.sudoku_engine.board))
