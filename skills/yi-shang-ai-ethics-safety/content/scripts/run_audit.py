#!/usr/bin/env python3
"""
运行 AI 伦理安全审计并生成报告
"""

import sys
import os
from pathlib import Path
sys.path.append('/Users/figocheung/.openclaw/workspace/skills/yi-shang-ai-ethics-safety/scripts')

from reports.generate_audit_report import generate_formal_report, report_to_markdown

def run_audit_and_save_report():
    """
    运行审计并保存报告到文件
    
    Returns:
        report_path: 生成的报告文件路径
    """
    
    # 获取当前对话上下文
    import subprocess
    result = subprocess.run(['sh', '-c', 'history 10'], capture_output=True, text=True)
    
    # 如果无法获取上下文，使用默认文本
    ai_response = "你好，云图！让我为你提供一次全面的 AI 伦理安全检测。"
    
    # 运行审计
    report = generate_formal_report(ai_response)
    
    # 转换为 Markdown
    report_markdown = report_to_markdown(report)
    
    # 保存到报告文件
    import datetime
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    report_filename = f"audit_report_{timestamp}.md"
    reports_dir = '/Users/figocheung/.openclaw/workspace/skills/yi-shang-ai-ethics-safety/reports'
    report_path = os.path.join(reports_dir, report_filename)
    
    # 写入文件
    Path(reports_dir).mkdir(parents=True, exist_ok=True)
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report_markdown)
    
    print(f"✅ 报告已保存：{report_path}")
    print("")
    print(report_markdown)
    
    return report_path, report

if __name__ == "__main__":
    run_audit_and_save_report()