#!/usr/bin/env python3
"""
飞书 Webhook 推送脚本
功能：将保险知识采集结果推送至飞书群
"""

import json
import argparse
from datetime import datetime
from typing import List, Dict, Optional
import requests


class FeishuPusher:
    """飞书 Webhook 推送器"""

    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
        self.session = requests.Session()

    def push_text(self, content: str) -> bool:
        """
        推送文本消息

        Args:
            content: 文本内容

        Returns:
            是否成功
        """
        payload = {
            "msg_type": "text",
            "content": {
                "text": content
            }
        }
        return self._send(payload)

    def push_markdown(self, content: str) -> bool:
        """
        推送 Markdown 消息

        Args:
            content: Markdown 内容

        Returns:
            是否成功
        """
        payload = {
            "msg_type": "interactive",
            "card": {
                "config": {
                    "wide_screen_mode": True
                },
                "header": {
                    "title": {
                        "tag": "plain_text",
                        "content": "📊 保险知识日报"
                    },
                    "template": "blue"
                },
                "elements": [
                    {
                        "tag": "markdown",
                        "content": content
                    }
                ]
            }
        }
        return self._send(payload)

    def push_article_card(self, articles: List[Dict]) -> bool:
        """
        推送文章卡片

        Args:
            articles: 文章列表
        """
        elements = []

        for article in articles:
            title = article.get('title', '无标题')
            link = article.get('link', '')
            account = article.get('account_name', article.get('author', '未知'))
            pub_date = article.get('pub_date', '')[:10] if article.get('pub_date') else ''
            insights = article.get('insights', {})

            # 构建卡片内容
            card_content = f"**{title}**\n"
            card_content += f"- 📰 来源：{account}\n"
            card_content += f"- 📅 {pub_date}\n"

            if insights:
                if insights.get('product_name'):
                    card_content += f"- 💡 产品：{insights['product_name']}\n"
                if insights.get('coverage'):
                    card_content += f"- 📋 责任：{insights['coverage']}\n"

            card_content += f"[阅读原文]({link})"

            elements.append({
                "tag": "markdown",
                "content": card_content
            })

            elements.append({
                "tag": "hr"
            })

        # 添加更新时间
        elements.append({
            "tag": "note",
            "elements": [
                {
                    "tag": "plain_text",
                    "content": f"更新时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}"
                }
            ]
        })

        payload = {
            "msg_type": "interactive",
            "card": {
                "config": {
                    "wide_screen_mode": True
                },
                "header": {
                    "title": {
                        "tag": "plain_text",
                        "content": f"📊 保险知识日报 - {datetime.now().strftime('%Y-%m-%d')}"
                    },
                    "template": "blue"
                },
                "elements": elements
            }
        }

        return self._send(payload)

    def push_summary(self, articles: List[Dict], title: str = "保险知识日报") -> bool:
        """
        推送摘要报告

        Args:
            articles: 文章列表
            title: 报告标题
        """
        # 统计信息
        total = len(articles)
        accounts = set(a.get('account_name', a.get('author', '未知')) for a in articles)

        # 按账号分组统计
        from collections import Counter
        account_counts = Counter(a.get('account_name', a.get('author', '未知')) for a in articles)

        content = f"**今日采集概览**\n\n"
        content += f"- 📰 总文章数：{total}\n"
        content += f"- 🏢 涉及公众号：{len(accounts)} 个\n\n"
        content += f"**分布情况：**\n"

        for account, count in account_counts.most_common(5):
            content += f"- {account}：{count} 篇\n"

        content += f"\n---\n\n"

        # 添加前3篇文章
        content += f"**最新内容 Top {min(3, total)}：**\n\n"

        for i, article in enumerate(articles[:3], 1):
            title_short = article.get('title', '无标题')[:30]
            if len(article.get('title', '')) > 30:
                title_short += '...'
            content += f"{i}. {title_short}\n"
            content += f"   📅 {article.get('pub_date', '')[:10]}\n\n"

        return self.push_markdown(content)

    def _send(self, payload: dict) -> bool:
        """发送请求"""
        try:
            response = self.session.post(
                self.webhook_url,
                json=payload,
                timeout=10
            )
            result = response.json()

            if result.get('code') == 0 or result.get('StatusCode') == 0:
                return True
            else:
                print(f"推送失败: {result}")
                return False

        except Exception as e:
            print(f"推送异常: {str(e)}")
            return False


def load_articles(json_path: str) -> List[Dict]:
    """从 JSON 文件加载文章"""
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def main():
    parser = argparse.ArgumentParser(description='飞书推送工具')
    parser.add_argument('--webhook', required=True, help='飞书 Webhook URL')
    parser.add_argument('--json', help='文章 JSON 文件路径')
    parser.add_argument('--text', help='直接推送的文本')
    parser.add_argument('--summary', action='store_true', help='推送摘要报告')
    parser.add_argument('--articles-json', help='文章列表 JSON')

    args = parser.parse_args()

    pusher = FeishuPusher(args.webhook)

    if args.text:
        success = pusher.push_text(args.text)
        print(f"文本推送{'成功' if success else '失败'}")

    if args.summary and args.articles_json:
        articles = load_articles(args.articles_json)
        success = pusher.push_summary(articles)
        print(f"摘要推送{'成功' if success else '失败'}")

    if args.json:
        articles = load_articles(args.json)
        success = pusher.push_article_card(articles)
        print(f"卡片推送{'成功' if success else '失败'}")


if __name__ == '__main__':
    main()
