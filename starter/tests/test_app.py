import pytest
from app import app, GAME_STATE

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
