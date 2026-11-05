#!/usr/bin/env python3
"""
审核匹配度分析工具 - 辅助脚本

用法:
    python audit_review.py <input_file> --prompt-col <col> --explanation-col <col> --output <output_file> [--sheet <sheet_name>]

参数:
    input_file       输入Excel文件路径
    --prompt-col     审核提示列名或列索引（从0开始）
    --explanation-col 审核说明列名或列索引（从0开始）
    --output         输出文件路径
    --sheet          工作表名称（默认为第一个工作表）

示例:
    python audit_review.py data.xlsx --prompt-col "审核提示" --explanation-col "审核说明" --output result.xlsx
    python audit_review.py data.xlsx --prompt-col 4 --explanation-col 6 --output result.xlsx --sheet sheet1
"""

import argparse
import json
import sys
import re
import openpyxl
import pandas as pd
from openpyxl.utils import get_column_letter
from openpyxl.styles import Alignment, Font
from copy import copy


def extract_numbers(text):
    """从文本中提取所有数字（含小数）"""
    return [float(x) for x in re.findall(r'\d+\.?\d*', text)]


def extract_codes(text):
    """从文本中提取编码（如210111、351311等5-6位数字编码）"""
    return re.findall(r'\b\d{5,6}\b', text)


def evaluate_explanation(prompt, explanation):
    """
    评估单行审核说明是否能解释清楚审核提示（基于规则的预筛选）

    Returns:
        dict: {'is_clear': bool, 'reason': str, 'issue_types': list}
    """
    if not explanation or explanation.strip() in ['nan', '', '无', '暂无']:
        return {
            'is_clear': False,
            'reason': '审核说明为空，未对审核提示中的问题进行任何解释。',
            'issue_types': ['空说明']
        }

    issues = []
    issue_types = []

    # 检查1：数据一致性 - 提取并比对金额
    prompt_numbers = extract_numbers(prompt)
    explanation_numbers = extract_numbers(explanation)
    if prompt_numbers and explanation_numbers:
        # 找出提示中的关键金额（通常是较大的数字或限额相关的数字）
        prompt_amounts = [n for n in prompt_numbers if n > 100]
        explanation_amounts = [n for n in explanation_numbers if n > 100]
        if prompt_amounts and explanation_amounts:
            # 检查是否有金额被明确引用但数值不一致
            for pa in prompt_amounts:
                close_match = any(abs(ea - pa) / max(pa, 1) < 0.05 for ea in explanation_amounts)
                if not close_match:
                    # 可能存在不一致，但不一定有问题（可能是其他数据）
                    pass

    # 检查2：说明是否过于简略（少于15个字符）
    if len(explanation.strip()) < 15:
        issues.append(f"审核说明过于简略（仅{len(explanation.strip())}字），未充分解释问题原因。")
        issue_types.append('过于简略')

    # 检查3：是否为套话
    generic_phrases = ['情况属实', '属实', '正常', '无误', '已核实']
    if explanation.strip() in generic_phrases or explanation.strip().replace('经核实，', '') in generic_phrases:
        issues.append("审核说明仅为套话（如'情况属实'），未提供具体解释内容。")
        issue_types.append('套话')

    # 检查4：是否仅列举数据而未解释原因
    if re.search(r'(有|包含|包括|为)\s*[、，]'.join(['本子', '笔', '生活费']),
                 explanation) and '因为' not in explanation and '由于' not in explanation and '所以' not in explanation:
        if '未说明' not in issues:
            pass  # 这个检查太具体，留给LLM判断

    if issues:
        return {
            'is_clear': False,
            'reason': '；'.join(issues),
            'issue_types': issue_types
        }

    return {
        'is_clear': True,
        'reason': '',
        'issue_types': []
    }


def generate_output(wb_src, ws_src, unclear_rows, output_path):
    """生成保持原表格式的新文档"""
    wb_new = openpyxl.Workbook()
    ws_new = wb_new.active
    ws_new.title = ws_src.title

    max_col = ws_src.max_column
    new_max_col = max_col + 1

    # 复制表头
    for col in range(1, max_col + 1):
        src_cell = ws_src.cell(row=1, column=col)
        dst_cell = ws_new.cell(row=1, column=col)
        dst_cell.value = src_cell.value
        dst_cell.font = copy(src_cell.font)
        dst_cell.fill = copy(src_cell.fill)
        dst_cell.border = copy(src_cell.border)
        dst_cell.alignment = copy(src_cell.alignment)
        dst_cell.number_format = src_cell.number_format

    # 新增"研判意见"列头
    header_cell = ws_new.cell(row=1, column=new_max_col)
    header_cell.value = '研判意见'
    header_cell.font = Font(bold=True)
    header_cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)

    # 复制不清晰行
    new_row = 2
    for item in unclear_rows:
        src_row = item['row']
        for col in range(1, max_col + 1):
            src_cell = ws_src.cell(row=src_row, column=col)
            dst_cell = ws_new.cell(row=new_row, column=col)
            dst_cell.value = src_cell.value
            dst_cell.font = copy(src_cell.font)
            dst_cell.fill = copy(src_cell.fill)
            dst_cell.border = copy(src_cell.border)
            dst_cell.alignment = copy(src_cell.alignment)
            dst_cell.number_format = src_cell.number_format

        reason_cell = ws_new.cell(row=new_row, column=new_max_col)
        reason_cell.value = item['reason']
        reason_cell.alignment = Alignment(wrap_text=True, vertical='top')
        reason_cell.font = Font(color='FF0000')
        new_row += 1

    # 自动调整列宽
    for col_idx in range(1, new_max_col + 1):
        max_len = max(
            (len(str(ws_new.cell(row=r, column=col_idx).value or ''))
             for r in range(1, new_row)),
            default=0
        )
        if col_idx == new_max_col:
            width = min(max(max_len + 2, 20), 80)
        else:
            width = min(max(max_len + 2, 8), 60)
        ws_new.column_dimensions[get_column_letter(col_idx)].width = width

    # 长文本列启用自动换行
    for r in range(2, new_row):
        for col_idx in range(1, new_max_col + 1):
            cell = ws_new.cell(row=r, column=col_idx)
            if len(str(cell.value or '')) > 50:
                cell.alignment = Alignment(wrap_text=True, vertical='top')

    wb_new.save(output_path)
    return new_row - 2


def export_for_llm_analysis(file_path, sheet_name, prompt_col, explanation_col, output_json):
    """导出数据为JSON格式，供LLM分析使用"""
    df = pd.read_excel(file_path, sheet_name=sheet_name, header=None)

    if isinstance(prompt_col, str):
        prompt_idx = list(df.iloc[0]).index(prompt_col)
    else:
        prompt_idx = prompt_col
    if isinstance(explanation_col, str):
        explanation_idx = list(df.iloc[0]).index(explanation_col)
    else:
        explanation_idx = explanation_col

    rows_data = []
    for i in range(1, df.shape[0]):
        e_val = str(df.iloc[i, prompt_idx]).strip() if pd.notna(df.iloc[i, prompt_idx]) else ""
        g_val = str(df.iloc[i, explanation_idx]).strip() if pd.notna(df.iloc[i, explanation_idx]) else ""
        rows_data.append({
            "row": i + 1,
            "prompt": e_val,
            "explanation": g_val
        })

    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(rows_data, f, ensure_ascii=False, indent=2)

    return rows_data


def main():
    parser = argparse.ArgumentParser(description='审核匹配度分析工具')
    parser.add_argument('input_file', help='输入Excel文件路径')
    parser.add_argument('--prompt-col', required=True, help='审核提示列名或索引（从0开始）')
    parser.add_argument('--explanation-col', required=True, help='审核说明列名或索引（从0开始）')
    parser.add_argument('--output', required=True, help='输出文件路径')
    parser.add_argument('--sheet', default=None, help='工作表名称（默认为第一个工作表）')
    parser.add_argument('--export-json', default=None, help='导出JSON供LLM分析的路径（可选）')

    args = parser.parse_args()

    # 读取文件
    wb_src = openpyxl.load_workbook(args.input_file)
    sheet_name = args.sheet or wb_src.sheetnames[0]
    ws_src = wb_src[sheet_name]
    df = pd.read_excel(args.input_file, sheet_name=sheet_name, header=None)

    # 解析列索引
    try:
        prompt_col = int(args.prompt_col)
    except ValueError:
        prompt_col = args.prompt_col
    try:
        explanation_col = int(args.explanation_col)
    except ValueError:
        explanation_col = args.explanation_col

    if isinstance(prompt_col, str):
        prompt_idx = list(df.iloc[0]).index(prompt_col)
    else:
        prompt_idx = prompt_col
    if isinstance(explanation_col, str):
        explanation_idx = list(df.iloc[0]).index(explanation_col)
    else:
        explanation_idx = explanation_col

    print(f"审核提示列索引: {prompt_idx} ({df.iloc[0, prompt_idx]})")
    print(f"审核说明列索引: {explanation_idx} ({df.iloc[0, explanation_idx]})")
    print(f"总数据行数: {df.shape[0] - 1}")

    # 可选：导出JSON
    if args.export_json:
        rows_data = export_for_llm_analysis(args.input_file, sheet_name, prompt_col, explanation_col, args.export_json)
        print(f"已导出JSON到: {args.export_json}")

    # 基于规则的预筛选
    unclear_rows = []
    for i in range(1, df.shape[0]):
        prompt = str(df.iloc[i, prompt_idx]).strip() if pd.notna(df.iloc[i, prompt_idx]) else ""
        explanation = str(df.iloc[i, explanation_idx]).strip() if pd.notna(df.iloc[i, explanation_idx]) else ""
        result = evaluate_explanation(prompt, explanation)
        if not result['is_clear']:
            unclear_rows.append({
                'row': i + 1,
                'prompt': prompt,
                'explanation': explanation,
                'reason': result['reason'],
                'issue_types': result['issue_types']
            })

    print(f"\n基于规则预筛选发现 {len(unclear_rows)} 行可能存在问题：")
    for r in unclear_rows:
        print(f"  行{r['row']}: [{', '.join(r['issue_types'])}] {r['reason'][:60]}...")

    # 生成输出文件（如果提供了LLM分析结果的JSON）
    llm_json = args.export_json + '.analyzed' if args.export_json else None
    if llm_json:
        try:
            with open(llm_json, 'r', encoding='utf-8') as f:
                llm_results = json.load(f)
            unclear_from_llm = [r for r in llm_results if not r.get('is_clear', True)]
            print(f"\nLLM分析发现 {len(unclear_from_llm)} 行解释不清楚")
            count = generate_output(wb_src, ws_src, unclear_from_llm, args.output)
            print(f"已生成输出文件: {args.output}（共{count}行）")
        except FileNotFoundError:
            print(f"\n未找到LLM分析结果文件: {llm_json}")
            print("请先使用LLM分析导出的JSON，然后将分析结果保存为.analyzed文件")
    else:
        print(f"\n提示：使用 --export-json 导出数据后，需结合LLM进行深度语义分析。")
        print(f"基于规则的预筛选结果仅供参考，建议结合LLM分析提高准确率。")

    # 输出统计摘要
    print(f"\n===== 分析摘要 =====")
    print(f"总行数: {df.shape[0] - 1}")
    print(f"规则预筛选不清晰行数: {len(unclear_rows)}")
    issue_type_count = {}
    for r in unclear_rows:
        for t in r['issue_types']:
            issue_type_count[t] = issue_type_count.get(t, 0) + 1
    if issue_type_count:
        print(f"问题类型分布:")
        for t, c in sorted(issue_type_count.items(), key=lambda x: -x[1]):
            print(f"  {t}: {c}行")


if __name__ == '__main__':
    main()
