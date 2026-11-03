#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
飞书消息推送模块
通过Webhook发送富文本消息卡片
"""

import requests
import json
import hashlib
import hmac
import time
import base64
from datetime import datetime
from typing import Dict, Optional, List


class FeishuNotifier:
    """飞书消息推送器"""

    def __init__(self, webhook_url: str, secret: Optional[str] = None):
        """
        初始化推送器

        Args:
            webhook_url: 飞书Webhook地址
            secret: 签名密钥（可选，用于安全验证）
        """
        self.webhook_url = webhook_url
        self.secret = secret

    def generate_sign(self, timestamp: int) -> str:
        """
        生成签名

        Args:
            timestamp: 时间戳（毫秒）

        Returns:
            签名字符串
        """
        if not self.secret:
            return ""

        string_to_sign = f"{timestamp}\n{self.secret}"
        return base64.b64encode(
            hmac.new(
                string_to_sign.encode("utf-8"),
                digestmod=hashlib.sha256
            ).digest()
        ).decode("utf-8")

    def send_text(self, content: str) -> Dict:
        """
        发送纯文本消息

        Args:
            content: 消息内容

        Returns:
            API响应结果
        """
        payload = {
            "msg_type": "text",
            "content": {
                "text": content
            }
        }
        return self._post(payload)

    def send_rich_text(self, title: str, content: str) -> Dict:
        """
        发送富文本消息

        Args:
            title: 标题
            content: 内容（支持换行）

        Returns:
            API响应结果
        """
        payload = {
            "msg_type": "post",
            "content": {
                "post": {
                    "zh_cn": {
                        "title": title,
                        "content": [
                            [
                                {
                                    "tag": "text",
                                    "text": content
                                }
                            ]
                        ]
                    }
                }
            }
        }
        return self._post(payload)

    def send_card(self, card_content: Dict) -> Dict:
        """
        发送交互卡片消息

        Args:
            card_content: 卡片内容配置

        Returns:
            API响应结果
        """
        payload = {
            "msg_type": "interactive",
            "card": card_content
        }
        return self._post(payload)

    def send_fund_report_card(self, report_data: Dict) -> Dict:
        """
        发送基金收益报表卡片

        Args:
            report_data: 报表数据

        Returns:
            API响应结果
        """
        total = report_data.get("total", {})
        holdings = report_data.get("holdings", [])
        date_str = datetime.now().strftime("%Y年%m月%d日")

        # 构建卡片元素
        elements = [
            # 汇总信息
            {
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": f"**📅 {date_str}**"
                }
            },
            {
                "tag": "hr"
            },
            {
                "tag": "div",
                "fields": [
                    {
                        "is_short": True,
                        "text": {
                            "tag": "lark_md",
                            "content": f"**💰 总资产**\n¥{total.get('total_market_value', 0):,.2f}"
                        }
                    },
                    {
                        "is_short": True,
                        "text": {
                            "tag": "lark_md",
                            "content": self._format_return_card(
                                "📈 今日收益",
                                total.get('total_daily_return', 0),
                                total.get('total_daily_return_pct', 0)
                            )
                        }
                    },
                    {
                        "is_short": True,
                        "text": {
                            "tag": "lark_md",
                            "content": self._format_return_card(
                                "💵 累计收益",
                                total.get('total_return', 0),
                                total.get('total_return_pct', 0)
                            )
                        }
                    }
                ]
            },
            {
                "tag": "hr"
            }
        ]

        # 持仓明细
        elements.append({
            "tag": "div",
            "text": {
                "tag": "lark_md",
                "content": "**【持仓明细】**"
            }
        })

        # 按持仓占比排序
        sorted_holdings = sorted(holdings, key=lambda x: x.get('market_value', 0), reverse=True)

        for i, h in enumerate(sorted_holdings, 1):
            daily_sign = "📈" if h.get('daily_return', 0) >= 0 else "📉"
            total_sign = "📈" if h.get('total_return', 0) >= 0 else "📉"

            holding_text = (
                f"{i}. **{h.get('name', h.get('code'))}** ({h.get('code')})\n"
                f"   • 持仓：{h.get('shares', 0):.2f}份 @ ¥{h.get('cost', 0):.4f}\n"
                f"   • {daily_sign} 今日：¥{h.get('daily_return', 0):+,.2f} ({h.get('daily_return_pct', 0):+.2f}%)\n"
                f"   • {total_sign} 累计：¥{h.get('total_return', 0):+,.2f} ({h.get('total_return_pct', 0):+.2f}%)\n"
                f"   • 占比：{h.get('allocation_pct', 0):.1f}%"
            )

            elements.append({
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": holding_text
                }
            })

            if i < len(sorted_holdings):
                elements.append({
                    "tag": "hr"
                })

        # 卡片配置
        card = {
            "config": {
                "wide_screen_mode": True
            },
            "header": {
                "title": {
                    "tag": "plain_text",
                    "content": "📊 每日基金收益报表"
                },
                "template": "blue"
            },
            "elements": elements
        }

        return self.send_card(card)

    def _format_return_card(self, label: str, amount: float, pct: float) -> str:
        """格式化收益数据用于卡片"""
        sign = "+" if amount >= 0 else ""
        return f"**{label}**\n{sign}¥{amount:,.2f} ({sign}{pct:.2f}%)"

    def _post(self, payload: Dict) -> Dict:
        """发送POST请求"""
        headers = {"Content-Type": "application/json"}

        # 添加签名
        if self.secret:
            timestamp = int(time.time() * 1000)
            sign = self.generate_sign(timestamp)
            payload["timestamp"] = timestamp
            payload["sign"] = sign

        try:
            response = requests.post(
                self.webhook_url,
                headers=headers,
                data=json.dumps(payload),
                timeout=10
            )

            result = response.json()

            if result.get("code") == 0 or result.get("StatusCode") == 0:
                return {"success": True, "message": "发送成功"}
            else:
                return {
                    "success": False,
                    "message": result.get("msg", "发送失败")
                }

        except requests.RequestException as e:
            return {
                "success": False,
                "message": f"请求异常: {str(e)}"
            }


def send_cli():
    """命令行入口"""
    import sys

    if len(sys.argv) < 3:
        print("用法: python send_feishu.py <webhook_url> <报告数据JSON>")
        print("示例: python send_feishu.py 'https://...' 'data/report.json'")
        sys.exit(1)

    webhook_url = sys.argv[1]
    report_file = sys.argv[2]

    # 加载报告数据
    with open(report_file, 'r', encoding='utf-8') as f:
        report_data = json.load(f)

    # 发送
    notifier = FeishuNotifier(webhook_url)
    result = notifier.send_fund_report_card(report_data)

    if result.get("success"):
        print("✅ 飞书消息发送成功!")
    else:
        print(f"❌ 发送失败: {result.get('message')}")


if __name__ == "__main__":
    send_cli()
