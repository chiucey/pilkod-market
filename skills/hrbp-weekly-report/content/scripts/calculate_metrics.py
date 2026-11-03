#!/usr/bin/env python3
"""
HRBP周报指标计算脚本
从Excel数据计算关键HR指标
"""

import pandas as pd
import json
from pathlib import Path


def load_excel_data(excel_path: str) -> dict:
    """读取Excel文件中的所有Sheet数据"""
    excel_file = pd.ExcelFile(excel_path)
    data = {}

    for sheet_name in ['本周', '上周']:
        if sheet_name in excel_file.sheet_names:
            data[sheet_name] = pd.read_excel(excel_file, sheet_name=sheet_name)

    return data


def calculate_hirecount_metrics(df: pd.DataFrame) -> dict:
    """计算HC相关指标"""
    total_hired = df['招聘数量'].sum() if '招聘数量' in df.columns else 0
    total_target = df['目标人数'].sum() if '目标人数' in df.columns else 0

    achievement_rate = (total_hired / total_target * 100) if total_target > 0 else 0

    return {
        '招聘人数': int(total_hired),
        '目标人数': int(total_target),
        '达成率': round(achievement_rate, 1)
    }


def calculate_attrition_metrics(df: pd.DataFrame, base_headcount: int = 100) -> dict:
    """计算离职相关指标"""
    total_turnover = len(df) if df is not None else 0
    turnover_rate = (total_turnover / base_headcount * 100) if base_headcount > 0 else 0

    reason_distribution = {}
    if df is not None and '离职原因' in df.columns:
        reason_distribution = df['离职原因'].value_counts().to_dict()

    return {
        '离职人数': total_turnover,
        '离职率': round(turnover_rate, 2),
        '原因分布': reason_distribution
    }


def calculate_training_metrics(df: pd.DataFrame) -> dict:
    """计算培训相关指标"""
    if df is None:
        return {
            '计划场次': 0,
            '完成场次': 0,
            '完成率': 0,
            '参与人次': 0,
            '平均满意度': 0
        }

    total_planned = len(df) if df is not None else 0
    total_completed = len(df) if df is not None else 0  # 实际完成以日期判断

    participation = df['实际人数'].sum() if '实际人数' in df.columns else 0
    avg_satisfaction = df['满意度'].mean() if '满意度' in df.columns else 0

    completion_rate = (total_completed / total_planned * 100) if total_planned > 0 else 0

    return {
        '计划场次': total_planned,
        '完成场次': total_completed,
        '完成率': round(completion_rate, 1),
        '参与人次': int(participation),
        '平均满意度': round(avg_satisfaction, 1)
    }


def calculate_all_metrics(excel_path: str) -> dict:
    """计算所有HR指标"""
    data = load_excel_data(excel_path)

    metrics = {
        '招聘数据': calculate_recruitment_metrics(data.get('招聘数据')),
        '离职数据': calculate_attrition_metrics(data.get('离职数据')),
        '培训数据': calculate_training_metrics(data.get('培训数据'))
    }

    return metrics


def generate_email_content(metrics: dict, week: str, department: str) -> str:
    """根据模板和指标生成邮件内容"""
    template_path = Path(__file__).parent.parent / 'references' / 'email_template.md'

    if template_path.exists():
        with open(template_path, 'r', encoding='utf-8') as f:
            template = f.read()
    else:
        # 使用内联模板
        template = get_inline_template()

    # 替换模板中的占位符
    content = template.replace('[周次/日期范围]', week)
    content = content.replace('[部门名称]', department)

    # 替换招聘数据
    rec = metrics.get('招聘数据', {})
    content = content.replace('[招聘人数]', str(rec.get('招聘人数', 0)))
    content = content.replace('[目标人数]', str(rec.get('目标人数', 0)))
    content = content.replace('[达成率]', str(rec.get('达成率', 0)))

    # 替换离职数据
    att = metrics.get('离职数据', {})
    content = content.replace('[离职人数]', str(att.get('离职人数', 0)))
    content = content.replace('[原因分析]', str(att.get('原因分布', '无')))

    # 替换培训数据
    tra = metrics.get('培训数据', {})
    content = content.replace('[计划场次]', str(tra.get('计划场次', 0)))
    content = content.replace('[完成场次]', str(tra.get('完成场次', 0)))
    content = content.replace('[完成率]', str(tra.get('完成率', 0)))
    content = content.replace('[参与人次]', str(tra.get('参与人次', 0)))
    content = content.replace('[评分]', str(tra.get('平均满意度', 0)))

    return content


def get_inline_template() -> str:
    """内联邮件模板（当文件不存在时使用）"""
    return f"""各位好，

以下是本周HR工作汇总，请查阅：

## 一、本周数据汇总

### 1. 招聘进展
- 本周招聘人数：[招聘人数]
- 目标招聘人数：[目标人数]
- 招聘达成率：[达成率]%

### 2. 人员变动
- 本周离职人数：[离职人数]

### 3. 培训与发展
- 计划培训场次：[计划场次]
- 完成培训场次：[完成场次]
- 培训完成率：[完成率]%

## 二、下周工作计划
1. 继续推进招聘工作
2. 组织培训活动
3. 完成员工一对一沟通

---
如有疑问，随时沟通。

Best Regards"""


if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print("用法: python calculate_metrics.py <Excel文件路径>")
        sys.exit(1)

    excel_path = sys.argv[1]
    week = sys.argv[2] if len(sys.argv) > 2 else "本周"
    department = sys.argv[3] if len(sys.argv) > 3 else "本部门"

    metrics = calculate_all_metrics(excel_path)
    print(json.dumps(metrics, ensure_ascii=False, indent=2))

    email = generate_email_content(metrics, week, department)
    print("\n=== 生成的邮件内容 ===\n")
    print(email)
