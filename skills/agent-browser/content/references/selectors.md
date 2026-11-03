# Selector Syntax Reference

## Standard CSS Selectors

### Basic Selectors

```css
/* ID selector */
#element-id

/* Class selector */
.element-class

/* Tag selector */
div, span, p

/* Attribute selector */
[disabled]
[type="text"]
[data-value="test"]
```

### Combinators

```css
/* Descendant */
.parent .child

/* Child */
.parent > .child

/* Adjacent sibling */
.element + .next

/* General sibling */
.element ~ .siblings
```

### Pseudo-selectors

```css
/* First/last child */
li:first-child
li:last-child

/* Nth child */
tr:nth-child(2)
tr:nth-child(odd)

/* Not */
button:not(.disabled)

/* Contains text */
td:contains("Hello")
```

## Extended Selector Syntax

### Attribute Extraction

```
selector@attribute-name
```

Examples:
- `a@href` - Get link URL
- `img@src` - Get image source
- `input@value` - Get input value
- `button@disabled` - Get disabled state

### Content Extraction

```
selector::text
selector::html
```

Examples:
- `h1::text` - Get inner text
- `article::html` - Get inner HTML
- `.price::text` - Get price text

## XPath Selectors

Prefix with `xpath:`:

```
xpath://div[@class='container']//button
xpath://input[@type='submit']
xpath://td[contains(text(),'Total')]
```

## Best Practices

1. **Prefer unique selectors** - Use IDs when available
2. **Avoid deeply nested selectors** - Keep it simple
3. **Use data attributes** - Add `data-testid` for testing
4. **Handle missing elements** - Always provide fallbacks

## Common Patterns

### Form Elements

```css
/* All inputs */
input, textarea, select

/* By type */
input[type="text"]
input[type="email"]
input[type="password"]

/* By name */
input[name="username"]
select[name="country"]
```

### Links and Buttons

```css
/* Links */
a[href]
a[href^="https"]
a[href*="example"]

/* Buttons */
button
.btn
[type="submit"]
[type="button"]
```

### Tables

```css
/* Table rows */
tr
tbody tr

/* Specific cells */
td:nth-child(2)
td:nth-last-child(1)
```
