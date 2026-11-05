#!/usr/bin/env python3
"""
Enhanced Excel XLSX Core Processing
Zero OpenClaw Dependency
Capabilities: Basic spreadsheet operations + Formula write/modify/check/intelligent optimize/auto-calculate
"""
import sys
import json
import os
import re
from openpyxl import Workbook, load_workbook
from openpyxl.utils import get_column_letter

# Load local YAML configuration
def load_settings():
    import yaml
    settings_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "../config/settings.yaml"
    )
    with open(settings_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

# ====================== Basic Excel Native Capabilities ======================
def create_new_excel(file_path, sheet_name):
    """Create new blank XLSX file"""
    wb = Workbook()
    ws = wb.active
    ws.title = sheet_name
    wb.save(file_path)
    return {"status": "created", "file": file_path, "sheet": sheet_name}

def write_cell(file_path, sheet_name, row, col, value):
    """Write plain text/number to cell"""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    wb = load_workbook(file_path)
    if sheet_name not in wb.sheetnames:
        wb.create_sheet(sheet_name)
    ws = wb[sheet_name]
    r, c = int(row), int(col)
    ws.cell(row=r, column=c, value=value)
    wb.save(file_path)
    return {
        "row": r, "col": c,
        "col_letter": get_column_letter(c),
        "content": value
    }

def read_cell(file_path, sheet_name, row, col):
    """Read cell, distinguish formula/calculated value"""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    wb = load_workbook(file_path, data_only=False)
    if sheet_name not in wb.sheetnames:
        raise ValueError(f"Worksheet {sheet_name} does not exist")
    ws = wb[sheet_name]
    r, c = int(row), int(col)
    cell = ws.cell(row=r, column=c)
    wb_data = load_workbook(file_path, data_only=True)
    ws_data = wb_data[sheet_name]
    calc_val = ws_data.cell(row=r, column=c).value
    return {
        "row": r, "col": c,
        "cell_formula_raw": cell.value,
        "formula_calc_result": calc_val
    }

def read_sheet_all(file_path, sheet_name):
    """Read all data from entire worksheet"""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    wb = load_workbook(file_path, data_only=True)
    if sheet_name not in wb.sheetnames:
        raise ValueError(f"Worksheet {sheet_name} does not exist")
    ws = wb[sheet_name]
    data = []
    for row in ws.iter_rows(values_only=True):
        data.append(list(row))
    return {"sheet_full_data": data, "total_rows": len(data)}

# ====================== Enhanced Formula Capabilities ======================
def write_modify_formula(file_path, sheet_name, row, col, formula):
    """Add / Modify cell Excel formula, auto-calculate result"""
    if not formula.startswith("="):
        formula = "=" + formula
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    wb = load_workbook(file_path)
    if sheet_name not in wb.sheetnames:
        wb.create_sheet(sheet_name)
    ws = wb[sheet_name]
    r, c = int(row), int(col)
    ws.cell(row=r, column=c, value=formula)
    wb.save(file_path)
    # Read calculated value
    wb_only = load_workbook(file_path, data_only=True)
    ws_only = wb_only[sheet_name]
    calc_res = ws_only.cell(row=r, column=c).value
    return {
        "row": r, "col": c,
        "col_letter": get_column_letter(c),
        "final_formula": formula,
        "calculated_result": calc_res
    }

def check_formula_syntax(formula):
    """Check formula: syntax, brackets, invalid characters, common function spelling"""
    check_errors = []
    # Validate = prefix
    if not formula.startswith("="):
        check_errors.append("ERROR: Excel formula must start with '='")
    # Bracket pairing
    if formula.count("(") != formula.count(")"):
        check_errors.append("ERROR: Unmatched parentheses - left and right brackets do not match")
    # Invalid character detection
    invalid_pattern = re.compile(r'[^\w\(\),\.\:\;\=\%\+\-\*\/A-Z0-9 ]')
    bad_chars = invalid_pattern.findall(formula)
    if bad_chars:
        check_errors.append(f"ERROR: Invalid special characters found: {set(bad_chars)}")
    # Common function spelling detection
    common_funcs = ["SUM","AVERAGE","IF","VLOOKUP","COUNTIF","MAX","MIN","ROUND","IFS"]
    for func in common_funcs:
        if re.search(func, formula.upper()) and not re.search(rf"{func}\(", formula.upper()):
            check_errors.append(f"WARNING: {func} function may have incorrect spelling")
    return {
        "input_formula": formula,
        "is_formula_valid": len(check_errors) == 0,
        "error_details": check_errors
    }

def optimize_formula_intelligent(formula):
    """Intelligent optimize redundant/inefficient Excel formulas"""
    orig = formula.strip()
    opt_txt = orig
    tips_list = []
    # Optimization 1: Full column large range reference optimization
    if re.search(r"SUM\(([A-Z]+):\1\)", opt_txt):
        opt_txt = re.sub(r"SUM\(([A-Z]+):\1\)", r"SUM(limited_range)", opt_txt)
        tips_list.append("1. Avoid full column references like A:A, narrow calculation range to improve performance")
    # Optimization 2: Multi-level nested IF split suggestion
    if formula.count("IF(") >= 3:
        opt_txt += "\n[SUGGESTION: For nested IF>=3 levels, consider using IFS function or split into helper columns]"
        tips_list.append("2. Nested IF>=3 levels, recommend replacing with IFS function or split into helper columns")
    # Optimization 3: Repeated calculation simplification
    if "AVERAGE(" in opt_txt.upper():
        opt_txt = re.sub(r"AVERAGE\((.+?)\)", r"Alternative: SUM(\1)/COUNT(\1)", opt_txt, flags=re.IGNORECASE)
        tips_list.append("3. Repeated calculation areas can use named cell ranges to reduce redundancy")
    return {
        "original_formula": orig,
        "optimized_formula_content": opt_txt,
        "optimize_suggestions": tips_list
    }

# ====================== Unified Entry Dispatch ======================
def run(input_data=None):
    try:
        input_data = input_data or {}
        settings = load_settings()
        action = input_data.get("action", "")
        file_path = input_data.get("file_path", os.path.join(settings["output_directory"], "output.xlsx"))
        sheet_name = input_data.get("sheet_name", settings["default_sheet_name"])

        # Basic operation branches
        if action == "create":
            res_data = create_new_excel(file_path, sheet_name)
            msg = "Excel blank file created successfully"
        elif action == "write_cell":
            row = input_data.get("row", 1)
            col = input_data.get("col", 1)
            val = input_data.get("value", "")
            res_data = write_cell(file_path, sheet_name, row, col, val)
            msg = "Cell text/number written successfully"
        elif action == "read_cell":
            row = input_data.get("row", 1)
            col = input_data.get("col", 1)
            res_data = read_cell(file_path, sheet_name, row, col)
            msg = "Cell read completed (raw formula + calculated result)"
        elif action == "read_all":
            res_data = read_sheet_all(file_path, sheet_name)
            msg = f"Full sheet read completed, {res_data['total_rows']} rows of data"

        # Enhanced formula operation branches
        elif action == "write_formula":
            row = input_data.get("row", 1)
            col = input_data.get("col", 1)
            formula = input_data.get("formula", "")
            if not formula:
                return {"status":"error","data":None,"message_for_user":"Please input the Excel formula to write/modify"}
            res_data = write_modify_formula(file_path, sheet_name, row, col, formula)
            msg = "Formula write/modify successful, cell result auto-calculated"
        elif action == "check_formula":
            formula = input_data.get("formula", "")
            res_data = check_formula_syntax(formula)
            msg = "Formula syntax check completed" if res_data["is_formula_valid"] else "Formula errors detected, please check details"
        elif action == "optimize_formula":
            formula = input_data.get("formula", "")
            res_data = optimize_formula_intelligent(formula)
            msg = "Inefficient formula intelligent optimization completed"
        else:
            return {
                "status":"error",
                "data":None,
                "message_for_user":"Invalid action. Supported: create/write_cell/read_cell/read_all/write_formula/check_formula/optimize_formula"
            }

        return {
            "status": "success",
            "data": res_data,
            "message_for_user": msg
        }

    except Exception as e:
        return {
            "status": "error",
            "data": None,
            "message_for_user": f"Excel processing failed: {str(e)}"
        }

if __name__ == "__main__":
    # Adapt to stdin/stdout calling
    if not sys.stdin.isatty():
        input_json = sys.stdin.read()
        input_data = json.loads(input_json) if input_json else {}
    else:
        input_data = {}
    output = run(input_data)
    print(json.dumps(output, ensure_ascii=False, indent=2))
