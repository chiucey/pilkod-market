# Python Style Guide for Learners

A simplified style reference to teach good Python habits from the start.
Adapted from PEP 8 with learner-friendly explanations.

---

## Naming Conventions

| Element | Convention | Example |
|---------|-----------|---------|
| Variable | `snake_case` | `user_name`, `total_score` |
| Function | `snake_case` | `calculate_average()`, `get_user()` |
| Class | `PascalCase` | `StudentRecord`, `HttpClient` |
| Constant | `UPPER_CASE` | `MAX_RETRIES`, `PI` |
| Private | `_single_underscore` | `_internal_value` |
| "Magic" | `__double_underscore__` | `__init__`, `__str__` |

---

## Indentation & Spacing

- Use **4 spaces** per indentation level (not tabs)
- One blank line between methods inside a class
- Two blank lines between top-level functions/classes
- Spaces around operators: `x = 1 + 2` ✅ not `x=1+2` ❌
- No space before colon in function definitions

---

## Comments & Docstrings

```python
# Single-line comment: explain WHY, not WHAT

def calculate_tax(income: float, rate: float) -> float:
    """
    Calculate tax owed based on income and rate.

    Args:
        income: Gross income before tax.
        rate: Tax rate as a decimal (e.g., 0.2 for 20%).

    Returns:
        Tax amount as a float.
    """
    return income * rate
```

**Rules:**
- Every public function/class should have a docstring
- Comments explain *why*, not *what* (code shows what)
- Avoid obvious comments: `x = x + 1  # increment x` ❌

---

## Import Organization

```python
# 1. Standard library imports
import os
import sys

# 2. Third-party imports
import requests
import numpy as np

# 3. Local imports
from mypackage import utils
```

- One import per line
- Alphabetical order within each group
- Never use `from module import *`

---

## Magic Numbers → Named Constants

```python
# Bad ❌
if score > 60:
    print("Pass")

# Good ✅
PASSING_SCORE = 60
if score > PASSING_SCORE:
    print("Pass")
```

---

## Pythonic Patterns to Teach

### Prefer `enumerate()` over manual indexing
```python
# Non-Pythonic ❌
for i in range(len(items)):
    print(i, items[i])

# Pythonic ✅
for i, item in enumerate(items):
    print(i, item)
```

### Use f-strings (Python 3.6+)
```python
name = "Alice"
# Old ❌
print("Hello, %s" % name)
# Modern ✅
print(f"Hello, {name}")
```

### Swap without temp variable
```python
a, b = b, a  # ✅ Pythonic swap
```

### Return early to avoid deep nesting
```python
# Deep nesting ❌
def process(data):
    if data:
        if isinstance(data, list):
            # ... 5 more levels

# Early return ✅
def process(data):
    if not data:
        return None
    if not isinstance(data, list):
        return None
    # main logic here
```

---

## Line Length

- Max **79 characters** per line (PEP 8 standard)
- For long expressions, use parentheses for implicit line continuation:

```python
result = (
    some_long_variable_name
    + another_long_variable
    - yet_another_one
)
```
