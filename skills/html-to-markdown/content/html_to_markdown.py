#!/usr/bin/env python3
"""
HTML to Markdown Converter
智能网页内容提取与 Markdown 转换工具
"""

import argparse
import html
import json
import os
import re
import sys
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import requests
import html2text


class StrategyType(Enum):
    """提取策略类型"""
    AUTO = "auto"
    FAST = "fast"
    FULL = "full"
    AUTH = "auth"
    WECHAT = "wechat"


@dataclass
class ExtractionResult:
    """提取结果数据类"""
    success: bool = False
    markdown: str = ""
    raw_content: str = ""
    strategy_used: StrategyType = StrategyType.AUTO
    quality_score: float = 0.0
    steps: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    is_wechat_extraction: bool = False
    wechat_fallback_used: bool = False


class HTMLToMarkdownConverter:
    """HTML 转 Markdown 转换器"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化转换器

        Args:
            config: 配置字典
                - body_width: 行宽，0 表示不换行
                - ignore_images: 是否忽略图片
                - timeout: 请求超时秒数
        """
        self.config = config or {}
        self.body_width = self.config.get('body_width', 0)
        self.ignore_images = self.config.get('ignore_images', False)
        self.timeout = self.config.get('timeout', 30)

        self.h = html2text.HTML2Text()
        self.h.body_width = self.body_width
        self.h.ignore_images = self.ignore_images
        self.h.unicode_snob = True
        self.h.skip_internal_links = True
        self.h.ignore_emphasis = False
        self.h.dash_delimiter = '-'
        self.h.asterisk_delimiter = '*'
        self.h.wrap_links = False
        self.h.wrap_lists = True

    def convert_url(self, url: str) -> str:
        """
        从 URL 获取并转换 HTML 为 Markdown

        Args:
            url: 网页 URL

        Returns:
            Markdown 格式的文本
        """
        try:
            response = requests.get(url, timeout=self.timeout, verify=False)
            response.encoding = response.apparent_encoding or 'utf-8'
            return self.convert_raw_html(response.text)
        except requests.RequestException as e:
            return f"# Error\n\nFailed to fetch URL: {str(e)}"

    def convert_file(self, file_path: str, output_path: Optional[str] = None) -> str:
        """
        转换本地 HTML 文件

        Args:
            file_path: HTML 文件路径
            output_path: 可选的输出文件路径

        Returns:
            Markdown 格式的文本
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            markdown = self.convert_raw_html(html_content)

            if output_path:
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(markdown)

            return markdown
        except Exception as e:
            return f"# Error\n\nFailed to read file: {str(e)}"

    def convert_raw_html(self, html_content: str) -> str:
        """
        转换 HTML 字符串为 Markdown

        Args:
            html_content: HTML 内容

        Returns:
            Markdown 格式的文本
        """
        html_content = html.unescape(html_content)
        markdown = self.h.handle(html_content)
        return markdown.strip()

    @staticmethod
    def is_wechat_url(url: str) -> bool:
        """
        检测 URL 是否为微信公众号文章

        Args:
            url: 待检测的 URL

        Returns:
            是否为微信文章 URL
        """
        return 'mp.weixin.qq.com' in url

    def search_wechat_articles(self, keyword: str, max_results: int = 5) -> List[Dict[str, str]]:
        """
        通过搜狗搜索微信公众号文章

        Args:
            keyword: 搜索关键词
            max_results: 最大返回结果数

        Returns:
            文章列表，每项包含 title, author, description, url
        """
        articles = []

        try:
            search_url = f"https://weixin.sogou.com/weixin?type=2&s_from=input&query={keyword}&ie=utf8&_sug_=n&_sug_type_="

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            }

            response = requests.get(search_url, headers=headers, timeout=self.timeout, verify=False)
            response.encoding = 'utf-8'

            article_pattern = r'<div class="txt-box">(.*?)</div>\s*</li>'
            matches = re.findall(article_pattern, response.text, re.DOTALL)

            for match in matches[:max_results]:
                title_match = re.search(r'<h3[^>]*>.*?<a[^>]*>(.*?)</a>', match, re.DOTALL)
                author_match = re.search(r'账号.*?<em>(.*?)</em>', match, re.DOTALL)
                desc_match = re.search(r'<p class="txt-info">(.*?)</p>', match, re.DOTALL)
                url_match = re.search(r'href="(https://mp\.weixin\.qq\.com/s[^"]+)"', match)

                if title_match:
                    article = {
                        'title': self._clean_html(title_match.group(1)),
                        'author': self._clean_html(author_match.group(1)) if author_match else 'Unknown',
                        'description': self._clean_html(desc_match.group(1)) if desc_match else '',
                        'url': url_match.group(1) if url_match else ''
                    }
                    articles.append(article)

        except Exception as e:
            print(f"搜索失败: {str(e)}")

        return articles

    @staticmethod
    def _clean_html(text: str) -> str:
        """清理 HTML 标签和实体"""
        text = re.sub(r'<[^>]+>', '', text)
        text = html.unescape(text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()


class SmartExtractor:
    """智能内容提取器"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化智能提取器

        Args:
            config: 配置字典
                - strategy: 提取策略 (auto, fast, full, auth)
                - js_rendering: 是否支持 JS 渲染
                - auth_support: 是否支持认证
                - debug: 调试模式
                - verbose: 详细输出
        """
        self.config = config or {}
        self.strategy = StrategyType(self.config.get('strategy', 'auto'))
        self.js_rendering = self.config.get('js_rendering', True)
        self.auth_support = self.config.get('auth_support', True)
        self.debug = self.config.get('debug', False)
        self.verbose = self.config.get('verbose', False)

        self.converter = HTMLToMarkdownConverter({
            'body_width': 0,
            'ignore_images': False,
            'timeout': self.config.get('timeout', 30)
        })

    def smart_extract(self, source: str, options: Optional[Dict[str, Any]] = None) -> ExtractionResult:
        """
        智能提取内容

        Args:
            source: URL 或文件路径
            options: 可选的额外选项

        Returns:
            ExtractionResult 对象
        """
        result = ExtractionResult()
        options = options or {}

        if self.verbose:
            print(f"[SmartExtractor] 开始提取: {source}")

        if source.startswith(('http://', 'https://')):
            return self._extract_from_url(source, options)
        elif os.path.isfile(source):
            return self._extract_from_file(source, options)
        else:
            result.errors.append(f"无效的源: {source}")
            return result

    def _extract_from_url(self, url: str, options: Dict[str, Any]) -> ExtractionResult:
        """从 URL 提取内容"""
        result = ExtractionResult()
        result.steps.append(f"开始提取 URL: {url}")

        if HTMLToMarkdownConverter.is_wechat_url(url):
            return self._extract_wechat_article(url)

        strategy = options.get('strategy', self.strategy.value)

        try:
            result.strategy_used = StrategyType(strategy)
            result.steps.append(f"使用策略: {strategy}")

            markdown = self.converter.convert_url(url)
            result.markdown = markdown
            result.raw_content = markdown
            result.success = True
            result.quality_score = self._calculate_quality(markdown)
            result.steps.append(f"提取完成，质量评分: {result.quality_score:.2f}")

        except Exception as e:
            result.errors.append(str(e))
            result.steps.append(f"提取失败: {str(e)}")

        return result

    def _extract_from_file(self, file_path: str, options: Dict[str, Any]) -> ExtractionResult:
        """从文件提取内容"""
        result = ExtractionResult()
        result.steps.append(f"开始提取文件: {file_path}")

        try:
            markdown = self.converter.convert_file(file_path)
            result.markdown = markdown
            result.raw_content = markdown
            result.success = True
            result.quality_score = self._calculate_quality(markdown)
            result.steps.append(f"提取完成，质量评分: {result.quality_score:.2f}")

        except Exception as e:
            result.errors.append(str(e))
            result.steps.append(f"提取失败: {str(e)}")

        return result

    def _extract_wechat_article(self, url: str) -> ExtractionResult:
        """提取微信公众号文章"""
        result = ExtractionResult()
        result.is_wechat_extraction = True
        result.steps.append("检测到微信公众号文章")

        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            }

            response = requests.get(url, headers=headers, timeout=30, verify=False)

            if 'var biz = ' in response.text or 'var ct = ' in response.text:
                result.markdown = self._generate_wechat_guide(url, response.text)
                result.success = True
                result.quality_score = 0.5
                result.wechat_fallback_used = True
                result.steps.append("使用降级处理，返回手动获取指南")
            else:
                result.markdown = self.converter.convert_raw_html(response.text)
                result.success = True
                result.quality_score = self._calculate_quality(result.markdown)
                result.steps.append("成功提取微信文章")

        except Exception as e:
            result.errors.append(str(e))
            result.markdown = self._generate_wechat_guide(url, "")
            result.success = True
            result.quality_score = 0.3
            result.wechat_fallback_used = True

        return result

    def _generate_wechat_guide(self, url: str, html_content: str) -> str:
        """生成微信公众号文章处理指南"""
        guide = """# 微信公众号文章提取指南

由于微信公众号的特殊限制，无法直接自动提取全文内容。

## 获取方法

### 方法一：搜狗微信搜索
1. 访问 https://weixin.sogou.com/
2. 搜索文章标题或关键词
3. 从搜索结果中获取文章摘要

### 方法二：浏览器手动保存
1. 在电脑浏览器中打开文章链接
2. 按 Ctrl + A 全选页面
3. 按 Ctrl + C 复制内容
4. 粘贴到文本编辑器中保存

### 方法三：使用开发者工具
1. 在浏览器中打开文章
2. 按 F12 打开开发者工具
3. 切换到 Network 标签
4. 刷新页面，找到主要的 HTML 请求
5. 复制响应内容

## 文章链接
"""
        guide += f"\n**URL**: {url}\n"
        return guide

    @staticmethod
    def _calculate_quality(markdown: str) -> float:
        """
        计算提取质量评分

        Args:
            markdown: Markdown 内容

        Returns:
            质量评分 (0.0-1.0)
        """
        if not markdown or len(markdown) < 50:
            return 0.1

        score = 0.5

        has_title = bool(re.search(r'^#+\s+.+', markdown, re.MULTILINE))
        has_paragraphs = len(re.findall(r'\n\n+', markdown)) > 2
        has_lists = bool(re.search(r'^[\*\-\+]\s+|^\d+\.\s+', markdown, re.MULTILINE))

        if has_title:
            score += 0.15
        if has_paragraphs:
            score += 0.2
        if has_lists:
            score += 0.15

        char_count = len(markdown)
        if char_count > 500:
            score += 0.1

        error_patterns = ['Error', 'Failed', 'Not Found', '404']
        error_count = sum(1 for p in error_patterns if p in markdown)
        if error_count > 0:
            score -= min(0.2, error_count * 0.1)

        return max(0.0, min(1.0, score))

    def batch_extract(self, sources: List[str]) -> Dict[str, ExtractionResult]:
        """
        批量提取内容

        Args:
            sources: URL 或文件路径列表

        Returns:
            字典，键为源，值为 ExtractionResult
        """
        results = {}

        for i, source in enumerate(sources):
            if self.verbose:
                print(f"[{i+1}/{len(sources)}] 正在处理: {source}")

            results[source] = self.smart_extract(source)

            if i < len(sources) - 1:
                time.sleep(1)

        return results


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(
        description='HTML to Markdown Converter - 智能网页内容提取与转换工具',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument('-u', '--url', help='要提取的 URL')
    parser.add_argument('-f', '--file', nargs='+', help='HTML 文件路径')
    parser.add_argument('-o', '--output', help='输出文件路径')
    parser.add_argument('-d', '--directory', help='批量输出目录')
    parser.add_argument('-s', '--strategy', default='auto',
                        choices=['auto', 'fast', 'full', 'auth'],
                        help='提取策略')
    parser.add_argument('-w', '--width', type=int, default=0,
                        help='行宽，0 表示不换行')
    parser.add_argument('-i', '--ignore-images', action='store_true',
                        help='忽略图片')
    parser.add_argument('-t', '--timeout', type=int, default=30,
                        help='请求超时秒数')
    parser.add_argument('--search-wechat', metavar='KEYWORD',
                        help='搜索微信公众号文章')
    parser.add_argument('--debug', action='store_true', help='调试模式')
    parser.add_argument('--verbose', action='store_true', help='详细输出')

    args = parser.parse_args()

    if args.search_wechat:
        converter = HTMLToMarkdownConverter({'timeout': args.timeout})
        articles = converter.search_wechat_articles(args.search_wechat)

        if articles:
            print(f"\n找到 {len(articles)} 篇相关文章:\n")
            for i, article in enumerate(articles, 1):
                print(f"--- 文章 {i} ---")
                print(f"标题: {article['title']}")
                print(f"作者: {article['author']}")
                print(f"摘要: {article['description']}")
                print(f"链接: {article['url']}\n")
        else:
            print("未找到相关文章，或搜索被限制（可能需要验证码）")
        return

    if not args.url and not args.file:
        parser.print_help()
        return

    if args.verbose:
        print("[HTML to Markdown] 开始转换...")

    config = {
        'strategy': args.strategy,
        'timeout': args.timeout,
        'verbose': args.verbose,
        'debug': args.debug
    }

    extractor = SmartExtractor(config)
    converter = HTMLToMarkdownConverter({
        'body_width': args.width,
        'ignore_images': args.ignore_images,
        'timeout': args.timeout
    })

    if args.url:
        urls = [u.strip() for u in args.url.split(',')]

        for i, url in enumerate(urls):
            if args.verbose:
                print(f"\n[{i+1}/{len(urls)}] 处理: {url}")

            result = extractor.smart_extract(url)

            if args.output and len(urls) == 1:
                output_path = args.output
            elif args.directory:
                url_hash = str(abs(hash(url)))[:8]
                filename = f"url_{url_hash}.md"
                output_path = os.path.join(args.directory, filename)
            else:
                output_path = None

            if output_path:
                os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(result.markdown)
                if args.verbose:
                    print(f"已保存到: {output_path}")
            else:
                print(result.markdown)

    if args.file:
        for file_path in args.file:
            if args.verbose:
                print(f"\n处理文件: {file_path}")

            if args.output and len(args.file) == 1:
                output_path = args.output
            elif args.directory:
                filename = Path(file_path).stem + '.md'
                output_path = os.path.join(args.directory, filename)
            else:
                output_path = None

            if output_path:
                os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
                markdown = converter.convert_file(file_path, output_path)
                if args.verbose:
                    print(f"已保存到: {output_path}")
            else:
                markdown = converter.convert_file(file_path)
                print(markdown)

    if args.verbose:
        print("\n[HTML to Markdown] 转换完成!")


if __name__ == '__main__':
    main()
