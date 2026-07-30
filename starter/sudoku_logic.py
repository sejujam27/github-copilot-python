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
    """Fill ``board`` in-place using backtracking and return True on success.

    The function attempts to place numbers in empty cells (`EMPTY`) and
    backtracks when no valid candidate is available.
    """
    for row in range(SIZE):
        for col in range(SIZE):
            if board[row][col] == EMPTY:
                possible = list(range(1, SIZE + 1))
                random.shuffle(possible)
                for candidate in possible:
                    if is_valid_placement(board, row, col, candidate):
                        board[row][col] = candidate
                        if fill_board_recursive(board):
                            return True
                        board[row][col] = EMPTY
                return False
    return True


def remove_cells_from_board(board, clues):
    """Remove cells from ``board`` until ``clues`` remain.

    The function randomly clears cells; it does not guarantee uniqueness of
    the resulting puzzle but is sufficient for demo purposes.
    """
    attempts = SIZE * SIZE - clues
    while attempts > 0:
        row = random.randrange(SIZE)
        col = random.randrange(SIZE)
        if board[row][col] != EMPTY:
            board[row][col] = EMPTY
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


def solve_sudoku(puzzle):
    """Return a solved board for the given partial ``puzzle`` or ``None``.

    Makes a deep copy of the provided puzzle and attempts to fill it using
    the backtracking solver. Returns the completed board on success or
    ``None`` if no solution is found.
    """
    board = copy_board(puzzle)
    if fill_board_recursive(board):
        return board
    return None
