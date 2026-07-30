"""Flask Sudoku web application.

Provides routes to render the user interface, generate Sudoku puzzles,
and check submitted solutions. The module keeps a small in-memory game
state while the server is running.
"""

from flask import Flask, render_template, jsonify, request
import sudoku_logic

app = Flask(__name__)

# In-memory store for the current puzzle and its solution.
GAME_STATE = {
    'puzzle': None,
    'solution': None
}


def set_game_state(puzzle, solution):
    """Store the current puzzle and its solution.

    Centralizes updates to the module-level ``GAME_STATE`` dictionary so
    route handlers and tests use a single accessor.
    """
    GAME_STATE['puzzle'] = puzzle
    GAME_STATE['solution'] = solution


def get_current_solution():
    """Return the current solution or ``None`` if no game is active.

    Using a helper keeps call sites simple and makes future storage
    adjustments straightforward.
    """
    return GAME_STATE.get('solution')


def error_response(message, status=400):
    """Return a standardized JSON error response.

    Returns a Flask response tuple ``(body, status)`` where ``body`` is a
    JSON object containing an ``error`` key with a human-friendly message.
    """
    return jsonify({'error': message}), status


def parse_difficulty_from_request(req):
    """Parse and validate the ``difficulty`` query parameter.

    Returns the corresponding number of clues for the requested difficulty.
    Raises ``ValueError`` for unsupported difficulty values.
    """
    raw = req.args.get('difficulty', None)
    if raw is None:
        return None

    mapping = {
        'easy': 45,
        'medium': 35,
        'hard': 25
    }
    difficulty = raw.strip().lower()
    if difficulty not in mapping:
        raise ValueError('`difficulty` must be one of Easy, Medium, or Hard')
    return mapping[difficulty]


def parse_clues_from_request(req):
    """Parse and validate the ``clues`` query parameter.

    Returns the requested number of clues as an ``int``. If the parameter is
    missing the default value ``35`` is returned. Raises ``ValueError`` when
    the provided value cannot be interpreted as an integer or is out of range.
    """
    raw = req.args.get('clues', None)
    if raw is None:
        return 35
    try:
        clues = int(raw)
    except (TypeError, ValueError):
        raise ValueError('`clues` must be an integer')
    max_clues = sudoku_logic.SIZE * sudoku_logic.SIZE
    if not (1 <= clues <= max_clues):
        raise ValueError(f'`clues` must be between 1 and {max_clues}')
    return clues


def validate_board(board):
    """Validate that ``board`` is a ``SIZE x SIZE`` list of integers.

    Raises ``ValueError`` when the board is invalid so callers can return a
    user-friendly error message to clients.
    """
    if not isinstance(board, list) or len(board) != sudoku_logic.SIZE:
        raise ValueError(f'`board` must be a {sudoku_logic.SIZE}x{sudoku_logic.SIZE} list')
    for i, row in enumerate(board):
        if not isinstance(row, list) or len(row) != sudoku_logic.SIZE:
            raise ValueError(f'Row {i} must be a list of length {sudoku_logic.SIZE}')
        for j, cell in enumerate(row):
            if not isinstance(cell, int) or not (0 <= cell <= sudoku_logic.SIZE):
                raise ValueError(f'Cell ({i},{j}) must be integer between 0 and {sudoku_logic.SIZE}')


@app.route('/')
def index():
    """Render the main Sudoku UI page."""
    return render_template('index.html')


@app.route('/new')
def new_game():
    """Generate a new Sudoku puzzle and return it as JSON.

    Accepts optional ``difficulty`` or ``clues`` query parameters. ``clues`` takes
    precedence when both are provided.
    """
    try:
        clues = parse_clues_from_request(request) if request.args.get('clues') is not None else None
        if clues is None:
            clues = parse_difficulty_from_request(request) or 35
    except ValueError as e:
        return error_response(str(e), 400)

    puzzle, solution = sudoku_logic.generate_sudoku_puzzle(clues)
    set_game_state(puzzle, solution)
    return jsonify({'puzzle': puzzle})


@app.route('/check', methods=['POST'])
def check_solution():
    """Check a posted ``board`` against the current solution and return
    a list of incorrect cell coordinates.
    """
    data = request.get_json(silent=True)
    if data is None:
        return error_response('Invalid or missing JSON body', 400)

    board = data.get('board')
    if board is None:
        return error_response('Missing `board` in request body', 400)

    try:
        validate_board(board)
    except ValueError as e:
        return error_response(str(e), 400)

    solution = get_current_solution()
    if solution is None:
        return error_response('No game in progress', 400)
    incorrect = []
    for i in range(sudoku_logic.SIZE):
        for j in range(sudoku_logic.SIZE):
            if board[i][j] != solution[i][j]:
                incorrect.append([i, j])
    return jsonify({'incorrect': incorrect})


if __name__ == '__main__':
    app.run(debug=True)
