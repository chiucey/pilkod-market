"""
Weekly Review Extractor Script
Extracts content from YYYY-Wnn format PDFs and generates concise communication reports
"""

import re
import json
from typing import Dict, List, Optional

def extract_review_summary(content: str) -> Dict[str, any]:
    """Extract weekly review key information"""

    # Extract time range
    week_match = re.search(r'第(\d+)周复盘（(\d+月\d+日)～(\d+月\d+日)）', content)
    week_num = week_match.group(1) if week_match else "unknown"
    date_range = f"{week_match.group(2)}~{week_match.group(3)}" if week_match else ""

    # Extract weekly overview
    overview_match = re.search(r'## 本周概览\n+(.+?)(?=##|$)', content, re.DOTALL)
    overview = overview_match.group(1).strip() if overview_match else ""

    # Extract completed items
    completed = []
    # Thesis
    if '论文' in content:
        paper_match = re.search(r'论文[：:]?\s*(.+?)(?=python|故障|$)', content, re.DOTALL)
        if paper_match:
            completed.append(f"Thesis: {paper_match.group(1).strip().split(chr(10))[0]}")

    # Python learning
    python_match = re.search(r'python.?学习[：:]?\s*[\n•]*进度[：:]?\s*(\d+)\s*[→→]\s*(\d+)（\+(\d+)节）', content)
    if python_match:
        completed.append(f"Python: {python_match.group(1)}->{python_match.group(2)} (+{python_match.group(3)} lessons)")

    # Fault analysis
    fault_match = re.search(r'故障分析.*?推进到\s*(\d+)\s*页', content)
    if fault_match:
        completed.append(f"Fault Analysis: advanced to page {fault_match.group(1)}")

    # Extract what went well
    smooth_things = []
    smooth_pattern = r'做得顺的事\n+(.+?)(?=阻力|反复|$)'
    smooth_match = re.search(smooth_pattern, content, re.DOTALL)
    if smooth_match:
        lines = smooth_match.group(1).strip().split('\n')
        for line in lines:
            line = line.strip('•- ')
            if line and len(line) < 100:
                smooth_things.append(line)

    # Extract challenges
    hard_things = []
    hard_pattern = r'阻力大的事\n+(.+?)(?=反复|未完成|$)'
    hard_match = re.search(hard_pattern, content, re.DOTALL)
    if hard_match:
        lines = hard_match.group(1).strip().split('\n')
        for line in lines:
            line = line.strip('•- ')
            if line and len(line) < 100:
                hard_things.append(line)

    # Extract next week adjustments
    next_week = []
    adjustment_pattern = r'下周调整\n+(.+?)(?=本周感悟|$)'
    adjustment_match = re.search(adjustment_pattern, content, re.DOTALL)
    if adjustment_match:
        lines = adjustment_match.group(1).strip().split('\n')
        for line in lines:
            line = line.strip()
            if re.match(r'\d+\.', line):
                next_week.append(line)

    # Extract weekly insight
    insight_match = re.search(r'本周感悟\n+(.+?)$', content, re.DOTALL)
    insight = insight_match.group(1).strip() if insight_match else ""

    return {
        "week_num": week_num,
        "date_range": date_range,
        "overview": overview,
        "completed": completed,
        "smooth_things": smooth_things,
        "hard_things": hard_things,
        "next_week": next_week,
        "insight": insight
    }

def format_output(data: Dict) -> str:
    """Format output as yellow highlight blocks"""

    output_parts = []

    # Date range title
    date_display = f"Week {data['week_num']} ({data['date_range']})"
    output_parts.append(f"## {date_display}")

    # Last week review
    output_parts.append("\n### Last Week Review\n")
    output_parts.append('<div style="background-color: #FFF3CD; padding: 15px; border-radius: 8px; margin: 10px 0;">')

    # Main outputs
    if data['completed']:
        output_parts.append("**Main Outputs**: " + "; ".join(data['completed']) + "\n\n")

    # Went well / Challenges
    if data['smooth_things']:
        output_parts.append("**Went Well**: " + "; ".join(data['smooth_things'][:2]) + "\n\n")
    if data['hard_things']:
        output_parts.append("**Challenges**: " + "; ".join(data['hard_things'][:2]) + "\n\n")

    # Weekly insight
    if data['insight']:
        insight_brief = data['insight'].split('。')[0] + '。'
        if len(insight_brief) > 80:
            insight_brief = insight_brief[:80] + '...'
        output_parts.append(f"**Weekly Insight**: {insight_brief}\n")

    output_parts.append('</div>')

    # Next week plan
    output_parts.append("\n### Next Week Plan\n")
    output_parts.append('<div style="background-color: #FFF3CD; padding: 15px; border-radius: 8px; margin: 10px 0;">')

    if data['next_week']:
        for i, item in enumerate(data['next_week'][:5], 1):
            output_parts.append(f"{i}. {item}\n")
    else:
        output_parts.append("No explicit plans yet. Please create based on last week review.\n")

    output_parts.append('</div>')

    return ''.join(output_parts)

def generate_for_labmate(data: Dict) -> str:
    """Generate labmate communication version - more concise and direct"""

    lines = []

    # Short title
    lines.append(f"**Week {data['week_num']} ({data['date_range']})**\n")

    # Last week progress
    lines.append("**Last Week Progress**:")
    if data['completed']:
        for item in data['completed'][:3]:
            lines.append(f"- {item}")
    lines.append("")

    # Issues / What's smooth
    if data['smooth_things']:
        lines.append("**Smooth**: " + "; ".join(data['smooth_things'][:2]))
    if data['hard_things']:
        lines.append("**Difficult**: " + "; ".join(data['hard_things'][:2]))
    lines.append("")

    # Next week plan
    lines.append("**Next Week Plan**:")
    if data['next_week']:
        for item in data['next_week'][:3]:
            lines.append(f"- {item}")
    else:
        lines.append("- Continue current task progress")

    return '\n'.join(lines)


if __name__ == "__main__":
    # Test content
    test_content = """
    ## 第19周复盘（5月4日～5月10日）

    ## 本周概览
    本周是论文撰写期的关键一周。论文查重通过（9%），但换系统后出现反复；python 学习从中断中恢复，进度 66→94；故障分析从连续 7 天缺席到重启并推进到 47 页。

    ## 本周完成
    论文：查重通过，重复率 9%
    python 学习：进度 66 → 94（+28 节）
    故障分析：从连续 7 天缺席到重启，推进到 47 页

    ## 做得顺的事
    论文格式工作：交叉引用、公式统一、查重修改，这类"具体、可拆解"的任务执行效率高
    周日全勤恢复：在连续2天低谷后，周日实现全勤

    ## 阻力大的事
    python 学习：近 7 天仅完成 4 天，主要是被论文查重和修改挤掉
    查重降重：换 speedai 后出现反复（37%→24%→30%）

    ## 下周调整
    1. python 学习降低门槛：从"60min"改为"学了就勾"
    2. 查重策略明确：确认学校最终用哪个查重系统
    3. 论文字数确认：与老师或师兄确认本科毕设的字数要求

    ## 本周感悟
    这周最有价值的发现是：任务的清晰度比专注力更重要。5/4 改交叉引用能坚持一个多小时，因为任务足够具体。
    """

    data = extract_review_summary(test_content)
    print("=== Standard Format ===")
    print(format_output(data))
    print("\n=== Labmate Version ===")
    print(generate_for_labmate(data))