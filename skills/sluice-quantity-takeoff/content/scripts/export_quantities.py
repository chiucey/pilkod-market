#!/usr/bin/env python3
"""Export sluice quantity takeoff JSON to an XLSX workbook."""

from __future__ import annotations

import json
import sys
import zipfile
from collections import defaultdict
from pathlib import Path
from xml.sax.saxutils import escape


SHEETS = [
    ("参数提取", "parameters"),
    ("工程量明细", "details"),
    ("材料汇总", "material_summary"),
    ("分段汇总", "segment_summary"),
    ("缺失信息", "missing"),
    ("假设条件", "assumptions"),
    ("图纸识别", "drawings"),
]

DETAIL_COLUMNS = [
    "segment",
    "component",
    "material",
    "quantity_m3",
    "formula",
    "confidence",
    "source",
    "notes",
]

PARAMETER_COLUMNS = ["segment", "parameter", "value", "unit", "source", "notes"]
MISSING_COLUMNS = ["segment", "item", "impact", "needed", "source"]
DRAWING_COLUMNS = ["file", "role", "title", "section", "notes"]


def col_name(index: int) -> str:
    name = ""
    index += 1
    while index:
        index, rem = divmod(index - 1, 26)
        name = chr(65 + rem) + name
    return name


def cell_xml(row: int, col: int, value) -> str:
    ref = f"{col_name(col)}{row}"
    if isinstance(value, dict) and "formula" in value:
        formula = escape(str(value.get("formula", "")))
        cached = value.get("value", 0)
        return f'<c r="{ref}"><f>{formula}</f><v>{cached}</v></c>'
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return f'<c r="{ref}"><v>{value}</v></c>'
    text = "" if value is None else str(value)
    return f'<c r="{ref}" t="inlineStr"><is><t>{escape(text)}</t></is></c>'


def sheet_xml(rows: list[list[object]]) -> str:
    body = []
    for row_index, row in enumerate(rows, start=1):
        cells = "".join(cell_xml(row_index, col_index, value) for col_index, value in enumerate(row))
        body.append(f'<row r="{row_index}">{cells}</row>')
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        "<sheetData>"
        + "".join(body)
        + "</sheetData></worksheet>"
    )


def rows_from_dicts(items: list[dict], columns: list[str]) -> list[list[object]]:
    rows: list[list[object]] = [columns]
    for item in items:
        rows.append([item.get(column, "") for column in columns])
    return rows


def normalize_text_rows(items: list[object], column_name: str) -> list[list[object]]:
    rows: list[list[object]] = [[column_name]]
    for item in items:
        if isinstance(item, dict):
            rows.append([json.dumps(item, ensure_ascii=False)])
        else:
            rows.append([item])
    return rows


def build_summaries(details: list[dict]) -> tuple[list[dict], list[dict]]:
    by_material: dict[str, float] = defaultdict(float)
    by_segment: dict[str, float] = defaultdict(float)

    for item in details:
        try:
            quantity = float(item.get("quantity_m3", 0) or 0)
        except (TypeError, ValueError):
            continue
        by_material[item.get("material", "未知材料")] += quantity
        by_segment[item.get("segment", "未知分段")] += quantity

    material_rows = []
    for row_index, (material, quantity) in enumerate(sorted(by_material.items()), start=2):
        material_rows.append(
            {
                "material": material,
                "quantity_m3": {
                    "formula": f'SUMIF(\'工程量明细\'!C:C,A{row_index},\'工程量明细\'!D:D)',
                    "value": round(quantity, 3),
                },
            }
        )

    segment_rows = []
    for row_index, (segment, quantity) in enumerate(sorted(by_segment.items()), start=2):
        segment_rows.append(
            {
                "segment": segment,
                "quantity_m3": {
                    "formula": f'SUMIF(\'工程量明细\'!A:A,A{row_index},\'工程量明细\'!D:D)',
                    "value": round(quantity, 3),
                },
            }
        )
    return material_rows, segment_rows


def workbook_xml() -> str:
    sheets = []
    for index, (name, _key) in enumerate(SHEETS, start=1):
        sheets.append(f'<sheet name="{escape(name)}" sheetId="{index}" r:id="rId{index}"/>')
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
        "<sheets>"
        + "".join(sheets)
        + "</sheets></workbook>"
    )


def workbook_rels_xml() -> str:
    rels = []
    for index, _sheet in enumerate(SHEETS, start=1):
        rels.append(
            f'<Relationship Id="rId{index}" '
            'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" '
            f'Target="worksheets/sheet{index}.xml"/>'
        )
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        + "".join(rels)
        + "</Relationships>"
    )


def content_types_xml() -> str:
    overrides = [
        '<Override PartName="/xl/workbook.xml" '
        'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
    ]
    for index, _sheet in enumerate(SHEETS, start=1):
        overrides.append(
            f'<Override PartName="/xl/worksheets/sheet{index}.xml" '
            'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
        )
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        + "".join(overrides)
        + "</Types>"
    )


def root_rels_xml() -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" '
        'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" '
        'Target="xl/workbook.xml"/>'
        "</Relationships>"
    )


def write_xlsx(data: dict, output_path: Path) -> None:
    details = data.get("details", [])
    material_summary, segment_summary = build_summaries(details)

    sheet_rows = {
        "parameters": rows_from_dicts(data.get("parameters", []), PARAMETER_COLUMNS),
        "details": rows_from_dicts(details, DETAIL_COLUMNS),
        "material_summary": rows_from_dicts(material_summary, ["material", "quantity_m3"]),
        "segment_summary": rows_from_dicts(segment_summary, ["segment", "quantity_m3"]),
        "missing": rows_from_dicts(data.get("missing", []), MISSING_COLUMNS),
        "assumptions": normalize_text_rows(data.get("assumptions", []), "assumption"),
        "drawings": rows_from_dicts(data.get("drawings", []), DRAWING_COLUMNS),
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml", content_types_xml())
        archive.writestr("_rels/.rels", root_rels_xml())
        archive.writestr("xl/workbook.xml", workbook_xml())
        archive.writestr("xl/_rels/workbook.xml.rels", workbook_rels_xml())
        for index, (_name, key) in enumerate(SHEETS, start=1):
            archive.writestr(f"xl/worksheets/sheet{index}.xml", sheet_xml(sheet_rows[key]))


def main() -> int:
    if len(sys.argv) != 3:
        print("Usage: export_quantities.py takeoff.json output.xlsx", file=sys.stderr)
        return 2

    input_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])
    data = json.loads(input_path.read_text(encoding="utf-8"))
    write_xlsx(data, output_path)
    print(output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
