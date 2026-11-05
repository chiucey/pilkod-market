# Proficiency Assessment Quiz

A 3-question progressive diagnostic to determine learner level.
Present these questions one at a time; stop when the difficulty is clearly beyond the user.

---

## Question 1 — Beginner Tier 🟢

**What will the following code print?**

```python
x = 10
y = 3
print(x // y)
print(x % y)
```

**Expected answer**: `3` and `1`

**Scoring**:
- Both correct → move to Q2
- Wrong → Level: **Beginner**. Explain floor division and modulo.

---

## Question 2 — Novice Tier 🟡

**What does this function return when called as `mystery([1, 2, 3, 4, 5])`?**

```python
def mystery(lst):
    return [x * 2 for x in lst if x % 2 == 0]
```

**Expected answer**: `[4, 8]`

**Scoring**:
- Correct → move to Q3
- Partially correct (understands list comprehension but missed filter) → Level: **Novice**
- Wrong → Level: **Beginner/Novice boundary**

---

## Question 3 — Intermediate/Advanced Tier 🟠🔴

**What will this print, and why?**

```python
def make_counter():
    count = 0
    def increment():
        nonlocal count
        count += 1
        return count
    return increment

c = make_counter()
print(c())
print(c())
print(c())
```

**Expected answer**: `1`, `2`, `3`

**Scoring**:
- Correct with explanation of closures → Level: **Advanced**
- Correct output but unsure about closures → Level: **Intermediate**
- Incorrect → Level: **Novice**

---

## Level Determination Matrix

| Q1 | Q2 | Q3 | Assigned Level |
|----|----|----|----------------|
| Wrong | — | — | Beginner |
| Right | Wrong | — | Novice |
| Right | Right | Wrong/Partial | Intermediate |
| Right | Right | Right | Advanced |

---

## After Quiz

Announce the result warmly:
> "Based on your answers, I'd place you at [LEVEL]. That means we'll [brief description of approach]. Sound good?"

Always allow the user to override: "Feel free to say 'go easier' or 'go harder' anytime!"
