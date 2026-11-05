# Excel Full Formula Processing Skill v1.1.0 for Minimax

Zero OpenClaw dependency | Local secure XLSX processing | Basic spreadsheet + full Excel formula capabilities

## Core Features

### Basic Spreadsheet
- Create blank .xlsx file with custom worksheet
- Cell text/number read and write
- Single cell read (differentiate raw formula and calculated result)
- Full sheet data export

### Enhanced Formula Core (Comprehensive coverage for check/add/modify/optimize)
1. **Add Formula**: Write standard Excel function formulas to specified rows/cols with auto-calculation
2. **Modify Formula**: Overwrite/replace existing cell formulas
3. **Check Formula**: Syntax validation, bracket matching, invalid characters, function spelling error detection
4. **Optimize Formula**: Simplify inefficient full column references, split nested IFs, reduce redundant calculations, with professional optimization suggestions

### Supported Functions
SUM, AVERAGE, IF, IFS, VLOOKUP, COUNTIF, MAX, MIN, ROUND and other mainstream Excel native formulas

## Trigger Keywords
`excel processing`, `xlsx spreadsheet`, `create Excel file`, `write Excel formula`, `modify cell formula`, `check Excel formula errors`, `optimize Excel function formula`

## Supported Actions

| Action | Description |
|--------|-------------|
| `create` | Create new blank XLSX file |
| `write_cell` | Write text/number to cell |
| `read_cell` | Read cell with formula and result |
| `read_all` | Read entire worksheet |
| `write_formula` | Write/modify Excel formula |
| `check_formula` | Syntax validation |
| `optimize_formula` | Intelligent optimization |

## Deployment Installation

1. Keep the complete directory and all files intact
2. Package as ZIP archive
3. Minimax Agent backend -> Custom Skills -> Import local Skill package
4. Modify `config/settings.yaml` to customize output directory and default worksheet

## Permission Description
- read:file - Read local XLSX files
- write:file - Create/edit local spreadsheets
- network:false - No external network requests, data security isolation

## Environment Dependencies
- Python 3.8+
- openpyxl>=3.1.0 / pyyaml>=6.0 / pytest>=7.0.0

## Unit Test Execution
```bash
cd tests
python test_main.py
```

## Common Usage Examples

### 1. Write/Modify Sum Formula
```
action: write_formula
row: 5, col: 2, formula: =SUM(A1:A4)
```

### 2. Check Error Formula
```
action: check_formula
formula: =SUM(A1:A4
```

### 3. Intelligent Optimize Inefficient Formula
```
action: optimize_formula
formula: =SUM(A:A)
```

## File Structure
```
excel-enhanced/
├── SKILL.md                    # Skill core configuration
├── src/
│   └── main.py                 # Main logic
├── assets/
│   └── .gitkeep                # Static placeholder
├── instructions/
│   └── system_prompt.md        # AI role instructions
├── config/
│   └── settings.yaml           # Global configuration
├── tests/
│   └── test_main.py            # Unit tests
└── README.md                   # Documentation
```
