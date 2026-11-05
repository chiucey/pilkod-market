#!/usr/bin/env python3
"""
保险知识内容采集脚本
功能：从微信公众号抓取文章信息，支持 RSSHub 公开接口
"""

import json
import time
import re
import argparse
from datetime import datetime
from typing import List, Dict, Optional
import requests
from bs4 import BeautifulSoup

# 配置
DEFAULT_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

class WeChatScraper:
    """微信公众号内容采集器"""

    def __init__(self, config_path: str = None):
        self.config = self._load_config(config_path)
        self.session = requests.Session()
        self.session.headers.update(DEFAULT_HEADERS)

    def _load_config(self, config_path: str) -> dict:
        """加载配置文件"""
        if config_path:
            import yaml
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        return {}

    def collect_via_rsshub(self, account_name: str, limit: int = 5) -> List[Dict]:
        """
        通过 RSSHub 获取公众号文章

        Args:
            account_name: 公众号名称
            limit: 最大文章数量

        Returns:
            文章列表
        """
        articles = []

        try:
            # RSSHub 公开接口
            rsshub_base = "https://rsshub.app"
            url = f"{rsshub_base}/wechat/mp/{account_name}"

            response = self.session.get(url, timeout=30)

            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'xml')
                items = soup.find_all('item')[:limit]

                for item in items:
                    article = {
                        'title': self._clean_text(item.title.text if item.title else ''),
                        'link': item.link.text if item.link else '',
                        'pub_date': item.pubDate.text if item.pubDate else '',
                        'author': account_name,
                        'platform': 'wechat_public',
                        'account_name': account_name
                    }
                    articles.append(article)

        except Exception as e:
            print(f"抓取公众号 '{account_name}' 失败: {str(e)}")

        return articles

    def collect_all(self, accounts: List[str], limit_per_account: int = 5,
                    interval: int = 30) -> List[Dict]:
        """
        批量采集多个公众号

        Args:
            accounts: 公众号名称列表
            limit_per_account: 每账号文章数
            interval: 请求间隔(秒)
        """
        all_articles = []

        for i, account in enumerate(accounts):
            print(f"[{i+1}/{len(accounts)}] 正在采集: {account}")
            articles = self.collect_via_rsshub(account, limit_per_account)
            all_articles.extend(articles)

            if i < len(accounts) - 1:
                time.sleep(interval)

        return all_articles

    def _clean_text(self, text: str) -> str:
        """清理文本"""
        if not text:
            return ''
        return re.sub(r'\s+', ' ', text).strip()


class ContentFilter:
    """内容过滤器"""

    def __init__(self, keywords: List[str] = None):
        # 默认保险相关关键词
        self.keywords = keywords or [
            '重疾险', '增额终身寿', '年金险', '医疗险', '寿险',
            '意外险', '保险攻略', '保险测评', '保险对比', '保险推荐'
        ]

    def is_relevant(self, title: str) -> bool:
        """
        判断内容是否相关

        Args:
            title: 文章标题

        Returns:
            是否相关
        """
        if not self.keywords:
            return True

        title_lower = title.lower()
        for keyword in self.keywords:
            if keyword.lower() in title_lower:
                return True
        return False

    def filter_articles(self, articles: List[Dict]) -> List[Dict]:
        """过滤文章列表"""
        return [a for a in articles if self.is_relevant(a.get('title', ''))]


def extract_insurance_insights(article: Dict, llm_api: str = None) -> Dict:
    """
    使用 LLM 提取保险核心观点

    Args:
        article: 文章信息
        llm_api: LLM API 地址

    Returns:
        包含核心观点的增强文章信息
    """
    # 如果没有 LLM API，返回基础信息
    if not llm_api:
        return {
            **article,
            'insights': {
                'product_name': '待分析',
                'coverage': '待分析',
                'rate_comparison': '待分析',
                'pros': [],
                'cons': [],
                'sales_talk': []
            }
        }

    # TODO: 实现 LLM 调用进行观点提炼
    # 以下为占位实现
    prompt = f"""
请分析以下保险相关文章，提取核心观点：

标题：{article.get('title', '')}
作者：{article.get('author', '')}

请提取：
1. 产品名称
2. 保障责任
3. 费率对比（如有）
4. 优点
5. 缺点
6. 常见销售话术

以 JSON 格式返回。
"""

    # 此处应调用 LLM API
    # 暂时返回空结构
    return {
        **article,
        'insights': {
            'product_name': '',
            'coverage': '',
            'rate_comparison': '',
            'pros': [],
            'cons': [],
            'sales_talk': []
        }
    }


def format_as_markdown(articles: List[Dict], title: str = "保险知识采集报告") -> str:
    """
    格式化为 Markdown

    Args:
        articles: 文章列表
        title: 报告标题

    Returns:
        Markdown 格式文本
    """
    lines = [
        f"# {title}",
        f"\n生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"\n共采集 {len(articles)} 篇文章\n",
        "---"
    ]

    # 按公众号分组
    from collections import defaultdict
    grouped = defaultdict(list)
    for a in articles:
        grouped[a.get('account_name', '未知')].append(a)

    for account, articles in grouped.items():
        lines.append(f"\n## 📰 {account}")
        lines.append(f"\n共 {len(articles)} 篇文章\n")

        for i, article in enumerate(articles, 1):
            lines.append(f"\n### {i}. {article.get('title', '无标题')}")
            lines.append(f"\n- 📅 发布时间：{article.get('pub_date', '未知')}")
            lines.append(f"- 🔗 原文链接：{article.get('link', '无链接')}")

            insights = article.get('insights', {})
            if insights:
                lines.append("\n**核心观点：**")
                if insights.get('product_name'):
                    lines.append(f"- 产品名称：{insights['product_name']}")
                if insights.get('coverage'):
                    lines.append(f"- 保障责任：{insights['coverage']}")
                if insights.get('rate_comparison'):
                    lines.append(f"- 费率对比：{insights['rate_comparison']}")
                if insights.get('pros'):
                    lines.append(f"- 优点：{', '.join(insights['pros'])}")
                if insights.get('cons'):
                    lines.append(f"- 缺点：{', '.join(insights['cons'])}")
                if insights.get('sales_talk'):
                    lines.append(f"- 销售话术：{', '.join(insights['sales_talk'])}")

    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description='保险知识内容采集')
    parser.add_argument('--accounts', nargs='+', help='公众号名称列表')
    parser.add_argument('--config', help='配置文件路径')
    parser.add_argument('--limit', type=int, default=5, help='每账号文章数')
    parser.add_argument('--interval', type=int, default=30, help='请求间隔(秒)')
    parser.add_argument('--output', help='输出文件路径')
    parser.add_argument('--keywords', nargs='+', help='过滤关键词')
    parser.add_argument('--llm-api', help='LLM API 地址')

    args = parser.parse_args()

    # 初始化采集器
    scraper = WeChatScraper(args.config)

    # 获取公众号列表
    accounts = args.accounts or []
    if args.config:
        import yaml
        with open(args.config, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            accounts = accounts or [a.get('name') for a in config.get('wechat_public_accounts', [])]

    if not accounts:
        print("请提供公众号名称列表或配置文件")
        return

    # 采集内容
    articles = scraper.collect_all(accounts, args.limit, args.interval)
    print(f"共采集 {len(articles)} 篇文章")

    # 过滤内容
    filter_obj = ContentFilter(args.keywords)
    filtered = filter_obj.filter_articles(articles)
    print(f"过滤后保留 {len(filtered)} 篇文章")

    # 提取观点
    enhanced = [extract_insurance_insights(a, args.llm_api) for a in filtered]

    # 格式化输出
    md_content = format_as_markdown(enhanced)

    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(md_content)
        print(f"已保存至: {args.output}")
    else:
        print("\n" + md_content)

    # 输出 JSON 格式（供其他程序使用）
    print("\n--- JSON OUTPUT ---")
    print(json.dumps(enhanced, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
