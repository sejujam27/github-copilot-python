"""Sudoku puzzle generation utilities.

This module provides simple backtracking-based puzzle generation and helpers
used by the Flask application. Functions are intentionally small and focused so
they are easy to test and reuse.
"""

import copy
import random

SIZE = 9
EMPTY = 0


def copy_board(board):
    """Return a deep copy of ``board``.

    A small wrapper around ``copy.deepcopy`` that makes intent explicit in
    call sites.
    """
    return copy.deepcopy(board)


def create_empty_board():
    """Create and return an empty ``SIZE x SIZE`` Sudoku board.

    Empty cells are represented by the module constant ``EMPTY``.
    """
    return [[EMPTY for _ in range(SIZE)] for _ in range(SIZE)]


def is_valid_placement(board, row, col, num):
    """Return True if ``num`` may be placed at ``(row, col)``.

    The check enforces Sudoku constraints for the row, column and 3x3 box.
    """
    for x in range(SIZE):
        if board[row][x] == num or board[x][col] == num:
            return False
    start_row = row - row % 3
    start_col = col - col % 3
    for i in range(3):
        for j in range(3):
            if board[start_row + i][start_col + j] == num:
                return False
    return True


def fill_board_recursive(board):
    """Fill ``board`` in-place with a valid randomized Sudoku solution.

    The function builds a complete Sudoku grid from a standard pattern and
    applies random shuffles to rows, columns and digits to avoid repetitive
    layouts while keeping the result valid.
    """
    base_pattern = [
        [1, 2, 3, 4, 5, 6, 7, 8, 9],
        [4, 5, 6, 7, 8, 9, 1, 2, 3],
        [7, 8, 9, 1, 2, 3, 4, 5, 6],
        [2, 3, 4, 5, 6, 7, 8, 9, 1],
        [5, 6, 7, 8, 9, 1, 2, 3, 4],
        [8, 9, 1, 2, 3, 4, 5, 6, 7],
        [3, 4, 5, 6, 7, 8, 9, 1, 2],
        [6, 7, 8, 9, 1, 2, 3, 4, 5],
        [9, 1, 2, 3, 4, 5, 6, 7, 8],
    ]

    digit_map = list(range(1, SIZE + 1))
    random.shuffle(digit_map)
    shuffled_pattern = [
        [digit_map[value - 1] for value in row]
        for row in base_pattern
    ]

    row_groups = [list(range(0, 3)), list(range(3, 6)), list(range(6, 9))]
    random.shuffle(row_groups)
    rows = [row for group in row_groups for row in random.sample(group, len(group))]

    col_groups = [list(range(0, 3)), list(range(3, 6)), list(range(6, 9))]
    random.shuffle(col_groups)
    cols = [col for group in col_groups for col in random.sample(group, len(group))]

    for row in range(SIZE):
        for col in range(SIZE):
            board[row][col] = shuffled_pattern[rows[row]][cols[col]]
    return True


def remove_cells_from_board(board, clues):
    """Remove cells from ``board`` until ``clues`` remain.

    The function randomly clears cells while preserving the uniqueness of the
    resulting puzzle. A clue is only removed permanently if the board still
    has exactly one solution.
    """
    attempts = SIZE * SIZE - clues
    while attempts > 0:
        row = random.randrange(SIZE)
        col = random.randrange(SIZE)
        if board[row][col] != EMPTY:
            saved_value = board[row][col]
            board[row][col] = EMPTY
            if count_solutions(copy_board(board), limit=2) != 1:
                board[row][col] = saved_value
            else:
                attempts -= 1


def generate_sudoku_puzzle(clues=35):
    """Generate a Sudoku ``puzzle`` and its full ``solution``.

    Returns a tuple ``(puzzle, solution)``. ``puzzle`` contains empty cells
    represented by ``EMPTY`` while ``solution`` is a completed board.
    """
    board = create_empty_board()
    fill_board_recursive(board)
    solution = copy_board(board)
    remove_cells_from_board(board, clues)
    puzzle = copy_board(board)
    return puzzle, solution


def count_solutions(board, limit=2):
    """Count valid Sudoku solutions up to ``limit``.

    The function uses recursive backtracking to explore possible placements and
    stops once ``limit`` solutions have been found. It reuses
    ``is_valid_placement()`` and restores the board after each recursive step
    so the original board is not modified.
    """
    if limit <= 0:
        return 0

    def search(current_board, solutions_found):
        for row in range(SIZE):
            for col in range(SIZE):
                if current_board[row][col] == EMPTY:
                    for candidate in range(1, SIZE + 1):
                        if is_valid_placement(current_board, row, col, candidate):
                            current_board[row][col] = candidate
                            solutions_found = search(current_board, solutions_found)
                            current_board[row][col] = EMPTY
                            if solutions_found >= limit:
                                return solutions_found
                    return solutions_found
        return solutions_found + 1

    return search(copy_board(board), 0)


def solve_board_recursive(board):
    """Solve a partial Sudoku board in-place using backtracking."""
    for row in range(SIZE):
        for col in range(SIZE):
            if board[row][col] == EMPTY:
                for candidate in range(1, SIZE + 1):
                    if is_valid_placement(board, row, col, candidate):
                        board[row][col] = candidate
                        if solve_board_recursive(board):
                            return True
                        board[row][col] = EMPTY
                return False
    return True


def solve_sudoku(puzzle):
    """Return a solved board for the given partial ``puzzle`` or ``None``.

    Makes a deep copy of the provided puzzle and attempts to fill it using
    the backtracking solver. Returns the completed board on success or
    ``None`` if no solution is found.
    """
    board = copy_board(puzzle)
    if solve_board_recursive(board):
        return board
    return None
