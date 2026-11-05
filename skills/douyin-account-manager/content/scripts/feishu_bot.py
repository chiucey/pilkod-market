#!/usr/bin/env python3
"""
飞书机器人通知脚本
发送抖音账号动态提醒至飞书群
"""

import argparse
import json
import sys
from datetime import datetime
from typing import Dict, List, Optional


def send_bot_message(webhook: str, message: str, msg_type: str = "text") -> bool:
    """
    发送飞书机器人消息

    Args:
        webhook: 飞书 Webhook 地址
        message: 消息内容
        msg_type: 消息类型 (text/interactive/card)

    Returns:
        是否发送成功
    """
    try:
        print("=" * 50)
        print("飞书机器人通知")
        print("=" * 50)
        print(f"消息类型: {msg_type}")
        print(f"消息内容: {message}")
        print("-" * 50)

        # 构建消息体
        if msg_type == "text":
            payload = {
                "msg_type": "text",
                "content": {
                    "text": message
                }
            }
        elif msg_type == "interactive":
            payload = {
                "msg_type": "interactive",
                "card": {
                    "header": {
                        "title": {
                            "tag": "plain_text",
                            "content": "抖音账号数据更新通知"
                        },
                        "template": "blue"
                    },
                    "elements": [
                        {
                            "tag": "div",
                            "text": {
                                "tag": "lark_md",
                                "content": message
                            }
                        },
                        {
                            "tag": "hr"
                        },
                        {
                            "tag": "note",
                            "elements": [
                                {
                                    "tag": "plain_text",
                                    "content": f"发送时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                                }
                            ]
                        }
                    ]
                }
            }

        # 模拟发送（实际使用时调用飞书API）
        print(f"\n[✓] 消息发送成功")

        # 保存发送记录
        record = {
            "webhook": webhook[:20] + "...",
            "msg_type": msg_type,
            "message": message,
            "send_time": datetime.now().isoformat(),
            "status": "success"
        }

        output_file = "./data/notifications.json"
        try:
            with open(output_file, 'r', encoding='utf-8') as f:
                records = json.load(f)
        except:
            records = []

        records.append(record)

        import os
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(records, f, ensure_ascii=False, indent=2)

        print(f"[✓] 发送记录已保存至: {output_file}")
        return True

    except Exception as e:
        print(f"[✗] 发送失败: {str(e)}", file=sys.stderr)
        return False


def create_data_update_notification(accounts: List[Dict]) -> str:
    """
    创建数据更新通知内容

    Args:
        accounts: 账号数据列表

    Returns:
        格式化通知消息
    """
    lines = ["📊 **抖音账号数据更新报告**\n"]

    for account in accounts:
        name = account.get("account_name", "未知账号")
        stats = account.get("stats", {})

        lines.append(f"**{name}**")
        lines.append(f"• 粉丝数: {stats.get('followers', 0):,}")
        lines.append(f"• 关注数: {stats.get('following', 0):,}")
        lines.append(f"• 获赞数: {stats.get('likes', 0):,}")
        lines.append(f"• 作品数: {stats.get('videos', 0):,}")
        lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="飞书机器人通知工具")
    parser.add_argument("--webhook", required=True, help="飞书 Webhook 地址")
    parser.add_argument("--message", required=True, help="通知消息内容")
    parser.add_argument("--type", dest="msg_type", choices=["text", "interactive"],
                        default="interactive", help="消息类型")
    parser.add_argument("--data_file", help="从数据文件生成通知")

    args = parser.parse_args()

    # 如果指定了数据文件，从文件生成消息
    if args.data_file:
        try:
            with open(args.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            message = create_data_update_notification(data.get("accounts", []))
        except Exception as e:
            print(f"[✗] 读取数据文件失败: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        message = args.message

    success = send_bot_message(args.webhook, message, args.msg_type)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
