# Practice Projects by Level

Suggested hands-on projects to reinforce learning at each level.
Assign after a session or when the user asks "what should I build?"

---

## Beginner Projects 🟢

### 1. Number Guessing Game
- Use `random.randint()`, `input()`, and a `while` loop
- Track number of attempts
- **Skills**: variables, loops, conditionals, input/output

### 2. Simple Calculator
- Accept two numbers and an operator (`+`, `-`, `*`, `/`)
- Handle division by zero
- **Skills**: conditionals, functions, error handling basics

### 3. Temperature Converter
- Convert between Celsius, Fahrenheit, Kelvin
- **Skills**: functions, arithmetic, string formatting

### 4. FizzBuzz
- Print numbers 1-100, replacing multiples of 3 with "Fizz", 5 with "Buzz"
- **Skills**: loops, conditionals, modulo operator

---

## Novice Projects 🟡

### 1. To-Do List (CLI)
- Add, remove, list, and mark tasks as done
- Store tasks in a list/dict
- **Skills**: lists, functions, loops, basic I/O

### 2. Word Frequency Counter
- Read a text string/file and count word occurrences
- Sort by frequency
- **Skills**: dictionaries, string methods, sorting

### 3. Student Grade Calculator
- Store student names + scores in a dict
- Calculate average, find highest/lowest
- **Skills**: dicts, list comprehensions, functions

### 4. Simple Quiz App
- Load questions from a list of dicts
- Track score and display result
- **Skills**: dicts, loops, conditionals, functions

---

## Intermediate Projects 🟠

### 1. Personal Expense Tracker
- Classes for `Transaction`, `Category`, `Budget`
- Read/write to a JSON file
- **Skills**: OOP, file I/O, JSON, exceptions

### 2. Weather CLI App
- Fetch weather via public API (e.g., wttr.in)
- Parse JSON response and display nicely
- **Skills**: `requests`, JSON, string formatting, error handling

### 3. Text-Based RPG
- Player, Enemy, Item classes
- Combat system with turn-based logic
- **Skills**: OOP, inheritance, game loop, exceptions

### 4. CSV Data Analyzer
- Load a CSV, compute statistics (mean, median, std)
- Filter and sort data
- **Skills**: `csv` module, list comprehensions, `statistics` module

---

## Advanced Projects 🔴

### 1. Async Web Scraper
- Scrape multiple URLs concurrently
- Parse HTML with `BeautifulSoup`
- **Skills**: `asyncio`, `aiohttp`, parsing, rate limiting

### 2. CLI Tool with `argparse`
- A utility tool (e.g., file organizer, log parser)
- Full argument parsing, help text, error messages
- **Skills**: `argparse`, OOP, file system, decorators

### 3. REST API with FastAPI
- CRUD endpoints for a resource (tasks, users, etc.)
- Pydantic models, async handlers
- **Skills**: FastAPI, type hints, async, testing with `pytest`

### 4. Tested Library Package
- Write a small utility library (e.g., date helpers, string utils)
- Full `pytest` test suite with fixtures and edge cases
- Package with `pyproject.toml`
- **Skills**: packaging, testing, type hints, CI readiness
