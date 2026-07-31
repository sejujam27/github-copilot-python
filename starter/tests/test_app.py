import copy

import pytest
from app import app, GAME_STATE
from sudoku_logic import count_solutions, generate_sudoku_puzzle, remove_cells_from_board

@pytest.fixture(autouse=True)
def reset_game_state():
    GAME_STATE['puzzle'] = None
    GAME_STATE['solution'] = None

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_index_route(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'Sudoku' in response.data


def test_new_route(client):
    response = client.get('/new')
    assert response.status_code == 200
    data = response.get_json()
    assert 'puzzle' in data
    assert isinstance(data['puzzle'], list)


def test_new_route_with_difficulty(client):
    response = client.get('/new?difficulty=hard')
    assert response.status_code == 200
    data = response.get_json()
    assert 'puzzle' in data
    assert isinstance(data['puzzle'], list)


def test_new_route_invalid_difficulty(client):
    response = client.get('/new?difficulty=invalid')
    assert response.status_code == 400
    data = response.get_json()
    assert data['error'] == '`difficulty` must be one of Easy, Medium, or Hard'


def test_check_no_game(client):
    response = client.post('/check', json={'board': [[0]*9 for _ in range(9)]})
    assert response.status_code == 400
    data = response.get_json()
    assert data['error'] == 'No game in progress'


def test_count_solutions_returns_single_solution_without_mutating_board():
    board = [
        [5, 3, 4, 6, 7, 8, 9, 1, 2],
        [6, 7, 2, 1, 9, 5, 3, 4, 8],
        [1, 9, 8, 3, 4, 2, 5, 6, 7],
        [8, 5, 9, 7, 6, 1, 4, 2, 3],
        [4, 2, 6, 8, 5, 3, 7, 9, 1],
        [7, 1, 3, 9, 2, 4, 8, 5, 6],
        [9, 6, 1, 5, 3, 7, 2, 8, 4],
        [2, 8, 7, 4, 1, 9, 6, 3, 5],
        [3, 4, 5, 2, 8, 6, 1, 7, 9],
    ]
    board[0][0] = 0

    assert count_solutions(board, limit=2) == 1
    assert board[0][0] == 0


def test_remove_cells_from_board_preserves_unique_solution():
    board = [
        [5, 3, 4, 6, 7, 8, 9, 1, 2],
        [6, 7, 2, 1, 9, 5, 3, 4, 8],
        [1, 9, 8, 3, 4, 2, 5, 6, 7],
        [8, 5, 9, 7, 6, 1, 4, 2, 3],
        [4, 2, 6, 8, 5, 3, 7, 9, 1],
        [7, 1, 3, 9, 2, 4, 8, 5, 6],
        [9, 6, 1, 5, 3, 7, 2, 8, 4],
        [2, 8, 7, 4, 1, 9, 6, 3, 5],
        [3, 4, 5, 2, 8, 6, 1, 7, 9],
    ]

    remove_cells_from_board(board, clues=80)

    assert count_solutions(board, limit=2) == 1


def test_hint_returns_first_empty_cell_value(client):
    puzzle = [
        [5, 3, 0, 6, 7, 8, 9, 1, 2],
        [6, 7, 2, 1, 9, 5, 3, 4, 8],
        [1, 9, 8, 3, 4, 2, 5, 6, 7],
        [8, 5, 9, 7, 6, 1, 4, 2, 3],
        [4, 2, 6, 8, 5, 3, 7, 9, 1],
        [7, 1, 3, 9, 2, 4, 8, 5, 6],
        [9, 6, 1, 5, 3, 7, 2, 8, 4],
        [2, 8, 7, 4, 1, 9, 6, 3, 5],
        [3, 4, 5, 2, 8, 6, 1, 7, 9],
    ]
    solution = [
        [5, 3, 4, 6, 7, 8, 9, 1, 2],
        [6, 7, 2, 1, 9, 5, 3, 4, 8],
        [1, 9, 8, 3, 4, 2, 5, 6, 7],
        [8, 5, 9, 7, 6, 1, 4, 2, 3],
        [4, 2, 6, 8, 5, 3, 7, 9, 1],
        [7, 1, 3, 9, 2, 4, 8, 5, 6],
        [9, 6, 1, 5, 3, 7, 2, 8, 4],
        [2, 8, 7, 4, 1, 9, 6, 3, 5],
        [3, 4, 5, 2, 8, 6, 1, 7, 9],
    ]
    GAME_STATE['puzzle'] = puzzle
    GAME_STATE['solution'] = solution

    response = client.post('/hint', json={'board': puzzle})

    assert response.status_code == 200
    assert response.get_json() == {'row': 0, 'col': 2, 'value': 4}


def test_hint_requires_active_game(client):
    response = client.post('/hint', json={'board': [[0] * 9 for _ in range(9)]})

    assert response.status_code == 400
    assert response.get_json() == {'error': 'No game in progress'}


def test_hint_requires_empty_cells(client):
    GAME_STATE['puzzle'] = [[1] * 9 for _ in range(9)]
    GAME_STATE['solution'] = [[1] * 9 for _ in range(9)]

    response = client.post('/hint', json={'board': [[1] * 9 for _ in range(9)]})

    assert response.status_code == 400
    assert response.get_json() == {'error': 'No empty cells remain'}


def test_hint_fills_one_empty_cell_without_overwriting_locked_clues(client):
    puzzle = [
        [5, 3, 0, 6, 7, 8, 9, 1, 2],
        [6, 7, 2, 1, 9, 5, 3, 4, 8],
        [1, 9, 8, 3, 4, 2, 5, 6, 7],
        [8, 5, 9, 7, 6, 1, 4, 2, 3],
        [4, 2, 6, 8, 5, 3, 7, 9, 1],
        [7, 1, 3, 9, 2, 4, 8, 5, 6],
        [9, 6, 1, 5, 3, 7, 2, 8, 4],
        [2, 8, 7, 4, 1, 9, 6, 3, 5],
        [3, 4, 5, 2, 8, 6, 1, 7, 9],
    ]
    solution = [
        [5, 3, 4, 6, 7, 8, 9, 1, 2],
        [6, 7, 2, 1, 9, 5, 3, 4, 8],
        [1, 9, 8, 3, 4, 2, 5, 6, 7],
        [8, 5, 9, 7, 6, 1, 4, 2, 3],
        [4, 2, 6, 8, 5, 3, 7, 9, 1],
        [7, 1, 3, 9, 2, 4, 8, 5, 6],
        [9, 6, 1, 5, 3, 7, 2, 8, 4],
        [2, 8, 7, 4, 1, 9, 6, 3, 5],
        [3, 4, 5, 2, 8, 6, 1, 7, 9],
    ]
    GAME_STATE['puzzle'] = puzzle
    GAME_STATE['solution'] = solution

    response = client.post('/hint', json={'board': puzzle})
    data = response.get_json()

    applied_board = copy.deepcopy(puzzle)
    applied_board[data['row']][data['col']] = data['value']

    assert response.status_code == 200
    assert data['row'] == 0
    assert data['col'] == 2
    assert data['value'] == 4
    assert applied_board[0][0] == puzzle[0][0]
    assert applied_board[0][2] == 4
    assert sum(cell == 0 for row in applied_board for cell in row) == 0


def test_hint_counter_increments_for_each_successful_hint(client):
    puzzle = [
        [5, 3, 0, 6, 7, 0, 9, 1, 2],
        [6, 7, 2, 1, 9, 5, 3, 4, 8],
        [1, 9, 8, 3, 4, 2, 5, 6, 7],
        [8, 5, 9, 7, 6, 1, 4, 2, 3],
        [4, 2, 6, 8, 5, 3, 7, 9, 1],
        [7, 1, 3, 9, 2, 4, 8, 5, 6],
        [9, 6, 1, 5, 3, 7, 2, 8, 4],
        [2, 8, 7, 4, 1, 9, 6, 3, 5],
        [3, 4, 5, 2, 8, 6, 1, 7, 9],
    ]
    solution = [
        [5, 3, 4, 6, 7, 8, 9, 1, 2],
        [6, 7, 2, 1, 9, 5, 3, 4, 8],
        [1, 9, 8, 3, 4, 2, 5, 6, 7],
        [8, 5, 9, 7, 6, 1, 4, 2, 3],
        [4, 2, 6, 8, 5, 3, 7, 9, 1],
        [7, 1, 3, 9, 2, 4, 8, 5, 6],
        [9, 6, 1, 5, 3, 7, 2, 8, 4],
        [2, 8, 7, 4, 1, 9, 6, 3, 5],
        [3, 4, 5, 2, 8, 6, 1, 7, 9],
    ]
    GAME_STATE['puzzle'] = puzzle
    GAME_STATE['solution'] = solution

    hints_used = 0
    applied_board = copy.deepcopy(puzzle)
    seen_positions = set()
    for _ in range(2):
        response = client.post('/hint', json={'board': applied_board})
        assert response.status_code == 200
        data = response.get_json()
        assert applied_board[data['row']][data['col']] == 0
        applied_board[data['row']][data['col']] = data['value']
        seen_positions.add((data['row'], data['col']))
        hints_used += 1

    assert hints_used == 2
    assert len(seen_positions) == 2
    assert sum(cell == 0 for row in applied_board for cell in row) == 0


@pytest.mark.parametrize(
    ("difficulty", "clues"),
    [("Easy", 45), ("Medium", 35), ("Hard", 25)],
)
def test_generated_puzzles_have_expected_clue_count_and_unique_solution(difficulty, clues):
    puzzle, _ = generate_sudoku_puzzle(clues=clues)

    clue_count = sum(cell != 0 for row in puzzle for cell in row)

    assert clue_count == clues
    assert count_solutions(puzzle, limit=2) == 1
