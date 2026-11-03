#!/usr/bin/env python3
"""
金价日报推送脚本
将生成的金价日报推送给用户
"""

import os
import datetime
from typing import Optional

def read_report(report_path: str) -> str:
    """
    读取报告内容

    Args:
        report_path: 报告文件路径

    Returns:
        str: 报告内容
    """
    with open(report_path, 'r', encoding='utf-8') as f:
        return f.read()

def format_report_for_notification(report_content: str) -> str:
    """
    将报告内容格式化为通知消息

    Args:
        report_content: 原始报告内容

    Returns:
        str: 格式化后的通知内容
    """
    lines = report_content.split('\n')

    # 提取关键信息
    title = ""
    summary = []
    in_summary = False

    for line in lines:
        if line.startswith('# '):
            title = line.replace('# ', '').strip()
        elif line.startswith('**核心结论**'):
            in_summary = True
        elif in_summary and line.strip().startswith('-'):
            summary.append(line.strip().replace('- ', ''))
        elif in_summary and line.strip().startswith('|'):
            in_summary = False

    # 构建简洁的通知内容
    notification = f"📊 **{title}**\n\n"
    notification += "**核心结论**\n"
    for item in summary[:3]:  # 只显示前3条
        notification += f"• {item}\n"

    notification += f"\n📎 完整报告请查看附件"

    return notification

def send_notification(report_path: str, method: str = "feishu") -> bool:
    """
    发送通知

    Args:
        report_path: 报告文件路径
        method: 通知方式（feishu/slack/email等）

    Returns:
        bool: 发送是否成功
    """
    if not os.path.exists(report_path):
        print(f"报告文件不存在: {report_path}")
        return False

    report_content = read_report(report_path)

    # 根据不同方式发送通知
    if method == "feishu":
        return send_feishu_notification(report_content)
    elif method == "slack":
        return send_slack_notification(report_content)
    else:
        # 默认打印到控制台
        print(report_content)
        return True

def send_feishu_notification(content: str) -> bool:
    """
    发送飞书通知

    Args:
        content: 通知内容

    Returns:
        bool: 发送是否成功
    """
    # TODO: 实现飞书Webhook推送
    # 1. 获取飞书Webhook URL
    # 2. 构建消息内容
    # 3. 发送POST请求

    print("飞书通知发送（待实现）")
    print(content[:500] + "..." if len(content) > 500 else content)
    return True

def send_slack_notification(content: str) -> bool:
    """
    发送Slack通知

    Args:
        content: 通知内容

    Returns:
        bool: 发送是否成功
    """
    # TODO: 实现Slack Webhook推送
    print("Slack通知发送（待实现）")
    return True

def main():
    """主函数"""
    today = datetime.datetime.now().strftime("%Y-%m-%d")

    # 默认报告路径
    report_path = f"reports/{today}-gold-daily-report.md"

    if not os.path.exists(report_path):
        print(f"报告文件不存在: {report_path}")
        return

    success = send_notification(report_path, method="feishu")

    if success:
        print(f"通知发送成功")
    else:
        print(f"通知发送失败")

if __name__ == "__main__":
    main()
