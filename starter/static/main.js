// Client-side rendering and interaction for the Flask-backed Sudoku
const SIZE = 9;
let puzzle = [];
let solution = [];
let hintsUsed = 0;


function collectBoard() {
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  const board = [];

  for (let i = 0; i < SIZE; i++) {
    board[i] = [];
    for (let j = 0; j < SIZE; j++) {
      const idx = i * SIZE + j;
      const val = inputs[idx].value;
      board[i][j] = val ? parseInt(val, 10) : 0;
    }
  }

  return board;
}

function clearCellErrors() {
    document.querySelectorAll('.sudoku-cell').forEach(input => {
        input.classList.remove('incorrect');
    });
}

/*
GitHub Copilot suggested an approach for implementing live
Sudoku conflict highlighting.

After reviewing the suggestion, I adapted the implementation
to detect duplicate values in rows, columns, and 3x3 subgrids,
because the project requires immediate visual feedback for
invalid moves while the user is typing. This approach checks
the current board state instead of relying only on the solved puzzle.
*/

function getConflictingPositions(board) {

  const conflicts = new Set();

  function mark(row, col) {
    if (board[row][col] !== 0) {
      conflicts.add(`${row}-${col}`);
    }
  }

  // Row conflicts
  for (let row = 0; row < SIZE; row++) {

    const seen = new Map();

    for (let col = 0; col < SIZE; col++) {

      const value = board[row][col];

      if (value === 0) continue;

      if (seen.has(value)) {

        mark(row, seen.get(value));
        mark(row, col);

      } else {

        seen.set(value, col);

      }
    }
  }

  // Column conflicts
  for (let col = 0; col < SIZE; col++) {

    const seen = new Map();

    for (let row = 0; row < SIZE; row++) {

      const value = board[row][col];

      if (value === 0) continue;

      if (seen.has(value)) {

        mark(seen.get(value), col);
        mark(row, col);

      } else {

        seen.set(value, row);

      }
    }
  }

  // Box conflicts
  for (let boxRow = 0; boxRow < 3; boxRow++) {

    for (let boxCol = 0; boxCol < 3; boxCol++) {

      const seen = new Map();

      for (let r = 0; r < 3; r++) {

        for (let c = 0; c < 3; c++) {

          const row = boxRow * 3 + r;
          const col = boxCol * 3 + c;

          const value = board[row][col];

          if (value === 0) continue;

          if (seen.has(value)) {

            const [pr, pc] = seen.get(value);

            mark(pr, pc);
            mark(row, col);

          } else {

            seen.set(value, [row, col]);

          }

        }

      }

    }

  }

  return conflicts;
}

function applyRealtimeValidation() {

  const board = collectBoard();

  const conflicts = getConflictingPositions(board);

  clearCellErrors();

  conflicts.forEach(pos => {
    const [row, col] = pos.split('-').map(Number);

    const input = document.querySelector(
      `input[data-row="${row}"][data-col="${col}"]`
    );

    if (input) {
      input.classList.add('incorrect');
    }
  });
}


function createBoardElement() {
  const boardDiv = document.getElementById('sudoku-board');
  boardDiv.innerHTML = '';
  for (let i = 0; i < SIZE; i++) {
    const rowDiv = document.createElement('div');
    rowDiv.className = 'sudoku-row';
    for (let j = 0; j < SIZE; j++) {
      const input = document.createElement('input');
      input.type = 'text';
      input.maxLength = 1;
      input.className = 'sudoku-cell';
      input.dataset.row = i;
      input.dataset.col = j;
      // box index 0..8 used for 3x3 subgrid styling
      input.dataset.box = (Math.floor(i / 3) * 3 + Math.floor(j / 3)).toString();
      input.addEventListener('input', (e) => {

    const val = e.target.value.replace(/[^1-9]/g, '');

    e.target.value = val;

    applyRealtimeValidation();

});
      rowDiv.appendChild(input);
    }
    boardDiv.appendChild(rowDiv);
  }
}

function renderPuzzle(puz, sol) {
  puzzle = puz;
  solution = Array.isArray(sol) ? sol : [];
  createBoardElement();
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  for (let i = 0; i < SIZE; i++) {
    for (let j = 0; j < SIZE; j++) {
      const idx = i * SIZE + j;
      const val = puzzle[i][j];
      const inp = inputs[idx];
      if (val !== 0) {
        inp.value = val;
        inp.disabled = true;
        inp.classList.add('prefilled', 'locked');
      } else {
        inp.value = '';
        inp.disabled = false;
        inp.classList.remove('prefilled', 'locked', 'incorrect');
      }
    }
  }
}

let timerInterval = null;
let elapsedSeconds = 0;

function formatTime(seconds) {
  const mins = Math.floor(seconds / 60).toString().padStart(2, '0');
  const secs = (seconds % 60).toString().padStart(2, '0');
  return `${mins}:${secs}`;
}

function updateTimerDisplay() {
  const timer = document.getElementById('game-timer');
  if (timer) {
    timer.textContent = `Time: ${formatTime(elapsedSeconds)}`;
  }
}

function resetTimer() {
  elapsedSeconds = 0;
  updateTimerDisplay();
  if (timerInterval) {
    clearInterval(timerInterval);
  }
  timerInterval = setInterval(() => {
    elapsedSeconds += 1;
    updateTimerDisplay();
  }, 1000);
}

async function newGame() {
  const difficulty = document.getElementById('difficulty-select').value;
  const res = await fetch(`/new?difficulty=${encodeURIComponent(difficulty)}`);
  const data = await res.json();
  renderPuzzle(data.puzzle, data.solution);
  hintsUsed = 0;
  resetTimer();
  document.getElementById('message').innerText = '';
}

async function getHint() {
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  const board = collectBoard();

  const res = await fetch('/hint', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({board})
  });
  const data = await res.json();
  const msg = document.getElementById('message');

  if (data.error) {
    msg.style.color = '#d32f2f';
    msg.innerText = data.error;
    return;
  }

  const input = boardDiv.querySelector(`input[data-row="${data.row}"][data-col="${data.col}"]`);
  if (input) {
    input.value = data.value;
    applyRealtimeValidation();
    input.disabled = true;
    input.classList.add('locked');
    input.classList.add('hint-cell');
    input.classList.remove('incorrect');
    hintsUsed += 1;
  }

  msg.style.color = '#388e3c';
  msg.innerText = `Hint used (${hintsUsed})`;
}

async function checkSolution() {
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  const board = collectBoard();
  
  const res = await fetch('/check', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({board, puzzle})
  });
  const data = await res.json();
  const msg = document.getElementById('message');
  if (data.error) {
    msg.style.color = '#d32f2f';
    msg.innerText = data.error;
    return;
  }
  const incorrect = new Set(data.incorrect.map(x => x[0]*SIZE + x[1]));
  for (let idx = 0; idx < inputs.length; idx++) {
    const inp = inputs[idx];
    if (inp.disabled) continue;
    inp.classList.remove('incorrect');

if (incorrect.has(idx)) {

    inp.classList.add('incorrect');

}
  }
  if (incorrect.size === 0) {
    if (timerInterval) {
      clearInterval(timerInterval);
      timerInterval = null;
    }
    const difficulty = document.getElementById('difficulty-select').value;
    const playerName = (prompt("Enter your name:") || "").trim() || "Anonymous";
    addLeaderboardEntry(playerName, difficulty, elapsedSeconds, hintsUsed);
    msg.style.color = '#388e3c';
    msg.innerText = `Congratulations! You solved it in ${formatTime(elapsedSeconds)}.`;
  } else {
    msg.style.color = '#d32f2f';
    msg.innerText = 'Some cells are incorrect.';
  }
}

function toggleTheme() {
  const body = document.body;
  const button = document.getElementById('theme-toggle');
  const isDark = body.classList.toggle('dark');
  if (button) {
    button.textContent = isDark ? 'Light Mode' : 'Dark Mode';
    button.setAttribute('aria-pressed', isDark ? 'true' : 'false');
  }
}

function loadLeaderboard() {
  const stored = localStorage.getItem('sudokuLeaderboard');
  if (!stored) {
    return [];
  }

  try {
    const parsed = JSON.parse(stored);
    return Array.isArray(parsed)
      ? parsed.map(entry => ({
          playerName: entry.playerName || 'Anonymous',
          difficulty: entry.difficulty || 'Unknown',
          time: entry.time ?? 0,
          hints: entry.hints ?? 0,
          completedAt: entry.completedAt || Date.now()
        }))
      : [];
  } catch (error) {
    return [];
  }
}

function saveLeaderboard(entries) {
  localStorage.setItem('sudokuLeaderboard', JSON.stringify(entries));
}

function formatTimeLabel(seconds) {
  return formatTime(seconds);
}

function formatDateLabel(timestamp) {
  return new Date(timestamp).toLocaleString();
}

function renderLeaderboard() {
  const entries = loadLeaderboard();
  const tbody = document.querySelector('#leaderboard-table tbody');
  const empty = document.getElementById('leaderboard-empty');
  tbody.innerHTML = '';

  if (entries.length === 0) {
    empty.style.display = 'block';
    return;
  }

  empty.style.display = 'none';
  entries.forEach((entry, index) => {
    const row = document.createElement('tr');
    row.innerHTML = `
      <td>${index + 1}</td>
      <td>${entry.playerName || 'Anonymous'}</td>
      <td>${entry.difficulty}</td>
      <td>${formatTimeLabel(entry.time)}</td>
      <td>${entry.hints ?? 0}</td>
      <td>${formatDateLabel(entry.completedAt)}</td>
    `;
    tbody.appendChild(row);
  });
}

function addLeaderboardEntry(playerName, difficulty, timeSeconds, hintsUsed) {
  const entries = loadLeaderboard();
  const normalizedName = (playerName || 'Anonymous').trim();
  const duplicate = entries.some(entry =>
    entry.playerName === normalizedName &&
    entry.difficulty === difficulty &&
    entry.time === timeSeconds
  );

  if (duplicate) {
    return;
  }

  entries.push({
    playerName: normalizedName,
    difficulty,
    time: timeSeconds,
    hints: hintsUsed || 0,
    completedAt: Date.now()
  });
  entries.sort((a, b) => a.time - b.time);
  saveLeaderboard(entries.slice(0, 10));
  renderLeaderboard();
}

function clearLeaderboard() {
  localStorage.removeItem('sudokuLeaderboard');
  renderLeaderboard();
}

// Wire buttons
window.addEventListener('load', () => {
  document.getElementById('new-game').addEventListener('click', newGame);
  document.getElementById('hint-button').addEventListener('click', getHint);
  document.getElementById('check-solution').addEventListener('click', checkSolution);
  document.getElementById('clear-leaderboard').addEventListener('click', clearLeaderboard);
  const themeToggle = document.getElementById('theme-toggle');
  if (themeToggle) {
    themeToggle.addEventListener('click', toggleTheme);
    // initialize aria state based on current theme
    themeToggle.setAttribute('aria-pressed', document.body.classList.contains('dark') ? 'true' : 'false');
  }
  renderLeaderboard();
  // initialize
  newGame();
});