# Coverage audit for figures and tables

Use this audit every time before finalizing the deck.

## Step 1: Build the source inventory

List every source visual item in order of appearance.

Required fields:
- item id
- page number
- caption short form
- visual type
- panel notes
- required readable elements
- planned slide number
- final verification status

Example:

| item id | page | caption short form | type | panel notes | required readable elements | planned slide | verified |
|---|---:|---|---|---|---|---:|---|
| Figure 1 | 3 | BAFF/APRIL pathway in IgAN | figure | single panel | receptor labels, kidney deposition pathway, drug labels | 4 | yes |
| Table 1 | 7-8 | conventional strategy for IgAN | table | spans 2 pages | columns, drug names, mechanisms, trial status | 8 | yes |

## Step 2: Decide what counts as coverage

### Figures
A figure counts as covered only if one of the following is true:
1. the original figure is shown directly and remains legible
2. the figure is split or enlarged across slides and all clinically essential parts remain visible
3. the figure is redrawn from source data with original comparison logic, units, labels, and key annotations preserved

Mentioning a figure in text does not count.

### Tables
A table counts as covered only if one of the following is true:
1. the original table is shown directly and remains legible
2. the table is recreated in Chinese with faithful row/column structure and source values
3. the table is split across slides without dropping clinically necessary fields

Summarizing a table into bullets does not count unless the user explicitly permits omission.

## Step 3: Multipanel handling

For multipanel figures, decide whether coverage requires:
- all panels, or
- only clinically material panels

Default rule:
- include all panels when each panel carries distinct information
- omit a panel only if it is duplicative, decorative, or nonessential to interpretation
- if omitting a panel changes the scientific meaning, do not omit it

## Step 4: Legibility thresholds

An item is not covered if any of the following applies:
- axis labels cannot be read
- legend colors or group labels are lost
- p values / significance markers disappear where interpretation depends on them
- table headers or footnotes become unreadable
- the recreated table/chart drops units or key denominators

## Step 5: Reverse and forward checks

Before delivery perform both:

### Reverse check
For each slide, write privately:
- which source item(s) are present
- whether they are cropped, recreated, or redrawn

### Forward check
For each source item, write privately:
- source item -> final slide number(s)
- verification result yes/no

Do not deliver until every source item is `yes`.

## Step 6: Review-paper rule

In review papers, the required source visuals often include:
- mechanistic pathway figures
- summary comparison tables
- treatment landscape tables
- challenge/future-direction summary figures if present

Do not assume that only “results” visuals need coverage.
