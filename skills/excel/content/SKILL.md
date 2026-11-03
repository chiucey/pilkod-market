---
name: excel
description: Zero OpenClaw dependency, Minimax enhanced Excel full-capability skill; supports XLSX creation/cell read-write/full sheet read + Excel formula add, formula modify, formula syntax error check, inefficient formula intelligent optimization, formula auto-calculation. Use when users ask to process Excel files, create xlsx spreadsheets, write Excel formulas, modify cell formulas, check formula errors, optimize Excel function formulas.
author: Enhanced for Minimax Excel Formula Full Capability
version: 1.1.0
permissions:
  - "read:file"
  - "write:file"
  - "network:false"
triggers:
  - "excel processing"
  - "xlsx spreadsheet"
  - "create Excel file"
  - "write Excel formula"
  - "modify cell formula"
  - "check Excel formula errors"
  - "optimize Excel function formula"
dependencies:
  python:
    - "openpyxl>=3.1.0"
    - "pyyaml>=6.0"
    - "pytest>=7.0.0"
environment_variables:
  - "EXCEL_OUTPUT_PATH"
  - "DEFAULT_SHEET_NAME"
input_schema:
  action:
    type: "string"
    required: true
    enum:
      - "create"
      - "write_cell"
      - "read_cell"
      - "read_all"
      - "write_formula"
      - "check_formula"
      - "optimize_formula"
  file_path:
    type: "string"
    required: false
    description: "XLSX file path"
  sheet_name:
    type: "string"
    required: false
    description: "Worksheet name"
  row:
    type: "integer"
    required: false
    description: "Row number"
  col:
    type: "integer"
    required: false
    description: "Column number"
  value:
    type: "any"
    required: false
    description: "Cell value"
  formula:
    type: "string"
    required: false
    description: "Excel standard = prefix formula"
output_schema:
  status: "success/error"
  data: "Structured results for each operation"
  message_for_user: "User-friendly result message"
---

# Excel Full Formula Processing Skill

Minimax enhanced Excel full-capability skill, zero OpenClaw dependency, supports complete XLSX file operations and formula processing.

## Core Capabilities

### Basic Spreadsheet Capabilities
- `create`: Create new blank XLSX file with custom worksheet
- `write_cell`: Write plain text/numbers to specified cells
- `read_cell`: Read cell raw content + formula + calculated result
- `read_all`: Read all structured data from entire worksheet

### Enhanced Formula Capabilities
- `write_formula`: Add/modify cell Excel formulas, auto-calculate results
- `check_formula`: Intelligent formula check for syntax, bracket pairing, invalid characters, function spelling
- `optimize_formula`: Intelligent optimization of inefficient formulas with professional suggestions

## Supported Functions
SUM, AVERAGE, IF, IFS, VLOOKUP, COUNTIF, MAX, MIN, ROUND and other mainstream Excel native formulas
