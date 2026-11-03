# Game Templates

## Template 1: Match-3 (Cat Tea Party)

**Input**: "Cat afternoon tea match-3 game, casual match-3, protagonist is cat, 10 levels, add cat paw power-up, Q-version cartoon style"

**Output**:
```html
<!-- Cat Tea Party Match-3 Game -->

<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>猫的下午茶 - 三消游戏</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      font-family: 'Comic Sans MS', cursive;
      background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      align-items: center;
      padding: 20px;
    }
    .game-header {
      background: white;
      padding: 15px 30px;
      border-radius: 20px;
      box-shadow: 0 4px 15px rgba(0,0,0,0.1);
      margin-bottom: 20px;
      display: flex;
      gap: 30px;
      align-items: center;
    }
    .score-display {
      font-size: 24px;
      color: #e74c3c;
      font-weight: bold;
    }
    .level-display {
      font-size: 20px;
      color: #3498db;
    }
    .power-up-btn {
      background: linear-gradient(45deg, #ff6b6b, #ee5a24);
      color: white;
      border: none;
      padding: 10px 20px;
      border-radius: 25px;
      cursor: pointer;
      font-size: 16px;
      transition: transform 0.2s;
    }
    .power-up-btn:hover {
      transform: scale(1.1);
    }
    .game-board {
      background: white;
      padding: 15px;
      border-radius: 20px;
      box-shadow: 0 8px 30px rgba(0,0,0,0.15);
    }
    .grid {
      display: grid;
      grid-template-columns: repeat(8, 50px);
      gap: 5px;
    }
    .cell {
      width: 50px;
      height: 50px;
      border-radius: 10px;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 30px;
      transition: all 0.2s;
      box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    .cell:hover {
      transform: scale(1.1);
    }
    .cell.selected {
      outline: 3px solid #ff6b6b;
      transform: scale(1.1);
    }
    .cell.matched {
      animation: match 0.3s ease;
    }
    @keyframes match {
      0% { transform: scale(1); }
      50% { transform: scale(1.3); }
      100% { transform: scale(0); }
    }
    /* Item colors */
    .cake { background: #ff9ff3; }
    .cookie { background: #feca57; }
    .tea { background: #48dbfb; }
    .milk { background: #fff; border: 2px solid #ddd; }
    .coffee { background: #6c5ce7; }

    .game-over, .level-complete {
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background: rgba(0,0,0,0.7);
      display: flex;
      align-items: center;
      justify-content: center;
      z-index: 100;
    }
    .modal {
      background: white;
      padding: 40px;
      border-radius: 20px;
      text-align: center;
    }
    .modal h2 {
      font-size: 32px;
      margin-bottom: 20px;
      color: #333;
    }
    .modal button {
      background: linear-gradient(45deg, #ff6b6b, #ee5a24);
      color: white;
      border: none;
      padding: 15px 40px;
      border-radius: 30px;
      font-size: 18px;
      cursor: pointer;
      margin: 10px;
    }
  </style>
</head>
<body>
  <div class="game-header">
    <div class="level-display">关卡: <span id="level">1</span>/10</div>
    <div class="score-display">得分: <span id="score">0</span></div>
    <button class="power-up-btn" onclick="usePowerUp()">
      🐾 猫爪 (1)
    </button>
  </div>

  <div class="game-board">
    <div class="grid" id="grid"></div>
  </div>

  <script>
    // Game Configuration
    const ITEMS = ['cake', 'cookie', 'tea', 'milk', 'coffee'];
    const GRID_SIZE = 8;
    const LEVELS = 10;

    let grid = [];
    let selectedCell = null;
    let score = 0;
    let level = 1;
    let powerUps = 1;
    let isAnimating = false;

    // Initialize Game
    function initGame() {
      grid = [];
      for (let i = 0; i < GRID_SIZE; i++) {
        grid[i] = [];
        for (let j = 0; j < GRID_SIZE; j++) {
          grid[i][j] = getRandomItem();
        }
      }
      renderGrid();
    }

    // Get random item
    function getRandomItem() {
      return ITEMS[Math.floor(Math.random() * ITEMS.length)];
    }

    // Render grid
    function renderGrid() {
      const gridElement = document.getElementById('grid');
      gridElement.innerHTML = '';
      for (let i = 0; i < GRID_SIZE; i++) {
        for (let j = 0; j < GRID_SIZE; j++) {
          const cell = document.createElement('div');
          cell.className = `cell ${grid[i][j]}`;
          cell.dataset.row = i;
          cell.dataset.col = j;
          cell.innerHTML = getItemEmoji(grid[i][j]);
          cell.onclick = () => handleCellClick(i, j);
          gridElement.appendChild(cell);
        }
      }
    }

    // Get emoji for item
    function getItemEmoji(item) {
      const emojis = {
        cake: '🎂',
        cookie: '🍪',
        tea: '🧋',
        milk: '🥛',
        coffee: '☕'
      };
      return emojis[item] || '';
    }

    // Handle cell click
    function handleCellClick(row, col) {
      if (isAnimating) return;

      const cellIndex = row * GRID_SIZE + col;
      const cells = document.querySelectorAll('.cell');
      const clickedCell = cells[cellIndex];

      if (selectedCell === null) {
        selectedCell = { row, col };
        clickedCell.classList.add('selected');
      } else {
        const prevIndex = selectedCell.row * GRID_SIZE + selectedCell.col;
        cells[prevIndex].classList.remove('selected');

        // Check if adjacent
        if (isAdjacent(selectedCell.row, selectedCell.col, row, col)) {
          swapCells(selectedCell.row, selectedCell.col, row, col);
        }
        selectedCell = null;
      }
    }

    // Check if cells are adjacent
    function isAdjacent(row1, col1, row2, col2) {
      return (Math.abs(row1 - row2) === 1 && col1 === col2) ||
             (Math.abs(col1 - col2) === 1 && row1 === row2);
    }

    // Swap cells
    async function swapCells(row1, col1, row2, col2) {
      isAnimating = true;

      // Swap in grid
      [grid[row1][col1], grid[row2][col2]] = [grid[row2][col2], grid[row1][col1]];

      // Check for matches
      const matches = findMatches();
      if (matches.length > 0) {
        renderGrid();
        await processMatches(matches);
      } else {
        // Swap back
        [grid[row1][col1], grid[row2][col2]] = [grid[row2][col2], grid[row1][col1]];
        renderGrid();
      }

      isAnimating = false;
    }

    // Find all matches
    function findMatches() {
      const matches = [];

      // Check horizontal
      for (let i = 0; i < GRID_SIZE; i++) {
        for (let j = 0; j < GRID_SIZE - 2; j++) {
          if (grid[i][j] === grid[i][j+1] && grid[i][j] === grid[i][j+2]) {
            matches.push({ row: i, col: j }, { row: i, col: j+1 }, { row: i, col: j+2 });
          }
        }
      }

      // Check vertical
      for (let i = 0; i < GRID_SIZE - 2; i++) {
        for (let j = 0; j < GRID_SIZE; j++) {
          if (grid[i][j] === grid[i+1][j] && grid[i][j] === grid[i+2][j]) {
            matches.push({ row: i, col: j }, { row: i+1, col: j }, { row: i+2, col: j });
          }
        }
      }

      return matches;
    }

    // Process matches
    async function processMatches(matches) {
      // Remove duplicates
      const uniqueMatches = [];
      matches.forEach(m => {
        if (!uniqueMatches.find(u => u.row === m.row && u.col === m.col)) {
          uniqueMatches.push(m);
        }
      });

      // Animate and remove
      const cells = document.querySelectorAll('.cell');
      uniqueMatches.forEach(m => {
        const cellIndex = m.row * GRID_SIZE + m.col;
        cells[cellIndex].classList.add('matched');
      });

      // Update score
      score += uniqueMatches.length * 10;
      document.getElementById('score').textContent = score;

      // Play sound effect
      playSound('match');

      await sleep(300);

      // Clear matched cells
      uniqueMatches.forEach(m => {
        grid[m.row][m.col] = null;
      });

      // Drop cells
      dropCells();
      renderGrid();

      // Check for more matches
      const newMatches = findMatches();
      if (newMatches.length > 0) {
        await sleep(200);
        await processMatches(newMatches);
      }
    }

    // Drop cells to fill gaps
    function dropCells() {
      for (let col = 0; col < GRID_SIZE; col++) {
        let emptyRow = GRID_SIZE - 1;
        for (let row = GRID_SIZE - 1; row >= 0; row--) {
          if (grid[row][col] !== null) {
            grid[emptyRow][col] = grid[row][col];
            if (emptyRow !== row) {
              grid[row][col] = null;
            }
            emptyRow--;
          }
        }
        // Fill empty top rows
        for (let row = emptyRow; row >= 0; row--) {
          grid[row][col] = getRandomItem();
        }
      }
    }

    // Use power-up (cat paw)
    function usePowerUp() {
      if (powerUps <= 0 || isAnimating) return;

      powerUps--;
      document.querySelector('.power-up-btn').textContent = `🐾 猫爪 (${powerUps})`;

      // Find center of any match or random
      const centerRow = Math.floor(GRID_SIZE / 2);
      const centerCol = Math.floor(GRID_SIZE / 2);

      // Clear 3x3 area
      const toRemove = [];
      for (let i = -1; i <= 1; i++) {
        for (let j = -1; j <= 1; j++) {
          const r = centerRow + i;
          const c = centerCol + j;
          if (r >= 0 && r < GRID_SIZE && c >= 0 && c < GRID_SIZE) {
            toRemove.push({ row: r, col: c });
          }
        }
      }

      // Remove with animation
      const cells = document.querySelectorAll('.cell');
      toRemove.forEach(m => {
        const cellIndex = m.row * GRID_SIZE + m.col;
        cells[cellIndex].classList.add('matched');
      });

      score += toRemove.length * 20;
      document.getElementById('score').textContent = score;
      playSound('powerup');

      setTimeout(() => {
        toRemove.forEach(m => {
          grid[m.row][m.col] = null;
        });
        dropCells();
        renderGrid();
      }, 300);
    }

    // Sound effects
    function playSound(type) {
      // Simple beep sound
      const audio = new AudioContext();
      const oscillator = audio.createOscillator();
      const gain = audio.createGain();

      oscillator.connect(gain);
      gain.connect(audio.destination);

      if (type === 'match') {
        oscillator.frequency.value = 800;
        gain.gain.value = 0.1;
      } else if (type === 'powerup') {
        oscillator.frequency.value = 1200;
        gain.gain.value = 0.2;
      }

      oscillator.start();
      oscillator.stop(audio.currentTime + 0.1);
    }

    // Sleep helper
    function sleep(ms) {
      return new Promise(resolve => setTimeout(resolve, ms));
    }

    // Start game
    initGame();
  </script>
</body>
</html>
```

---

## Template 2: Puzzle Game (Escape Room)

**Input**: "Escape room puzzle game, find clues to unlock door, 5 rooms, detective style"

**Output Structure**:
```javascript
// Game elements
- Room scenes with clickable areas
- Inventory system
- Item combination
- Clue collection
- Door unlock mechanic

// Level design
Room 1: Bedroom (find key under pillow)
Room 2: Study (solve number puzzle)
Room 3: Kitchen (find hidden note)
Room 4: Library (arrange books by color)
Room 5: Final room (use all clues)
```

---

## Template 3: Runner Game

**Input**: "Endless runner, character is robot, dodge obstacles, collect coins"

**Output Structure**:
```javascript
// Game elements
- Auto-scrolling background
- Jump/duck controls
- Obstacle spawning
- Coin collection
- Score counter
- Speed increase over time

// Difficulty
- Level 1-5: Slow speed, simple obstacles
- Level 6-10: Faster, complex patterns
```

---

## Game Modification Examples

### Example 1: Change Protagonist
```javascript
// Before: Cat
const player = {
  sprite: '🐱',
  jumpHeight: 150,
  speed: 5
};

// After: Dog
const player = {
  sprite: '🐶',
  jumpHeight: 180, // Dogs jump higher
  speed: 6
};
```

### Example 2: Add Power-up
```javascript
// Add shield power-up
const powerUps = [
  { name: 'Shield', icon: '🛡️', duration: 5000, effect: 'invincible' },
  { name: 'Magnet', icon: '🧲', duration: 10000, effect: 'attractCoins' },
  { name: 'Speed', icon: '⚡', duration: 3000, effect: 'speedBoost' }
];
```

### Example 3: Adjust Difficulty
```javascript
const levelConfig = {
  1: { speed: 2, obstacles: 3, powerUps: 1 },
  5: { speed: 4, obstacles: 6, powerUps: 2 },
  10: { speed: 6, obstacles: 10, powerUps: 3 }
};
```

---

## Style Presets

### Pixel Art
```css
.pixel-art {
  image-rendering: pixelated;
  image-size: 8px;
}
```

### Cartoon
```css
.cartoon {
  border-radius: 20px;
  box-shadow: 0 4px 8px rgba(0,0,0,0.2);
}
```

### Minimalist
```css
.minimalist {
  background: white;
  border: 2px solid black;
}
```
