# Internal Mapping

Use this reference when the user wants the result to feel closer to the internal component ecosystem and page patterns.

## Naming Families

Treat these families as design language rather than hard technical dependencies.

### Base Family

Use for foundational page construction.

**Representative patterns:**
- layout container: page shell, content framing, sectional layout
- form container: search form, edit form, grouped controls
- data table: main data grid
- action button: primary and secondary actions
- side drawer: side-panel workflows
- modal dialog: compact confirmation or form tasks
- tab container: related subviews
- pagination control: result navigation
- status tag: concise status display
- card container: grouped content blocks
- baseline selectors and date pickers: structured inputs

### Business Family

Use for business-aware inputs that encode domain context.

**Representative patterns:**
- date range selector: operational time filters
- location selector: site or branch selection
- organization selector: organization-unit selection
- resource selector: resource lookup and selection
- hierarchy selector: hierarchical location or storage selection
- category selector: category cascader
- object tree selector: object or model tree selection

### Configured Blocks

Use when the page should feel standardized and reusable.

**Representative patterns:**
- standard search form: generated filter area
- standardized table: generated table area
- button group: clustered row or page actions
- fixed footer actions: fixed footer actions for longer forms
- status indicator: dot-plus-text status presentation

## Page Recipes

### Standard List Page

Use this when the user asks for a management list, search page, operational table, or data maintenance page.

**Recipe:**
1. base-layout-like page frame
2. standard-search-form-like filter area or base-form-like filter panel
3. button-group-like action strip
4. standardized-table-like or base-table-like data region
5. pagination-like footer

**Common additions:**
- export action
- batch action
- row-level edit or detail action
- tag-based status column

### Standard Form Page

Use this for create, edit, approval, or configuration pages.

**Recipe:**
1. title and status
2. one or more card-like containers
3. grouped base-form-like sections
4. domain selectors from the business family when relevant
5. fixed-footer-action-like footer actions

### Standard Drawer Flow

Use this for quick create, quick edit, assignment, or side inspection.

**Recipe:**
1. drawer-like container
2. compact base-form-like body
3. limited field count
4. sticky footer with primary and secondary actions

### Standard Detail Page

Use this for record inspection or status tracking.

**Recipe:**
1. header with title and status-tag-like status
2. summary card
3. key-value information blocks
4. tab-container-like related sections
5. operation log or remarks timeline

## Prompt Add-ons

Add one of these snippets when you want the model to lean harder into the internal style.

```
Keep the page structure close to a base-form plus base-table enterprise list pattern, with a restrained search area, standardized table region, and bottom pagination.
```

```
Use internal-style business selectors where relevant, such as organization selectors, location selectors, resource selectors, or category selectors, instead of generic plain inputs.
```

```
For the action area, prefer a button-group-like cluster and a fixed-footer-action-like footer when the workflow is form-heavy.
```
