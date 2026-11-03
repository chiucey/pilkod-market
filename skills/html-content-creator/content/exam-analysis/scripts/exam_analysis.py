#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
班级多批次成绩全量分析与可视化
支持上传最多20个Excel文件，生成交互式HTML报告
"""

import argparse
import json
import re
from datetime import datetime
from pathlib import Path


def _ensure_deps():
    """检查并自动安装依赖（pandas, openpyxl）"""
    try:
        import pandas  # noqa
    except ImportError:
        import subprocess
        import sys
        print("正在安装依赖 pandas 和 openpyxl...")
        r = subprocess.run(
            [sys.executable, '-m', 'pip', 'install', 'pandas', 'openpyxl'],
            capture_output=True, text=True
        )
        if r.returncode != 0:
            print("=" * 50)
            print("依赖安装失败！请手动执行：")
            print("  pip install pandas openpyxl")
            print("错误信息：")
            print(r.stderr)
            print("=" * 50)
            sys.exit(1)
        print("依赖安装成功。")


_ensure_deps()
import pandas as pd


def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description='班级多批次成绩全量分析与可视化报告生成'
    )
    parser.add_argument(
        '--input-dir',
        required=True,
        help='包含Excel文件的目录路径'
    )
    parser.add_argument(
        '--output',
        default='output.html',
        help='输出HTML报告文件路径(默认:output.html)'
    )
    parser.add_argument(
        '--exam-order',
        default='',
        help='考试顺序，逗号分隔的考试名称，如"考试1,考试2,考试3"'
    )
    parser.add_argument(
        '--filter',
        default='',
        help='文件名筛选关键字（如 "班级1"），仅处理文件名包含该关键字的文件'
    )
    return parser.parse_args()


def find_excel_files(directory, filter_keyword=''):
    """查找目录中的所有Excel文件，可选按文件名关键字筛选"""
    directory = Path(directory)
    if not directory.exists():
        raise FileNotFoundError(f"目录不存在: {directory}")

    excel_files = []
    for pattern in ['*.xlsx', '*.xls']:
        excel_files.extend(directory.glob(pattern))
    # 排除Excel临时文件(~$开头)
    excel_files = [f for f in excel_files if not f.name.startswith('~$')]

    # 按关键字筛选
    if filter_keyword:
        excel_files = [f for f in excel_files if filter_keyword in f.name or filter_keyword in f.stem]

    if not excel_files:
        raise ValueError(f"目录中未找到Excel文件 (filter={filter_keyword}): {directory}")
    if len(excel_files) > 20:
        raise ValueError(f"Excel文件数量超过20个限制(当前:{len(excel_files)})")

    return excel_files


def extract_exam_time_from_filename(filename):
    """从文件名中提取考试时间"""
    patterns = [
        r'(\d{4})[年\-_](\d{1,2})[月\-_](\d{1,2})',
        r'(\d{4})(\d{2})(\d{2})',
        r'(\d{4})[年\-_](\d{1,2})',
    ]

    for i, pattern in enumerate(patterns):
        match = re.search(pattern, filename)
        if match:
            year = int(match.group(1))
            month = int(match.group(2))
            day = int(match.group(3)) if len(match.groups()) >= 3 else 1
            return datetime(year, month, day)

    return None


def get_pinyin_sort_key(name):
    """获取姓名的拼音排序键"""
    # 简单的拼音转换表（常用姓氏）
    pinyin_map = {
        '张': 'zhang', '李': 'li', '王': 'wang', '刘': 'liu', '陈': 'chen',
        '杨': 'yang', '黄': 'huang', '赵': 'zhao', '周': 'zhou', '吴': 'wu',
        '徐': 'xu', '孙': 'sun', '马': 'ma', '朱': 'zhu', '胡': 'hu',
        '郭': 'guo', '林': 'lin', '何': 'he', '罗': 'luo', '梁': 'liang',
        '宋': 'song', '唐': 'tang', '许': 'xu', '韩': 'han', '冯': 'feng',
        '董': 'dong', '萧': 'xiao', '程': 'cheng', '曹': 'cao', '袁': 'yuan',
        '邓': 'deng', '任': 'ren', '彭': 'peng', '鲁': 'lu', '卫': 'wei',
        '蒋': 'jiang', '蔡': 'cai', '魏': 'wei', '丁': 'ding', '潘': 'pan',
    }
    if not name:
        return 'zzz'
    first_char = name[0]
    pinyin = pinyin_map.get(first_char, first_char)
    return pinyin + name


def sort_exam_files_by_time(excel_files, exam_order=''):
    """
    按时间排序考试文件
    如果无法确定时间，返回None并在后续询问用户
    """
    exam_times = {}
    unclear_files = []

    # 如果指定了顺序，按顺序匹配文件名关键字
    if exam_order:
        order_names = [s.strip() for s in exam_order.split(',')]
        ordered_files = []
        remaining = list(excel_files)
        for name_key in order_names:
            matched = None
            for f in remaining:
                if name_key in f.stem or name_key in f.name:
                    matched = f
                    break
            if matched:
                ordered_files.append(matched)
                remaining.remove(matched)
        # 追加未匹配的文件
        ordered_files.extend(remaining)
        return ordered_files, []

    for f in excel_files:
        time_info = extract_exam_time_from_filename(f.name)
        if time_info:
            exam_times[f] = time_info
        else:
            unclear_files.append(f)

    # 如果有无法确定时间的文件
    if unclear_files:
        return None, unclear_files

    # 按时间排序
    sorted_files = sorted(excel_files, key=lambda x: exam_times[x])
    return sorted_files, []


def is_valid_student_name(name):
    """判断是否为有效学生姓名"""
    if not name or pd.isna(name):
        return False
    name_str = str(name).strip()
    if name_str in ['nan', '缺考', 'None', '', '姓名', '学生名']:
        return False
    if len(name_str) < 2 or len(name_str) > 20:
        return False
    return True


def normalize_column_name(col):
    """标准化列名"""
    if pd.isna(col):
        return ''
    return str(col).strip().lower()


def match_subject_columns(columns):
    """
    智能匹配科目列名
    
    列识别规则（严格从左到右交替识别）:
    1. 姓名列：单元格内容精确为 "姓名"
    2. 语数英总分列：单元格内容精确为 "语数英总分" 或 "语数英"
    3. 总分列：单元格内容精确为 "总分" 或 "赋分总分"
    4. 科目分数列：单元格内容精确为科目名称（语文/数学/英语/物理/化学/生物/历史/地理/政治/技术）
    5. 排名列：单元格内容为 "排序"/"校序"/"mc"/"XXmc"/"名次"/"赋分名次" 时，
       识别为前一列分数项目的排名列。"赋分名次" 仅当前一列为 "总分" 列时有效。
    6. 不匹配任何上述规则的列自动跳过。
    7. 严格按 分数列→排名列→分数列→排名列 交替顺序识别，找不到则跳过对应分析。
    """
    # 分数列名（精确匹配）
    score_columns = {
        '姓名': 'name',
        '语数英总分': 'three_total',
        '语数英': 'three_total',
        '总分': 'total',
        '赋分总分': 'total',
        '语文': 'subject',
        '数学': 'subject',
        '英语': 'subject',
        '物理': 'subject',
        '化学': 'subject',
        '生物': 'subject',
        '历史': 'subject',
        '地理': 'subject',
        '政治': 'subject',
        '技术': 'subject',
    }

    # 排名列名（精确匹配）
    rank_names = {'排序', '校序', 'mc', '名次', '赋分名次'}

    actual_columns = [str(c).strip() for c in columns]
    original_columns = list(columns)

    matched = {
        'name': None,        # 列索引
        'total': None,       # 列索引
        'total_rank': None,  # 列索引
        'three_total': None, # 列索引
        'three_total_rank': None,  # 列索引
        'subjects': {},      # {科目名: {'score': 列索引, 'rank': 列索引}}
    }

    # 从左到右逐列扫描，严格交替识别
    last_score_subject = None  # 上一个分数列对应的类型（'total', 'three_total', 科目名等）
    last_score_index = None    # 上一个分数列的索引，用于 XXmc 检测

    for i, col in enumerate(actual_columns):
        col_stripped = col.strip()
        # 存储原始列名用于 XXmc 后缀匹配（完整列名，如 "语文"）
        orig_name = original_columns[i]

        # ---- 第1步：检查是否是分数列 ----
        if col_stripped in score_columns:
            col_type = score_columns[col_stripped]
            if col_type == 'name':
                if matched['name'] is None:
                    matched['name'] = i
                last_score_subject = None
                last_score_index = None
            elif col_type == 'three_total':
                if matched['three_total'] is None:
                    matched['three_total'] = i
                last_score_subject = 'three_total'
                last_score_index = i
            elif col_type == 'total':
                if matched['total'] is None:
                    matched['total'] = i
                last_score_subject = 'total'
                last_score_index = i
            elif col_type == 'subject':
                subj = col_stripped
                if subj not in matched['subjects']:
                    matched['subjects'][subj] = {'score': i, 'rank': None}
                last_score_subject = subj
                last_score_index = i
            continue

        # ---- 第2步：检查是否是排名列 ----
        is_rank = False

        # 2a. 匹配排名关键词（含 pandas 自动去重后缀如 mc.1, 排序.2 等）
        for kw in rank_names:
            if col_stripped == kw or col_stripped.startswith(kw + '.'):
                is_rank = True
                break


        # 2b. XXmc模式：列名 = 上一分数列名 + "mc"（如"语文mc"）
        if not is_rank and col_stripped.endswith('mc') and last_score_index is not None:
            prefix = col_stripped[:-2]
            prev_name = original_columns[last_score_index]
            if prefix == prev_name:
                is_rank = True

        # 2c. XX校序模式：列名 = 上一分数列名 + "校序"（如"语文校序"）
        if not is_rank and col_stripped.endswith('校序') and last_score_index is not None:
            prefix = col_stripped[:-2]
            prev_name = original_columns[last_score_index]
            if prefix == prev_name:
                is_rank = True

        # 2d. XX排序模式：列名 = 上一分数列名 + "排序"（如"语文排序"）
        if not is_rank and col_stripped.endswith('排序') and last_score_index is not None:
            if len(col_stripped) > 2:  # 避免将纯"排序"双重匹配
                prefix = col_stripped[:-2]
                prev_name = original_columns[last_score_index]
                if prefix == prev_name:
                    is_rank = True

        if is_rank:
            # "赋分名次" 仅当前一列为总分列时有效
            if col_stripped == '赋分名次' and last_score_subject != 'total':
                continue

            # 将排名关联到上一个分数列
            if last_score_subject is not None:
                if last_score_subject == 'total':
                    if matched['total_rank'] is None:
                        matched['total_rank'] = i
                elif last_score_subject == 'three_total':
                    if matched['three_total_rank'] is None:
                        matched['three_total_rank'] = i
                elif last_score_subject in matched['subjects']:
                    if matched['subjects'][last_score_subject]['rank'] is None:
                        matched['subjects'][last_score_subject]['rank'] = i
            # 消耗上一个分数列
            last_score_subject = None
            last_score_index = None
            continue

        # ---- 第3步：不匹配任何规则，跳过 ----

    return matched


def parse_exam_file(file_path, exam_index):
    """解析单个考试文件"""
    try:
        df_raw = pd.read_excel(file_path, header=None, engine='openpyxl', nrows=2)

        header_row = 0
        for i in range(min(2, len(df_raw))):
            row_values = [str(v) for v in df_raw.iloc[i]]
            row_str = ' '.join(row_values).lower()
            keywords = ['姓名', '总分', '名次', '语文', '数学', '英语']
            if any(kw in row_str for kw in keywords):
                header_row = i
                break

        df = pd.read_excel(file_path, header=header_row, engine='openpyxl')
        df.columns = df.columns.astype(str).str.strip()
        df = df.dropna(how='all')

        column_mapping = match_subject_columns(df.columns)

        exam_name = Path(file_path).stem
        time_info = extract_exam_time_from_filename(exam_name)
        if time_info:
            exam_display_name = time_info.strftime('%Y年%m月') + '考试'
        else:
            # 从文件名提取月份（如 "10月考试——班级1" → "10月考试——班级1"）
            exam_display_name = exam_name

        students = []
        name_col = column_mapping['name']

        if name_col is None:
            raise ValueError(f"无法识别的学生姓名列: {df.columns.tolist()}")

        for _, row in df.iterrows():
            name = row.iloc[name_col] if name_col is not None else None
            if not is_valid_student_name(name):
                continue

            name = str(name).strip()
            student_data = {
                'name': name,
                'exam_index': exam_index,
                'exam_name': exam_display_name,
                'total_score': None,
                'total_rank': None,
                'three_total': None,
                'three_total_rank': None,
                'subjects': {}
            }

            if column_mapping['total'] is not None:
                val = row.iloc[column_mapping['total']]
                if pd.notna(val):
                    try:
                        student_data['total_score'] = float(val)
                    except (ValueError, TypeError):
                        pass

            if column_mapping['total_rank'] is not None:
                val = row.iloc[column_mapping['total_rank']]
                if pd.notna(val):
                    try:
                        student_data['total_rank'] = int(float(val))
                    except (ValueError, TypeError):
                        pass

            # 优先从直接列读取语数英总分
            if column_mapping.get('three_total') is not None:
                val = row.iloc[column_mapping['three_total']]
                if pd.notna(val):
                    try:
                        student_data['three_total'] = float(val)
                    except (ValueError, TypeError):
                        pass

            # 读取语数英总分排名
            if column_mapping.get('three_total_rank') is not None:
                val = row.iloc[column_mapping['three_total_rank']]
                if pd.notna(val):
                    try:
                        student_data['three_total_rank'] = int(float(val))
                    except (ValueError, TypeError):
                        pass

            # 读取各科目成绩
            subject_scores = []
            for subj, cols in column_mapping['subjects'].items():
                score_idx = cols['score']
                if score_idx is not None:
                    score_val = row.iloc[score_idx]
                    if pd.notna(score_val):
                        try:
                            score = float(score_val)
                            student_data['subjects'][subj] = score
                            if subj in ['语文', '数学', '英语']:
                                subject_scores.append(score)
                        except (ValueError, TypeError):
                            pass

            # 从语数英计算语数英总分（仅当未从直接列读取到）
            if student_data['three_total'] is None and len(subject_scores) == 3:
                student_data['three_total'] = sum(subject_scores)

            students.append(student_data)

        return {
            'exam_index': exam_index,
            'exam_name': exam_display_name,
            'file_name': Path(file_path).name,
            'students': students,
            'all_subjects': list(column_mapping['subjects'].keys())
        }

    except Exception as e:
        raise Exception(f"解析文件失败 {file_path}: {str(e)}")


def calculate_all_exams_statistics(exams_data):
    """计算所有考试的统计数据"""
    all_stats = []

    for exam in exams_data:
        exam_index = exam['exam_index']
        prev_exam = exams_data[exam_index - 1] if exam_index > 0 else None
        stats = calculate_single_exam_stats(exam, prev_exam)
        all_stats.append({
            'exam_index': exam_index,
            'exam_name': exam['exam_name'],
            'stats': stats
        })

    return all_stats


def calculate_single_exam_stats(exam_data, prev_exam_data=None):
    """计算单次考试的统计数据"""
    students = exam_data['students']
    if not students:
        return []

    df = pd.DataFrame(students)

    # 判断语数英总分是否有 Excel 排名列
    has_excel_three_total_rank = (
        'three_total_rank' in df.columns and df['three_total_rank'].notna().any()
    )

    tables = []

    # ---- 表格1: 总分前50名 ----
    if df['total_rank'].notna().any():
        top50 = df[df['total_rank'].notna() & (df['total_rank'] <= 50)].copy()
        top50 = top50.sort_values('total_rank')
        tables.append({
            'id': 'total_top50',
            'name': '总分前50名',
            'headers': ['姓名', '总分', '名次'],
            'rows': [[r['name'], r['total_score'], r['total_rank']] for _, r in top50.iterrows()]
        })

    # ---- 表格2: 语数英总分前50名 ----
    if 'three_total' in df.columns and df['three_total'].notna().any():
        if has_excel_three_total_rank:
            # 有 Excel 排名列：按排名排序
            top50 = df[df['three_total_rank'].notna() & (df['three_total_rank'] <= 50)].copy()
            top50 = top50.sort_values('three_total_rank')
            tables.append({
                'id': 'three_top50',
                'name': '语数英总分前50名',
                'headers': ['姓名', '语数英总分', '名次'],
                'rows': [[r['name'], r['three_total'], r['three_total_rank']] for _, r in top50.iterrows()]
            })
        else:
            # 无 Excel 排名列：按总分排序取前50，不展示名次
            top50 = df[df['three_total'].notna()].sort_values('three_total', ascending=False).head(50)
            tables.append({
                'id': 'three_top50',
                'name': '语数英总分前50名',
                'headers': ['姓名', '语数英总分'],
                'rows': [[r['name'], r['three_total']] for _, r in top50.iterrows()]
            })

    # ---- 表格3-5: 语数英110分以上（不展示排名列） ----
    for name in ['语文', '数学', '英语']:
        mask = df['subjects'].apply(lambda x: x.get(name, 0) >= 110 if isinstance(x, dict) else False)
        high_score = df[mask].copy()
        if len(high_score) > 0:
            high_score['temp_score'] = high_score['subjects'].apply(lambda x: x.get(name, 0) if isinstance(x, dict) else 0)
            high_score = high_score.sort_values('temp_score', ascending=False)
            tables.append({
                'id': f'{name}_110',
                'name': f'{name}110分以上',
                'headers': ['姓名', f'{name}成绩'],
                'rows': [[r['name'], r['subjects'].get(name, '-')] for _, r in high_score.iterrows()]
            })

    # ---- 表格6-12: 选科90分以上（固定顺序，不展示排名列） ----
    elective_order = ['物理', '化学', '生物', '政治', '历史', '地理', '技术']
    subject_90_tables = {}
    for _, row in df.iterrows():
        subjects = row.get('subjects', {})
        if isinstance(subjects, dict):
            for subj, score in subjects.items():
                if subj in ['语文', '数学', '英语']:
                    continue
                if score is not None and score >= 90:
                    if subj not in subject_90_tables:
                        subject_90_tables[subj] = []
                    subject_90_tables[subj].append({
                        'name': row['name'],
                        'score': score,
                    })

    for subj in elective_order:
        if subj in subject_90_tables:
            records = sorted(subject_90_tables[subj], key=lambda x: x['score'], reverse=True)
            tables.append({
                'id': f'{subj}_90',
                'name': f'{subj}90分以上',
                'headers': ['姓名', f'{subj}成绩'],
                'rows': [[r['name'], r['score']] for r in records]
            })

    # ---- 表格13: 总分进步大于50名(仅非首次考试，新增"上次总分") ----
    if prev_exam_data:
        prev_students = {s['name']: s for s in prev_exam_data['students']}
        improved = []

        for _, row in df.iterrows():
            name = row['name']
            if name in prev_students and row['total_rank'] is not None:
                prev_rank = prev_students[name].get('total_rank')
                if prev_rank is not None:
                    progress = prev_rank - row['total_rank']
                    if progress > 50:
                        improved.append({
                            'name': name,
                            'progress': progress,
                            'prev_rank': prev_rank,
                            'curr_rank': row['total_rank'],
                            'prev_score': prev_students[name].get('total_score'),
                            'curr_score': row['total_score'],
                        })

        improved = sorted(improved, key=lambda x: x['progress'], reverse=True)
        if improved:
            tables.append({
                'id': 'improved',
                'name': '总分进步大于50名',
                'headers': ['姓名', '进步名次', '上次名次', '本次名次', '上次总分', '本次总分'],
                'rows': [[r['name'], r['progress'], r['prev_rank'], r['curr_rank'],
                          r['prev_score'], r['curr_score']] for r in improved]
            })

    return tables


def read_charts_js():
    """读取charts.js文件内容"""
    js_path = Path(__file__).parent / 'charts.js'
    with open(js_path, 'r', encoding='utf-8') as f:
        return f.read()


def read_chart_lib():
    """读取本地 chart.umd.min.js 并返回内嵌 script 标签"""
    js_path = Path(__file__).parent / 'chart.umd.min.js'
    with open(js_path, 'r', encoding='utf-8') as f:
        return f'<script>{f.read()}</script>'


def generate_html_report(exams_data, output_path):
    """生成HTML报告"""
    num_exams = len(exams_data)

    # 收集所有学生
    all_students = {}
    for exam in exams_data:
        for student in exam['students']:
            if student['name'] not in all_students:
                all_students[student['name']] = {
                    'name': student['name'],
                    'total_scores': {},
                    'total_ranks': {}
                }
            all_students[student['name']]['total_scores'][exam['exam_index']] = student['total_score']
            all_students[student['name']]['total_ranks'][exam['exam_index']] = student['total_rank']

    # 按拼音排序所有学生
    sorted_students = sorted(all_students.items(), key=lambda x: get_pinyin_sort_key(x[0]))

    # 准备图表数据 - 按拼音排序
    exam_labels = [exam['exam_name'] for exam in exams_data]

    colors = [
        '#5B8DEF', '#FF6B6B', '#4ECDC4', '#95E1D3', '#F38181',
        '#AA96DA', '#FCBAD3', '#A8D8EA', '#FF9F43', '#6C5CE7',
        '#00CEC9', '#FD79A8', '#74B9FF', '#55EFC4', '#FDCB6E',
        '#E17055', '#00B894', '#636E72', '#B2BEC3', '#DFE6E9',
        '#74B9FF', '#A29BFE', '#FD79A8', '#FAB1A0', '#81ECEC'
    ]

    # 生成图表数据集 - 每组最多10人
    chart_groups = []
    for i in range(0, len(sorted_students), 10):
        group = sorted_students[i:i + 10]
        datasets = []
        for j, (name, data) in enumerate(group):
            color = colors[j % len(colors)]
            total_scores = [data['total_scores'].get(idx) for idx in range(num_exams)]
            total_ranks = [data['total_ranks'].get(idx) for idx in range(num_exams)]
            datasets.append({
                'name': name,
                'color': color,
                'total_scores': total_scores,
                'total_ranks': total_ranks,
            })
        chart_groups.append({
            'group_index': i // 10,
            'datasets': datasets
        })

    # 计算所有统计表
    all_stats = calculate_all_exams_statistics(exams_data)

    # 读取JS代码并替换占位符
    charts_js = read_charts_js()
    chart_lib_code = read_chart_lib()
    exam_file_names = [Path(e['file_name']).stem for e in exams_data]
    # 构造折线图x轴标签：日期在第一行 + 其余描述在第二行
    exam_axis_labels = []
    for exam in exams_data:
        name = exam['exam_name']  # 如 "2026年02月考试" 或 "10月考试——班级1"
        fn_stem = Path(exam['file_name']).stem
        # 尝试从文件名中提取日期前缀（含年份）
        date_part = re.sub(r'考试.*$', '', name)  # 去掉"考试"及之后内容
        # 去掉文件名中的日期前缀（YYYY年M月 或 M月），剩下描述
        desc = re.sub(r'^\d{4}年\d{1,2}月', '', fn_stem).strip('-').strip()
        if not desc or desc == fn_stem:
            # 无年份前缀，尝试去掉 "X月" 前缀
            desc = re.sub(r'^\d{1,2}月', '', fn_stem).strip('—').strip('-').strip()
        if not desc or desc == fn_stem:
            desc = ''
        if not desc:
            exam_axis_labels.append(date_part)
        else:
            exam_axis_labels.append(f"{date_part}\n{desc}")
    js_replacements = {
        'exam_labels_json': json.dumps(exam_labels, ensure_ascii=False),
        'exam_axis_labels_json': json.dumps(exam_axis_labels, ensure_ascii=False),
        'chart_groups_json': json.dumps(chart_groups, ensure_ascii=False),
        'exam_names_json': json.dumps([e['exam_name'] for e in exams_data], ensure_ascii=False),
        'exam_file_names_json': json.dumps(exam_file_names, ensure_ascii=False),
        'all_stats_json': json.dumps(all_stats, ensure_ascii=False),
        'total_groups': str(len(chart_groups)),
    }
    for key, value in js_replacements.items():
        charts_js = charts_js.replace('{' + key + '}', str(value))

    # 渲染HTML
    replacements = {
        'report_time': datetime.now().strftime('%Y年%m月%d日 %H:%M:%S'),
        'exam_count': str(num_exams),
        'student_count': str(len(all_students)),
        'charts_js_code': charts_js,
        'chart_lib_code': chart_lib_code,
    }

    html_content = HTML_TEMPLATE
    for key, value in replacements.items():
        html_content = html_content.replace('{' + key + '}', str(value))

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    return output_path


HTML_TEMPLATE = r'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>班级多批次考试成绩分析报告</title>
    {chart_lib_code}
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Microsoft YaHei', 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif;
            background: #f5f7fa;
            color: #333;
            line-height: 1.6;
        }
        .navbar {
            background: linear-gradient(135deg, #1a5276 0%, #2874a6 100%);
            color: white;
            padding: 18px 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.15);
            position: fixed;
            top: 0; left: 0; right: 0;
            z-index: 1000;
        }
        .navbar h1 { font-size: 22px; font-weight: 500; text-align: center; }
        .main-container { display: flex; margin-top: 70px; min-height: calc(100vh - 70px); }
        .sidebar {
            width: 220px;
            background: #f8f9fa;
            border-right: 1px solid #e0e0e0;
            position: fixed;
            top: 70px; left: 0; bottom: 0;
            overflow-y: auto;
            padding: 15px 0;
        }
        .sidebar-section {
            margin-bottom: 15px;
        }
        .sidebar-section-title {
            padding: 8px 20px;
            font-size: 12px;
            color: #888;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        .exam-item {
            padding: 10px 20px;
            cursor: pointer;
            transition: all 0.2s;
            border-left: 3px solid transparent;
            font-size: 14px;
        }
        .exam-item:hover { background: #e8f4fc; }
        .exam-item.active {
            background: #e8f4fc;
            border-left-color: #2874a6;
            color: #2874a6;
            font-weight: 500;
        }
        .chart-tab {
            padding: 10px 20px;
            cursor: pointer;
            transition: all 0.2s;
            border-left: 3px solid transparent;
            font-size: 14px;
        }
        .chart-tab:hover { background: #fff3e0; }
        .chart-tab.active {
            background: #fff3e0;
            border-left-color: #ff9800;
            color: #e65100;
            font-weight: 500;
        }
        .content { flex: 1; margin-left: 220px; padding: 25px 30px; }
        .section {
            background: white;
            border-radius: 12px;
            padding: 25px;
            margin-bottom: 25px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.06);
            display: none;
        }
        .section.active { display: block; }
        .section-title {
            font-size: 18px;
            color: #1a5276;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #e8f4fc;
            font-weight: 600;
        }
        .search-box {
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .search-input {
            flex: 1;
            max-width: 300px;
            padding: 10px 15px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 14px;
            transition: border-color 0.2s;
        }
        .search-input:focus { outline: none; border-color: #5B8DEF; }
        .search-icon { color: #999; }
        .btn {
            padding: 10px 18px;
            border: none;
            border-radius: 8px;
            font-size: 14px;
            cursor: pointer;
            font-family: inherit;
            transition: all 0.2s;
        }
        .btn-search {
            background: #2874a6;
            color: white;
        }
        .btn-search:hover { background: #1a5276; }
        .btn-clear {
            background: #e0e0e0;
            color: #555;
        }
        .btn-clear:hover { background: #ccc; }
        .search-hint {
            font-size: 12px;
            color: #999;
            margin-bottom: 15px;
        }
        .table-sort-hint {
            font-size: 12px;
            color: #999;
            margin-bottom: 15px;
            margin-top: -15px;
        }
        .charts-section { display: block; }
        .chart-group { margin-bottom: 30px; }
        .chart-group-title {
            font-size: 14px;
            color: #666;
            margin-bottom: 15px;
            font-weight: 500;
        }
        .charts-container { display: flex; gap: 25px; flex-wrap: wrap; }
        .chart-wrapper {
            flex: 1;
            min-width: 450px;
            background: #fafbfc;
            border-radius: 10px;
            padding: 20px;
            border: 1px solid #eee;
        }
        .chart-title { font-size: 15px; color: #555; margin-bottom: 15px; text-align: center; font-weight: 500; }
        .chart-canvas { max-height: 400px; }
        .table-container { margin-bottom: 30px; background: white; border-radius: 10px; overflow: hidden; }
        .table-title {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 12px 20px;
            font-size: 15px;
            font-weight: 500;
        }
        .table-wrapper { overflow-x: auto; }
        .data-table { width: 100%; border-collapse: collapse; font-size: 14px; }
        .data-table th {
            background: #f0f7ff;
            color: #1a5276;
            padding: 12px 15px;
            text-align: left;
            font-weight: 600;
            border-bottom: 2px solid #e0e7ff;
            cursor: pointer;
            white-space: nowrap;
            position: sticky;
            top: 0;
        }
        .data-table th:hover { background: #e8f4fc; }
        .sort-icon { font-size: 10px; margin-left: 5px; color: #999; }
        .data-table th.sorted .sort-icon { color: #2874a6; }
        .data-table td { padding: 10px 15px; border-bottom: 1px solid #f0f0f0; }
        .data-table tbody tr:nth-child(even) { background: #fafcff; }
        .data-table tbody tr:hover { background: #f0f7ff; }
        .data-table tbody tr.highlight { background: #fff3cd !important; font-weight: 600; }
        .pagination {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            padding: 15px;
            background: #f8f9fa;
        }
        .page-btn {
            padding: 6px 12px;
            border: 1px solid #ddd;
            background: white;
            border-radius: 5px;
            cursor: pointer;
            font-size: 13px;
            transition: all 0.2s;
        }
        .page-btn:hover:not(:disabled) { background: #e8f4fc; border-color: #5B8DEF; }
        .page-btn.active { background: #2874a6; color: white; border-color: #2874a6; }
        .page-btn:disabled { opacity: 0.5; cursor: not-allowed; }
        .page-ellipsis { padding: 0 5px; color: #999; }
        .page-info { font-size: 13px; color: #666; margin-left: 15px; }
        .footer {
            background: #f8f9fa;
            padding: 20px 30px;
            text-align: center;
            color: #666;
            font-size: 13px;
            margin-left: 220px;
            border-top: 1px solid #e0e0e0;
        }
        @media (max-width: 1024px) {
            .sidebar { width: 180px; }
            .content, .footer { margin-left: 180px; }
            .chart-wrapper { min-width: 100%; }
        }
        @media (max-width: 768px) {
            .sidebar { display: none; }
            .content, .footer { margin-left: 0; }
            .chart-wrapper { min-width: 100%; }
        }
        .chart-legend {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            justify-content: center;
            margin-top: 15px;
            max-height: 100px;
            overflow-y: auto;
        }
        .legend-item {
            display: flex;
            align-items: center;
            gap: 5px;
            font-size: 12px;
            cursor: pointer;
            padding: 3px 8px;
            border-radius: 4px;
            transition: background 0.2s;
        }
        .legend-item:hover { background: #f0f0f0; }
        .legend-color { width: 12px; height: 12px; border-radius: 2px; }
    </style>
</head>
<body>
    <nav class="navbar">
        <h1>班级多批次考试成绩分析报告</h1>
    </nav>

    <div class="main-container">
        <aside class="sidebar">
            <div class="sidebar-section">
                <div class="sidebar-section-title">折线图分析</div>
                <div class="chart-tab active" id="chartTab" onclick="showChartView()">
                    &#128202; 成绩变化趋势
                </div>
            </div>
            <div class="sidebar-section">
                <div class="sidebar-section-title">考试批次</div>
                <div id="examList"></div>
            </div>
        </aside>

        <main class="content">
            <!-- 折线图视图 -->
            <div id="chartView" class="section active">
                <h2 class="section-title">全量学生成绩变化趋势</h2>
                    <div class="search-box">
                        <span class="search-icon">&#128269;</span>
                        <input type="text" class="search-input" id="studentSearch" placeholder="输入学生姓名搜索..." onkeydown="if(event.key==='Enter') document.getElementById('searchBtn').click()">
                        <button class="btn btn-search" id="searchBtn">搜索</button>
                        <button class="btn btn-clear" id="clearBtn">清空</button>
                    </div>
                    <div class="search-hint">点击折线图下方的学生姓名可以展示/隐藏该学生的相关信息</div>
                    <div id="chartsContainer"></div>
            </div>

            <!-- 表格视图 -->
            <div id="tableView" class="section">
                    <h2 class="section-title" id="currentExamTitle">考试统计表格</h2>
                    <div class="table-sort-hint">点击表格项目栏的按钮可以改变排序方式（升序/降序）</div>
                    <div id="tablesContainer"></div>
            </div>
        </main>
    </div>

    <footer class="footer">
        <p>报告生成时间: {report_time} | 共分析 {exam_count} 次考试 | 涉及 {student_count} 名学生</p>
    </footer>

    <script>{charts_js_code}</script>
</body>
</html>
'''


def main():
    """主函数"""
    args = parse_arguments()

    print(f"正在分析目录: {args.input_dir}")

    # 查找Excel文件
    excel_files = find_excel_files(args.input_dir, args.filter)
    filter_msg = f" (filter='{args.filter}')" if args.filter else ""
    print(f"找到 {len(excel_files)} 个Excel文件{filter_msg}")

    # 检查时间是否明确
    sorted_files, unclear_files = sort_exam_files_by_time(excel_files, args.exam_order)

    if unclear_files:
        # 有文件时间不明确
        print("\n以下文件无法确定考试时间:")
        for f in unclear_files:
            print(f"  - {f.name}")
        print("\n请使用 --exam-order 参数指定考试顺序")
        print("格式: --exam-order \"考试1,考试2,考试3\"")
        print("示例: --exam-order \"2024年01月考试,2024年03月考试,2024年05月考试\"")
        return

    # 解析每个文件
    exams_data = []
    for i, file_path in enumerate(sorted_files):
        print(f"正在解析: {Path(file_path).name}")
        exam_data = parse_exam_file(file_path, i)
        exams_data.append(exam_data)
        print(f"  - {exam_data['exam_name']}: {len(exam_data['students'])} 名学生")

    # 生成报告
    print(f"正在生成HTML报告: {args.output}")
    output_path = generate_html_report(exams_data, args.output)

    print(f"\n报告生成完成: {output_path}")

    result = {
        'status': 'success',
        'output_file': str(output_path),
        'exam_count': len(exams_data),
        'student_count': sum(len(e['students']) for e in exams_data)
    }
    print(json.dumps(result, ensure_ascii=False))


if __name__ == '__main__':
    main()
