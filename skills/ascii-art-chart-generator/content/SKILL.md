---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 001e3bcaf31e78f76157c249e84875ae
    PropagateID: 001e3bcaf31e78f76157c249e84875ae
    ReservedCode1: 3045022017d6c000c76fa0796980b08437a4c942260c575079d0c01073d1cb9044ad647f022100a1f12078086e4a61fc6affbe44c272a90c8f54cf84180cfb751dfef7b83021a2
    ReservedCode2: 3046022100c3abaed7d15c417e8685106d812b695f1b0d50d1c41430b67551a836ef6ef7f6022100d6b4dbfbc65fd173a9afb6d9fce2fd5d4470b95318c56c7e12116d7b9b2b9638
description: Generate ASCII art charts with customizable styles and colors. Use when users request ASCII charts, bar charts, line charts, pie charts, or visual text-based graphs. Trigger phrases include "生成 ASCII 图表", "create ASCII chart", "make a bar chart in terminal", "text-based graph", "ANSI colored output".
name: ascii-art-chart-generator
---

# ASCII Art Chart Generator

A skill for generating various types of ASCII art charts with customizable styling and color support using ANSI escape codes.

## Supported Chart Types

| Type | Description | Trigger Keywords |
|------|-------------|------------------|
| Bar Chart | Vertical bars representing values | `bar`, `柱状图`, `histogram` |
| Line Chart | Points connected by lines | `line`, `折线图`, `trend` |
| Pie Chart | Circular representation using text | `pie`, `饼图`, `percentage` |
| Scatter Plot | Points distributed on grid | `scatter`, `散点图`, `distribution` |
| Table | Text-based data table | `table`, `表格`, `grid` |

## Style Customization Options

### Characters
- **Bar Fill**: `#`, `█`, `▓`, `▒`, `░`, `*`, `@`, `█`
- **Line/Point**: `-`, `=`, `*`, `•`, `○`, `●`
- **Border**: `+`, `-`, `|`, `╔`, `╗`, `╚`, `╝`, `═`, `║`

### Colors (ANSI Escape Codes)
| Color Name | Foreground | Background |
|------------|------------|------------|
| Red | `\033[31m` | `\033[41m` |
| Green | `\033[32m` | `\033[42m` |
| Yellow | `\033[33m` | `\033[43m` |
| Blue | `\033[34m` | `\033[44m` |
| Magenta | `\033[35m` | `\033[45m` |
| Cyan | `\033[36m` | `\033[36m` |
| White | `\033[37m` | `\033[47m` |
| Reset | `\033[0m` | `\033[0m` |

## Chart Generation Workflow

### Step 1: Parse Requirements
Extract from user request:
- Chart type
- Data points (or request them)
- Customization preferences
- Terminal width (default: 80 columns)

### Step 2: Generate Chart
For each chart type, apply the generation algorithm:

**Bar Chart:**
```
1. Calculate max value and scale
2. Determine bar width based on terminal width
3. For each data point:
   - Calculate bar height (proportional to value)
   - Apply fill character
   - Add color if specified
4. Render y-axis labels and gridlines
5. Add legend and title
```

**Line Chart:**
```
1. Normalize data to grid coordinates
2. Plot points using marker character
3. Connect adjacent points with line character
4. Add axis labels and title
```

**Pie Chart:**
```
1. Calculate percentages
2. Use block characters to represent slices: ▏▎▍▌▋▊▉█
3. Add legend with percentages
4. Optional: circular frame using box-drawing chars
```

### Step 3: Apply Styling
- Apply ANSI color codes if requested
- Ensure proper spacing and alignment
- Add title and axis labels
- Include data labels if appropriate

### Step 4: Output
- Return raw ASCII output (user can pipe to terminal)
- Suggest wrapping in backticks for display

## Usage Examples

### Example 1: Simple Bar Chart
**Request:** "Show monthly sales: Jan 100, Feb 150, Mar 120, Apr 200"

**Output:**
```
        ASCII Bar Chart
        ===============

Apr | ████████████████████ 200
Mar | █████████████████ 120
Feb | █████████████████████ 150
Jan | ██████████████ 100

    +---------------------------
        Jan   Feb   Mar   Apr
```

### Example 2: Colored Line Chart
**Request:** "Create a cyan line chart for temperature: 20, 22, 25, 28, 27, 24"

**Output:**
```
 Temperature Trend
 =================

30 |
25 |           ●--------●
20 | ●-----●
    +------------------------
       1    2    3    4    5    6
```

### Example 3: Stylized Bar Chart
**Request:** "Generate a bar chart with green bars using ▓ character"

**Output:** (using green color)
```
\033[32m
    Sales Report Q1
    ===============

Mar | ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ 120
Feb | ▓▓▓▓▓▓▓▓▓▓▓▓▓ 100
Jan | ▓▓▓▓▓▓▓▓▓ 90
\033[0m
```

## Error Handling

- **Missing data**: Prompt user for required data points
- **Invalid values**: Filter non-numeric values and notify user
- **Terminal width overflow**: Auto-scale or suggest breaking into multiple charts
- **Color not supported**: Provide fallback monochrome version

## Best Practices

1. Always include a title for the chart
2. Label axes clearly
3. Use consistent scales
4. Keep charts readable in narrow terminals (min 40 columns)
5. Use color sparingly for emphasis
6. Include a legend when multiple data series are present
