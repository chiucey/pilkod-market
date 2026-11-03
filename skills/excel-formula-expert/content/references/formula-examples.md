# Excel Formula Examples Library

## Statistics

### COUNTIFS - Multiple Criteria Count

**Requirement**: Count orders where Column A sales > 500 AND Column B region = Beijing

**Formula**:
```excel
=COUNTIFS(A:A,">500",B:B,"Beijing")
```

**Parameter Explanation**:
- `A:A`: Sales column
- `">500"`: Sales condition (greater than 500)
- `B:B`: Region column
- `"Beijing"`: Region condition

**Sample Data**:
| Column A (Sales) | Column B (Region) | Counted? |
|------------------|------------------|----------|
| 600 | Beijing | ✅ +1 |
| 400 | Beijing | ❌ Sales too low |
| 600 | Shanghai | ❌ Region mismatch |
| 800 | Beijing | ✅ +1 |

**Formula Result**: 2

---

### SUMIFS - Multiple Criteria Sum

**Requirement**: Calculate total amount for Beijing region with sales > 500

**Formula**:
```excel
=SUMIFS(C:C, A:A,">500", B:B,"Beijing")
```

**Parameter Explanation**:
- `C:C`: Amount column (to sum)
- `A:A`: Sales column (criteria column 1)
- `">500"`: Sales condition
- `B:B`: Region column (criteria column 2)
- `"Beijing"`: Region condition

**Sample Data**:
| Column A (Sales) | Column B (Region) | Column C (Amount) |
|------------------|------------------|-------------------|
| 600 | Beijing | 1500 |
| 400 | Beijing | 800 |
| 600 | Shanghai | 2000 |
| 800 | Beijing | 3000 |

**Formula Result**: 4500 (1500+3000)

---

## Lookup

### VLOOKUP - Vertical Lookup

**Requirement**: Lookup department by name

**Formula**:
```excel
=VLOOKUP(F2, A:D, 3, 0)
```

**Parameter Explanation**:
- `F2`: Name to lookup
- `A:D`: Lookup range (must include return column)
- `3`: Column number of return value (3rd column)
- `0`: Exact match

**Sample Data**:
| Column A (Name) | Column B (ID) | Column C (Dept) | Column D (Title) |
|----------------|---------------|-----------------|------------------|
| John | A001 | Sales | Manager |
| Mary | A002 | Engineering | Engineer |

F2 = "Mary" → Formula Result = "Engineering"

**Advanced**: Multi-criteria lookup
```excel
=INDEX(C:C, MATCH(1, (A:A=F2)*(B:B=G2), 0))
```

---

### XLOOKUP - Modern Lookup (Office 365)

**Requirement**: Replace VLOOKUP with more flexible lookup

**Formula**:
```excel
=XLOOKUP(F2, A:A, C:C, "Not Found")
```

**Parameter Explanation**:
- `F2`: Value to lookup
- `A:A`: Lookup column
- `C:C`: Return column
- `"Not Found"`: Value to display when not found

---

## Conditional

### IF - Conditional Logic

**Requirement**: Show "Excellent" if sales > 1000, otherwise "Normal"

**Formula**:
```excel
=IF(A2>1000, "Excellent", "Normal")
```

**Nested IF**:
```excel
=IF(A2>=1000, "Excellent", IF(A2>=500, "Good", "Normal"))
```

---

### IFS - Multiple Condition Branches

**Requirement**: Return grade based on score

**Formula**:
```excel
=IFS(A2>=90, "A", A2>=80, "B", A2>=60, "C", A2<60, "D")
```

---

## Data Extraction

### FILTER - Filter Data (Dynamic Array)

**Requirement**: Filter all Beijing records

**Formula**:
```excel
=FILTER(A:C, B:B="Beijing")
```

**Parameter Explanation**:
- `A:C`: Column range to return
- `B:B="Beijing"`: Filter condition

---

### UNIQUE - Remove Duplicates

**Requirement**: Extract unique region list

**Formula**:
```excel
=UNIQUE(B:B)
```

---

## Text Processing

### TEXTJOIN - Text Concatenation

**Requirement**: Join multiple cell texts with comma

**Formula**:
```excel
=TEXTJOIN(",", TRUE, A:A)
```

**Parameter Explanation**:
- `","`: Delimiter
- `TRUE`: Ignore empty cells
- `A:A`: Column to join

---

### LEFT/RIGHT/MID - Text Extraction

```excel
=LEFT(A1, 3)      "Extract first 3 characters"
=RIGHT(A1, 4)     "Extract last 4 characters"
=MID(A1, 2, 5)    "Extract 5 characters from position 2"
```

---

## Date Functions

### DATEDIF - Date Difference

**Requirement**: Calculate days/months/years between two dates

**Formula**:
```excel
=DATEDIF(A1, B1, "D")  "Days"
=DATEDIF(A1, B1, "M")  "Months"
=DATEDIF(A1, B1, "Y")  "Years"
```

---

### YEAR/MONTH/DAY - Date Extraction

```excel
=YEAR(A1)   "Extract year"
=MONTH(A1)  "Extract month"
=DAY(A1)    "Extract day"
```

---

## Advanced Techniques

### SUMPRODUCT - Conditional Sum (Array Logic)

**Requirement**: Count with multiple criteria

**Formula**:
```excel
=SUMPRODUCT((A:A>500)*(B:B="Beijing")*(C:C))
```

**Equivalent to**:
```excel
=SUMIFS(C:C, A:A,">500", B:B,"Beijing")
```

---

### IFERROR - Error Handling

**Requirement**: Show default value when lookup fails

**Formula**:
```excel
=IFERROR(VLOOKUP(F2, A:D, 3, 0), "Not Found")
```

---

### COUNTBLANK - Count Blanks

**Requirement**: Count blank cells in a column

**Formula**:
```excel
=COUNTBLANK(A:A)
```
