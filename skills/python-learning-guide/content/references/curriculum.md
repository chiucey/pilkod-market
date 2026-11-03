# Python Learning Curriculum

A structured progression from zero to advanced Python proficiency.

---

## Level 1: Beginner 🟢

**Goal**: Write and understand simple Python scripts.

### Module 1.1 — Environment & First Steps
- Installing Python & running scripts (`python hello.py`)
- REPL (interactive shell)
- `print()`, comments, indentation rules

### Module 1.2 — Variables & Data Types
- `int`, `float`, `str`, `bool`
- Variable assignment and naming conventions
- `type()` function, basic type conversion

### Module 1.3 — Operators
- Arithmetic: `+`, `-`, `*`, `/`, `//`, `%`, `**`
- Comparison: `==`, `!=`, `<`, `>`, `<=`, `>=`
- Logical: `and`, `or`, `not`

### Module 1.4 — Control Flow
- `if` / `elif` / `else`
- Truthy and falsy values
- Nested conditions

### Module 1.5 — Loops
- `for` loop with `range()`
- `while` loop
- `break`, `continue`, `pass`

### Module 1.6 — Input & Output
- `input()`, formatting strings with f-strings
- Basic `print()` formatting

---

## Level 2: Novice 🟡

**Goal**: Build small functional programs using Python's core structures.

### Module 2.1 — Functions
- `def`, parameters, return values
- Default arguments, keyword arguments
- Scope (local vs global)
- Docstrings

### Module 2.2 — Collections
- Lists: indexing, slicing, methods (`append`, `remove`, `sort`)
- Tuples: immutability, unpacking
- Dictionaries: key-value, `.get()`, `.items()`, `.keys()`
- Sets: uniqueness, union, intersection

### Module 2.3 — String Manipulation
- Methods: `.upper()`, `.lower()`, `.split()`, `.join()`, `.strip()`
- Formatting: f-strings, `.format()`
- String indexing and slicing

### Module 2.4 — List Comprehensions
- Basic syntax: `[expr for item in iterable]`
- Conditional filtering: `[expr for item in iterable if cond]`

### Module 2.5 — Modules & Imports
- `import`, `from ... import`
- Standard library: `math`, `random`, `datetime`, `os`, `sys`
- `__name__ == "__main__"` pattern

---

## Level 3: Intermediate 🟠

**Goal**: Write well-structured, reusable Python code.

### Module 3.1 — Object-Oriented Programming
- Classes, `__init__`, instance attributes
- Methods, `self`
- Inheritance, `super()`
- `__str__`, `__repr__`, `__len__` (dunder methods)

### Module 3.2 — Error Handling
- `try` / `except` / `else` / `finally`
- Exception types: `ValueError`, `TypeError`, `FileNotFoundError`, etc.
- Raising exceptions: `raise`
- Custom exception classes

### Module 3.3 — File I/O
- Reading/writing files: `open()`, context managers (`with`)
- CSV: `csv` module
- JSON: `json.load()`, `json.dump()`

### Module 3.4 — Functional Programming
- `lambda`, `map()`, `filter()`, `sorted()` with `key=`
- `zip()`, `enumerate()`
- Generator expressions

### Module 3.5 — Iterators & Generators
- `iter()`, `next()`
- `yield` keyword, generator functions
- `itertools` module

### Module 3.6 — Virtual Environments & Packages
- `venv`, `pip install`, `requirements.txt`
- Understanding `site-packages`

---

## Level 4: Advanced 🔴

**Goal**: Write production-quality Python — efficient, maintainable, testable.

### Module 4.1 — Decorators
- First-class functions, closures
- `@decorator` syntax
- `functools.wraps`, decorator factories
- Built-in decorators: `@property`, `@classmethod`, `@staticmethod`

### Module 4.2 — Type Hints & Typing
- Basic annotations: `int`, `str`, `List[str]`, `Optional[int]`
- `typing` module: `Union`, `Callable`, `TypeVar`
- `mypy` for static analysis

### Module 4.3 — Concurrency
- Threading vs multiprocessing
- `asyncio`: `async def`, `await`, event loop
- `aiohttp` for async HTTP

### Module 4.4 — Testing
- `unittest` framework
- `pytest`: fixtures, parametrize, mocking
- TDD basics

### Module 4.5 — Performance & Profiling
- `timeit`, `cProfile`
- Memory optimization: generators vs lists
- `numpy` basics for numerical work

### Module 4.6 — Advanced Patterns
- Context managers: `__enter__`, `__exit__`, `@contextmanager`
- Metaclasses (overview)
- Dataclasses: `@dataclass`
- Design patterns in Python: Singleton, Factory, Observer
