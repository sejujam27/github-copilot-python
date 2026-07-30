// Client-side rendering and interaction for the Flask-backed Sudoku
const SIZE = 9;
let puzzle = [];

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
      });
      rowDiv.appendChild(input);
    }
    boardDiv.appendChild(rowDiv);
  }
}

function renderPuzzle(puz) {
  puzzle = puz;
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
  renderPuzzle(data.puzzle);
  resetTimer();
  document.getElementById('message').innerText = '';
}

async function checkSolution() {
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
    inp.className = 'sudoku-cell';
    if (incorrect.has(idx)) {
      inp.className = 'sudoku-cell incorrect';
    }
  }
  if (incorrect.size === 0) {
    if (timerInterval) {
      clearInterval(timerInterval);
      timerInterval = null;
    }
    const difficulty = document.getElementById('difficulty-select').value;
    addLeaderboardEntry(difficulty, elapsedSeconds);
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
  return stored ? JSON.parse(stored) : [];
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
      <td>${entry.difficulty}</td>
      <td>${formatTimeLabel(entry.time)}</td>
      <td>${formatDateLabel(entry.completedAt)}</td>
    `;
    tbody.appendChild(row);
  });
}

function addLeaderboardEntry(difficulty, timeSeconds) {
  const entries = loadLeaderboard();
  entries.push({
    difficulty,
    time: timeSeconds,
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