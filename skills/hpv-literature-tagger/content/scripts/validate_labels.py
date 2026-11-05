#!/usr/bin/env python3
"""Validate HPV literature tagging Excel files against V2 taxonomy.

Usage:
  python scripts/validate_labels.py input.xlsx --sheet 标签结果 --out validation_report.txt
"""
import argparse
import re
import sys
from pathlib import Path

try:
    import openpyxl
except Exception as exc:
    print(f"ERROR: openpyxl is required: {exc}", file=sys.stderr)
    sys.exit(2)

REQUIRED_COLUMNS = [
    "age",
    "population",
    "ethnicity/region",
    "type/exposure",
    "condition/relate disease",
    "outcome",
    "sample'size",
    "time",
]

TYPE_TAGS = {
    "cross", "cho", "casec", "caser", "meta", "rev", "mec", "resp", "rct",
    "nrct", "model", "guide", "consensus", "prospective", "implementation",
    "qualitative study",
}

EXPOSURE_TAGS = {"1", "2", "3", "4", "5", "6", "7"}

POP_TAGS = {
    "g", "msm", "msw", "uk", "children", "adolescent", "hcp", "parents",
    "staff", "bi", "female", "HIV", "diabetes", "sle", "ckd", "students",
    "PCa", "BPH", "les", "syphilis", "GNH", "HSV", "HTN", "CAD",
    "Obesity", "HLD", "PID", "MC", "HBV", "CT", "PLWH", "SPN", "P",
    "Neo", "CDH", "thyroid cancer", "EBV", "CAT", "PNI", "COPD", "IS",
    "Liver disease", "Renal disease", "AMI", "HF", "Peripheral vascular disease",
    "Cerebrovascular disease", "Dementia", "CLRD", "CTD", "PUD",
    "Diabetes mellitus with complications", "HP", "Malignancy", "Metastatic cancer",
    "Psych dis", "RF", "Tracheotomy", "FSWs", "depression", "stroke",
    "Alcohol-related illness", "AID", "psoriasis", "osteoporosis",
    "ischemic heart disease", "TB", "na",
}
POP_SETTINGS = {"cl", "co", "na"}
REGION_TAGS = {"c", "y", "n", "na"}
CENTER_TAGS = {"m", "s", "na"}
CONDITION_TAGS = {
    "0", "0.5", "1", "2", "2.1", "2.2", "2.5", "3", "4", "5",
    "5.1", "5.2", "5.3", "5.4", "5.5", "5.6", "5.7", "5.8",
    "6", "7", "8", "8.1", "9", "10",
}
OUTCOME_TAGS = {
    "pre", "in", "or", "rr", "pi", "gen", "hr", "dr", "safety", "rein",
    "psy", "cost", "clear", "sur", "imm", "qlife", "kap", "vcr",
    "recommendation", "concern", "avertcases", "policies", "effectiveness",
    "efficacy", "fertility", "na",
}


def split_tags(value):
    return [part.strip() for part in str(value).split(",") if part.strip()]


def cell(row, col_index):
    value = row[col_index].value
    return "" if value is None else str(value).strip()


def validate_age(value):
    issues = []
    if not value:
        return ["age is blank"]
    if value == "na":
        issues.append("age missing should be 'na,na', not 'na'")
    if value == "0,12":
        issues.append("do not infer minimum age 0; use ',12' when only <=12 is stated")
    if value != "na,na" and value.count(",") > 1:
        issues.append("age should contain at most one comma")
    return issues


def validate_population(value):
    issues = []
    parts = split_tags(value)
    if len(parts) < 2:
        return ["population must include population tag(s) plus setting cl/co/na"]
    setting = parts[-1]
    if setting not in POP_SETTINGS:
        issues.append("population final setting must be cl, co, or na")
    for tag in parts[:-1]:
        if tag not in POP_TAGS:
            issues.append(f"unknown population tag: {tag}")
    return issues


def validate_region(value):
    parts = split_tags(value)
    issues = []
    if len(parts) != 2:
        return ["ethnicity/region must be region,center"]
    if parts[0] not in REGION_TAGS:
        issues.append(f"unknown region tag: {parts[0]}")
    if parts[1] not in CENTER_TAGS:
        issues.append(f"unknown center tag: {parts[1]}")
    return issues


def validate_type_exposure(value):
    parts = split_tags(value)
    issues = []
    if len(parts) < 2:
        return ["type/exposure must include type tag(s) and numeric exposure 1-7"]
    exposure = parts[-1]
    if exposure not in EXPOSURE_TAGS:
        issues.append(f"exposure must be number 1-7, got: {exposure}")
    for tag in parts[:-1]:
        if tag == "na":
            issues.append("type must not be na")
        elif tag not in TYPE_TAGS:
            issues.append(f"unknown type tag: {tag}")
    return issues


def validate_condition(value):
    issues = []
    for tag in split_tags(value):
        if tag not in CONDITION_TAGS:
            issues.append(f"unknown condition tag: {tag}")
    parts = set(split_tags(value))
    for child, parent in [("2.1", "2"), ("2.2", "2"), ("2.5", "2")]:
        if child in parts and parent not in parts:
            issues.append(f"condition child {child} should include parent {parent}")
    for child in ["5.1", "5.2", "5.3", "5.4", "5.5", "5.6", "5.7", "5.8"]:
        if child in parts and "5" not in parts:
            issues.append(f"condition child {child} should include parent 5")
    return issues


def validate_outcome(value):
    issues = []
    for tag in split_tags(value):
        if tag not in OUTCOME_TAGS:
            issues.append(f"unknown outcome tag: {tag}")
    return issues


def validate_sample_size(value):
    if not value:
        return ["sample'size is blank"]
    if value == "na":
        return []
    normalized = value.replace(",", "")
    if not re.fullmatch(r"\d+(\.\d+)?", normalized):
        return ["sample'size must be a male count number or na"]
    return []


def validate_time(value):
    issues = []
    if not value:
        return ["time is blank"]
    if value == "na":
        issues.append("time missing should be 'na,na', not 'na'")
    if value != "na,na":
        parts = split_tags(value)
        if len(parts) != 2:
            issues.append("time must be start_year,period")
        else:
            if parts[0] != "na" and not re.fullmatch(r"\d{4}", parts[0]):
                issues.append("time start year must be a 4-digit year or na")
            if parts[1] != "na" and not re.fullmatch(r"0|\d+(\.\d+)?[dmy]", parts[1]):
                issues.append("time period should look like 0, 1d, 1m, 1y, or decimal y/m/d")
    return issues


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--sheet", default="标签结果")
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args()

    wb = openpyxl.load_workbook(args.input, data_only=True)
    if args.sheet not in wb.sheetnames:
        print(f"ERROR: sheet not found: {args.sheet}", file=sys.stderr)
        sys.exit(1)
    ws = wb[args.sheet]

    headers = [str(c.value).strip() if c.value is not None else "" for c in ws[1]]
    colmap = {name: idx for idx, name in enumerate(headers)}

    report = []
    missing_cols = [col for col in REQUIRED_COLUMNS if col not in colmap]
    if missing_cols:
        report.append("CRITICAL missing required columns: " + ", ".join(missing_cols))

    validators = {
        "age": validate_age,
        "population": validate_population,
        "ethnicity/region": validate_region,
        "type/exposure": validate_type_exposure,
        "condition/relate disease": validate_condition,
        "outcome": validate_outcome,
        "sample'size": validate_sample_size,
        "time": validate_time,
    }

    issue_count = 0
    if not missing_cols:
        for excel_row_num, row in enumerate(ws.iter_rows(min_row=2), start=2):
            row_label = cell(row, colmap.get("PDF/File name", 0)) or f"row {excel_row_num}"
            for field, validator in validators.items():
                value = cell(row, colmap[field])
                for issue in validator(value):
                    issue_count += 1
                    report.append(f"Row {excel_row_num} ({row_label}) [{field}]: {issue}; value='{value}'")

    if issue_count == 0 and not missing_cols:
        report.insert(0, "PASS: no critical validation issues found.")
    else:
        report.insert(0, f"FAIL: {issue_count} validation issue(s) found.")

    text = "\n".join(report) + "\n"
    if args.out:
        args.out.write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
