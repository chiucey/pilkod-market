#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
来函文档提取器 - 最终修复版
修复doc2单位识别和部门格式扩展问题
"""

import os
import re
import sys
from datetime import datetime
from dataclasses import dataclass
from bs4 import BeautifulSoup
import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side


# 分解单位枚举值
UNIT_MAPPINGS = {
    "武汉公司": ["武汉公司", "国网武汉供电公司", "武汉供电公司"],
    "黄石公司": ["黄石公司", "国网黄石供电公司", "黄石供电公司"],
    "十堰公司": ["十堰公司", "国网十堰供电公司", "十堰供电公司"],
    "襄阳公司": ["襄阳公司", "国网襄阳供电公司", "襄阳供电公司"],
    "黄冈公司": ["黄冈公司", "国网黄冈供电公司", "黄冈供电公司"],
    "鄂州公司": ["鄂州公司", "国网鄂州供电公司", "鄂州供电公司"],
    "荆门公司": ["荆门公司", "国网荆门供电公司", "荆门供电公司"],
    "宜昌公司": ["宜昌公司", "国网宜昌供电公司", "宜昌供电公司"],
    "荆州公司": ["荆州公司", "国网荆州供电公司", "荆州供电公司"],
    "孝感公司": ["孝感公司", "国网孝感供电公司", "孝感供电公司"],
    "咸宁公司": ["咸宁公司", "国网咸宁供电公司", "咸宁供电公司"],
    "随州公司": ["随州公司", "国网随州供电公司", "随州供电公司"],
    "神农架公司": ["神农架公司", "国网神农架供电公司", "神农架供电公司"],
    "恩施公司": ["恩施公司", "国网恩施供电公司", "恩施供电公司"],
    "黄龙滩水电厂": ["黄龙滩水电厂", "黄龙滩电厂", "国网湖北黄龙滩电厂", "国网湖北黄龙滩水电厂"],
    "超高压公司": ["超高压公司", "国网湖北超高压公司"],
    "直流运检公司": ["直流运检公司", "直流公司", "国网湖北直流公司"],
    "信通公司": ["信通公司", "国网湖北信通公司", "国网湖北信通公司（数据中心）"],
    "电科院": ["电科院", "国网湖北电科院"],
    "营销服务中心": ["营销服务中心", "国网湖北营销中心", "营销中心", "计量中心", "国网湖北营销中心（计量中心）"],
    "后勤服务中心": ["后勤服务中心", "后勤中心", "国网湖北后勤中心"],
    "经研院": ["经研院", "国网湖北经研院", "经济技术研究院"],
    "中超公司": ["中超公司", "国网湖北中超公司", "中超建设管理公司", "国网湖北省电力有限公司中超建设管理公司"],
    "技培中心": ["技培中心", "国网湖北技培中心", "技培中心（武汉电院）", "国网湖北技培中心（武汉电院）"],
}

REVERSE_MAPPING = {}
for enum_val, variants in UNIT_MAPPINGS.items():
    for variant in variants:
        REVERSE_MAPPING[variant] = enum_val


@dataclass
class LetterDetail:
    来函部门: str = ""
    包项目名称: str = ""
    分解单位: str = ""
    来函分解金额万元: str = ""
    数据来源: str = ""
    备注: str = ""


@dataclass
class FuzzyMatchRecord:
    原始文本: str = ""
    匹配结果: str = ""
    匹配度: float = 0.0
    需确认: bool = False


def clean_text(text: str) -> str:
    text = re.sub(r'</?div[^>]*>', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def extract_department(content: str) -> str:
    """提取来函部门，支持多种格式：XX部、XX办、XX中心、XX会、XX联、办公室等"""
    # 部、办、中心、会、联、指挥部等结尾的部门
    patterns = [
        r'公司([^\s公司]{2,8}(?:部|办|中心|会|联|办公室|指挥部))',  # 国网XX公司XX部
    ]

    for pattern in patterns:
        match = re.search(pattern, content)
        if match:
            dept = match.group(1)
            # 确保以部/办/中心等结尾
            if dept.endswith(('部', '办', '中心', '会', '联')):
                return dept
            elif '办公室' in dept:
                return '办公室'

    return "未知部门"


def match_unit(text: str, fuzzy_records: list) -> str:
    """匹配单位到枚举值"""
    if not text:
        return None
    for variant, enum_val in REVERSE_MAPPING.items():
        if variant in text:
            if variant != enum_val:
                fuzzy_records.append(FuzzyMatchRecord(
                    原始文本=variant,
                    匹配结果=enum_val,
                    匹配度=0.95,
                    需确认=False
                ))
            return enum_val
    return None


def parse_table_rows(table_html: str) -> list:
    """解析表格为行列表"""
    soup = BeautifulSoup(table_html, 'lxml')
    rows = soup.find_all('tr')
    result = []
    for row in rows:
        cells = [td.get_text(strip=True) for td in row.find_all(['td', 'th'])]
        if cells:
            result.append(cells)
    return result


def extract_details_doc1(content: str, filename: str) -> tuple:
    """第一个文档格式：项目名称在前，单位在表格列"""
    details = []
    fuzzy_records = []

    content = clean_text(content)

    # 提取来函部门
    dept_name = extract_department(content)

    # 分割内容为项目section - 按"## 2025年专项成本分解明细表"分割
    sections = re.split(r'(?=##\s*2025\s*年\s*专项成本分解明细表)', content)

    current_project = ""

    for section in sections:
        section = section.strip()
        if not section:
            continue

        # 检查是否是项目名称section
        project_match = re.search(r'项目名称[：:]\s*([^\n<]+)', section)
        if project_match:
            current_project = clean_text(project_match.group(1))

        if not current_project:
            continue

        # 提取所有表格
        all_tables_html = re.findall(r'<table>.*?</table>', section, re.DOTALL)

        # 处理所有数据行
        for table_html in all_tables_html:
            rows = parse_table_rows(table_html)

            for cells in rows:
                if not cells:
                    continue

                first_cell = cells[0]

                # 跳过表头行
                if '序号' in first_cell or '单位' in first_cell:
                    continue

                # 跳过合计行
                if '合计' in first_cell:
                    continue

                # 跳过非数字序号
                if not first_cell.isdigit():
                    continue

                # 查找单位和金额
                unit_text = ""
                amount_text = ""

                for idx, cell in enumerate(cells):
                    cell_clean = clean_text(cell)

                    # 匹配单位
                    if not unit_text:
                        matched = match_unit(cell_clean, fuzzy_records)
                        if matched:
                            unit_text = cell_clean
                            # 金额可能在同一列的下一格
                            if idx + 1 < len(cells):
                                next_cell = clean_text(cells[idx + 1])
                                m = re.search(r'^(\d+(?:,\d{3})*(?:\.\d+)?)$', next_cell)
                                if m:
                                    amount_text = next_cell
                            break

                    # 如果还没找到金额，查找数字列
                    if not amount_text:
                        m = re.search(r'^(\d+(?:,\d{3})*(?:\.\d+)?)$', cell_clean)
                        if m:
                            amount_text = cell_clean

                # 匹配单位
                matched_unit = match_unit(unit_text, fuzzy_records) if unit_text else None

                # 提取金额
                if matched_unit and amount_text:
                    amount_match = re.search(r'^(\d+(?:,\d{3})*(?:\.\d+)?)$', amount_text)
                    if amount_match:
                        amount = amount_match.group(1).replace(',', '')
                        try:
                            amount_val = float(amount)
                            if 0.1 <= amount_val <= 2000:
                                details.append(LetterDetail(
                                    来函部门=dept_name,
                                    包项目名称=current_project[:200] if current_project else "",
                                    分解单位=matched_unit,
                                    来函分解金额万元=amount,
                                    数据来源=filename,
                                    备注=""
                                ))
                        except ValueError:
                            pass

    return details, fuzzy_records


def extract_details_doc2(content: str, filename: str) -> tuple:
    """第二个文档格式：单位名称在前，每个单位对应自己的表格"""
    details = []
    fuzzy_records = []

    content = clean_text(content)

    # 提取来函部门
    dept_name = extract_department(content)

    # 分割内容为单位section - 按"## 单位名称"分割
    parts = re.split(r'(?=##\s*单位名称)', content)

    for part in parts:
        if not part.strip():
            continue

        # 提取当前section的单位名称
        unit_match = re.search(r'单位名称[：:]\s*([^\n<]+)', part)
        if not unit_match:
            continue

        unit_text = clean_text(unit_match.group(1))
        matched_unit = match_unit(unit_text, fuzzy_records)

        if not matched_unit:
            continue

        # 提取该单位下的所有表格并合并处理
        tables = re.findall(r'<table>.*?</table>', part, re.DOTALL)

        # 收集所有行并预处理：合并被截断的项目名称
        all_rows = []
        for table_html in tables:
            rows = parse_table_rows(table_html)
            all_rows.extend(rows)

        # 预处理：合并被截断的项目名称
        merged_rows = []
        i = 0
        while i < len(all_rows):
            cells = all_rows[i]
            if not cells:
                i += 1
                continue

            first_cell = cells[0]
            second_cell = cells[1] if len(cells) > 1 else ""

            # 跳过表头行
            if '序号' in first_cell and ('单位' in second_cell or '项目' in second_cell):
                i += 1
                continue

            # 跳过合计行
            if '合计' in first_cell:
                i += 1
                continue

            # 跳过页码行
            if re.match(r'^\d+\.$', first_cell):
                i += 1
                continue

            # 检查是否是续接行（序号为空但有项目文本）
            if not first_cell and second_cell:
                suffix = second_cell.strip()
                if suffix:
                    # 追加到上一行的项目名称
                    if merged_rows and '序号' not in merged_rows[-1][0]:
                        merged_rows[-1][1] = merged_rows[-1][1] + suffix
                        merged_rows[-1][1] = merged_rows[-1][1][:200]  # 限制长度
                i += 1
                continue

            # 数字序号行，加入merged_rows
            if first_cell.isdigit():
                # 提取项目名称（列2）
                project_name = cells[1][:100] if len(cells) > 1 and cells[1] else ""
                merged_rows.append([first_cell, project_name] + cells[2:])
            i += 1

        # 处理合并后的行
        for cells in merged_rows:
            if not cells:
                continue

            first_cell = cells[0]
            project_name = cells[1] if len(cells) > 1 else ""

            # 跳过表头（如果还有）
            if '序号' in first_cell:
                continue

            # 提取金额（列3，即cells[2]）
            if len(cells) > 2:
                amount_text = clean_text(cells[2])
                amount_match = re.search(r'^(\d+(?:,\d{3})*(?:\.\d+)?)$', amount_text)
                if amount_match:
                    amount = amount_match.group(1).replace(',', '')
                    try:
                        amount_val = float(amount)
                        if 0.1 <= amount_val <= 2000 and project_name:
                            details.append(LetterDetail(
                                来函部门=dept_name,
                                包项目名称=project_name,
                                分解单位=matched_unit,
                                来函分解金额万元=amount,
                                数据来源=filename,
                                备注=""
                            ))
                    except ValueError:
                        pass

    return details, fuzzy_records


def save_to_excel(details: list, fuzzy_records: list, output_path: str):
    """保存到Excel"""
    wb = openpyxl.Workbook()

    header_font = Font(bold=True, color="FFFFFF")
    header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
    thin_border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )

    # Sheet1: 来函明细
    ws1 = wb.active
    ws1.title = "来函明细"

    headers1 = ["来函部门", "包项目名称", "分解单位", "来函分解金额(万元)", "数据来源", "备注"]
    for col, header in enumerate(headers1, 1):
        cell = ws1.cell(row=1, column=col, value=header)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.border = thin_border

    for row_idx, detail in enumerate(details, 2):
        row_data = [
            detail.来函部门 or "",
            detail.包项目名称 or "",
            detail.分解单位 or "",
            detail.来函分解金额万元 or "",
            detail.数据来源 or "",
            detail.备注 or ""
        ]
        for col, value in enumerate(row_data, 1):
            cell = ws1.cell(row=row_idx, column=col, value=value)
            cell.border = thin_border
            cell.alignment = Alignment(vertical="center", wrap_text=True)

    ws1.column_dimensions['A'].width = 12
    ws1.column_dimensions['B'].width = 70
    ws1.column_dimensions['C'].width = 15
    ws1.column_dimensions['D'].width = 18
    ws1.column_dimensions['E'].width = 45
    ws1.column_dimensions['F'].width = 30

    # Sheet2: 来函汇总
    ws2 = wb.create_sheet("来函汇总")

    headers2 = ["来函部门", "来函单位", "项目数量", "总金额(万元)"]
    for col, header in enumerate(headers2, 1):
        cell = ws2.cell(row=1, column=col, value=header)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.border = thin_border

    summary_dict = {}
    for detail in details:
        if not detail.分解单位:
            continue
        key = (detail.来函部门 or "", detail.分解单位)
        if key not in summary_dict:
            summary_dict[key] = {
                "来函部门": detail.来函部门 or "",
                "来函单位": detail.分解单位,
                "项目数量": 0,
                "总金额万元": 0.0
            }
        try:
            amount = float(detail.来函分解金额万元) if detail.来函分解金额万元 else 0
            summary_dict[key]["总金额万元"] += amount
            summary_dict[key]["项目数量"] += 1
        except ValueError:
            pass

    for row_idx, summary in enumerate(summary_dict.values(), 2):
        row_data = [
            summary["来函部门"],
            summary["来函单位"],
            summary["项目数量"],
            round(summary["总金额万元"], 2)
        ]
        for col, value in enumerate(row_data, 1):
            cell = ws2.cell(row=row_idx, column=col, value=value)
            cell.border = thin_border
            cell.alignment = Alignment(horizontal="center" if col > 2 else "left", vertical="center")

    ws2.column_dimensions['A'].width = 12
    ws2.column_dimensions['B'].width = 15
    ws2.column_dimensions['C'].width = 12
    ws2.column_dimensions['D'].width = 18

    # Sheet3: 模糊匹配清单
    ws3 = wb.create_sheet("模糊匹配清单")

    headers3 = ["原始文本", "匹配结果", "匹配度", "需确认"]
    for col, header in enumerate(headers3, 1):
        cell = ws3.cell(row=1, column=col, value=header)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.border = thin_border

    seen = set()
    for record in fuzzy_records:
        key = (record.原始文本, record.匹配结果)
        if key not in seen:
            seen.add(key)
            row_data = [
                record.原始文本,
                record.匹配结果,
                f"{record.匹配度:.0%}",
                "是" if record.需确认 else "否"
            ]
            row_idx = ws3.max_row + 1
            for col, value in enumerate(row_data, 1):
                cell = ws3.cell(row=row_idx, column=col, value=value)
                cell.border = thin_border
                cell.alignment = Alignment(horizontal="center", vertical="center")

    ws3.column_dimensions['A'].width = 30
    ws3.column_dimensions['B'].width = 15
    ws3.column_dimensions['C'].width = 12
    ws3.column_dimensions['D'].width = 10

    wb.save(output_path)
    print(f"已保存: {output_path}")


def main(folder_path: str):
    output_path = folder_path

    # 查找PDF文件
    pdf_files = [
        f for f in os.listdir(folder_path)
        if f.endswith('.pdf') and not f.startswith('~')
    ]

    if not pdf_files:
        print(f"在 {folder_path} 中未找到PDF文件")
        return

    # 查找提取好的markdown文件
    md_files = {}
    for f in os.listdir('/workspace/extract'):
        if f.endswith('.md'):
            # 提取原始PDF名
            base = f.split('_')[0]
            if base not in md_files:
                md_files[base] = os.path.join('/workspace/extract', f)

    all_details = []
    all_fuzzy_records = []
    total_amount = 0

    for pdf_file in sorted(pdf_files):
        print(f"处理: {pdf_file}")

        # 查找对应的markdown文件
        pdf_base = pdf_file.replace('.pdf', '')
        md_path = md_files.get(pdf_base)

        if not md_path:
            print(f"  未找到对应的提取文件，跳过")
            continue

        content = open(md_path, 'r', encoding='utf-8').read()

        # 判断文档类型 - doc2有"## 单位名称"作为section分隔
        if '## 单位名称' in content:
            extractor = extract_details_doc2
            print(f"  识别为: doc2格式（单位在前）")
        else:
            extractor = extract_details_doc1
            print(f"  识别为: doc1格式（项目在前）")

        details, fuzzy_records = extractor(content, pdf_file)

        file_amount = sum(float(d.来函分解金额万元) for d in details if d.来函分解金额万元)
        print(f"  - 提取到 {len(details)} 条明细记录，金额合计 {file_amount:.2f} 万元")

        all_details.extend(details)
        all_fuzzy_records.extend(fuzzy_records)
        total_amount += file_amount

    print(f"\n总计: {len(all_details)} 条记录，金额合计 {total_amount:.2f} 万元")

    # 去重
    unique_details = []
    seen = set()
    for d in all_details:
        key = (d.来函部门, d.包项目名称, d.分解单位, d.来函分解金额万元)
        if key not in seen:
            seen.add(key)
            unique_details.append(d)

    print(f"去重后: {len(unique_details)} 条记录")

    date_str = datetime.now().strftime("%Y%m%d")
    detail_file = os.path.join(output_path, f"来函明细统计表_{date_str}.xlsx")
    save_to_excel(unique_details, all_fuzzy_records, detail_file)

    print(f"\n处理完成!")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        folder_path = sys.argv[1]
    else:
        folder_path = "/workspace/test_letters"
    main(folder_path)
