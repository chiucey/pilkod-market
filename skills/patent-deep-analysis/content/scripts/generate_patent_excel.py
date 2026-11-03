#!/usr/bin/env python3
"""Generate or append to a structured Excel report from patent analysis results JSON."""

import argparse
import json
import os
import sys


COLUMNS = [
    ("basic_info.patent_title", "专利名称", 25),
    ("basic_info.application_number", "申请号", 18),
    ("basic_info.applicant", "申请人", 20),
    ("basic_info.inventor", "发明人", 15),
    ("basic_info.inventor_classification", "发明人分类", 30),
    ("basic_info.filing_date", "申请日期", 12),
    ("solution_summary", "一句话方案简述", 35),
    ("invention_point", "一句话发明点", 35),
    ("application_scenarios", "应用场景", 30),
    ("technical_category", "技术分支归类", 35),
    ("technical_branch", "重点技术分支", 40),
    ("lm_video_judgment", "大模型与音视频结合", 35),
    ("technical_analysis.architecture", "技术架构梳理", 40),
    ("technical_analysis.implementation_details", "关键实现细节", 40),
    ("technical_analysis.background", "技术背景说明", 35),
    ("rd_inspiration.adaptability", "技术适配性评估", 35),
    ("rd_inspiration.innovation_points", "技术创新点挖掘", 35),
    ("rd_inspiration.cross_scene", "跨场景创新启发", 30),
    ("recommendations.research_reference", "可作为技术研究参考", 30),
    ("recommendations.differentiated_innovation", "建议差异化创新", 30),
    ("recommendations.gap_breakthrough", "可突破技术空白点", 30),
]


def get_nested_value(data, path):
    keys = path.split(".")
    current = data
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return ""
    return str(current) if current else ""


def get_column_letter(col_idx):
    result = ""
    while col_idx > 0:
        col_idx, remainder = divmod(col_idx - 1, 26)
        result = chr(65 + remainder) + result
    return result


def create_workbook():
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Border, Font, PatternFill, Side

    wb = Workbook()
    ws = wb.active
    ws.title = "专利深度解读报告"

    header_font = Font(bold=True, size=10, color="FFFFFF")
    header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
    header_alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    thin_border = Border(
        left=Side(style="thin"), right=Side(style="thin"),
        top=Side(style="thin"), bottom=Side(style="thin")
    )

    all_headers = ["序号", "文件名"] + [col[1] for col in COLUMNS]
    all_widths = [5, 18] + [col[2] for col in COLUMNS]

    for col_idx, (header, width) in enumerate(zip(all_headers, all_widths), 1):
        cell = ws.cell(row=1, column=col_idx, value=header)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = header_alignment
        cell.border = thin_border
        ws.column_dimensions[get_column_letter(col_idx)].width = width

    ws.row_dimensions[1].height = 35
    ws.freeze_panes = "A2"
    return wb, ws


def append_to_workbook(ws, analysis_data, start_row=2):
    from openpyxl.styles import Alignment, Border, Side

    cell_alignment = Alignment(vertical="top", wrap_text=True)
    thin_border = Border(
        left=Side(style="thin"), right=Side(style="thin"),
        top=Side(style="thin"), bottom=Side(style="thin")
    )

    current_row = start_row
    for item in analysis_data:
        filename = item.get("filename", "")
        row_values = [current_row - 1, filename]
        for col_path, _, _ in COLUMNS:
            row_values.append(get_nested_value(item, col_path))

        max_len = 0
        for col_idx, value in enumerate(row_values, 1):
            cell = ws.cell(row=current_row, column=col_idx, value=str(value) if value else "")
            cell.alignment = cell_alignment
            cell.border = thin_border
            if value:
                max_len = max(max_len, len(str(value)))

        ws.row_dimensions[current_row].height = min(max(30, max_len // 3), 200)
        current_row += 1
    return current_row


def generate_excel(analysis_data, output_path, append=False):
    from openpyxl import load_workbook

    output_dir = os.path.dirname(os.path.abspath(output_path))
    os.makedirs(output_dir, exist_ok=True)

    if append and os.path.isfile(output_path):
        print(f"Appending to existing file: {output_path}", file=sys.stderr)
        wb = load_workbook(output_path)
        ws = wb.active
        append_to_workbook(ws, analysis_data, ws.max_row + 1)
    else:
        if append:
            print(f"File not found, creating new: {output_path}", file=sys.stderr)
        wb, ws = create_workbook()
        append_to_workbook(ws, analysis_data, 2)

    total_cols = len(["序号", "文件名"] + [col[1] for col in COLUMNS])
    ws.auto_filter.ref = f"A1:{get_column_letter(total_cols)}{ws.max_row}"
    wb.save(output_path)
    print(f"Excel report saved: {output_path} ({len(analysis_data)} patent(s) added)", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(description="Generate or append to Excel report")
    parser.add_argument("--input", required=True, help="Path to the JSON file")
    parser.add_argument("--output", required=True, help="Path to the output Excel file")
    parser.add_argument("--append", action="store_true", help="Append to existing file")
    args = parser.parse_args()

    if not os.path.isfile(args.input):
        print(f"Error: Input file not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    with open(args.input, "r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, dict):
        analysis_data = [data]
    elif isinstance(data, list):
        analysis_data = data
    else:
        print("Error: JSON must be an object or array", file=sys.stderr)
        sys.exit(1)

    if len(analysis_data) == 0:
        print("Error: No analysis data", file=sys.stderr)
        sys.exit(1)

    generate_excel(analysis_data, args.output, args.append)


if __name__ == "__main__":
    main()
