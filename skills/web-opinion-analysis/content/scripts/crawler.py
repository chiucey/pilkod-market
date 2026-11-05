#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
网页舆情分析 - 网页爬取模块
自动爬取指定网页的正文内容，过滤广告、导航等无关信息
"""

import re
import json
import sys
import argparse
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
import chardet


class WebCrawler:
    """网页爬取器"""

    # 需要过滤的HTML标签
    IGNORE_TAGS = [
        "script",
        "style",
        "nav",
        "header",
        "footer",
        "aside",
        "iframe",
        "noscript",
        "meta",
        "link",
        "button",
        "input",
        "form",
        "select",
        "textarea",
        "svg",
        "canvas",
    ]

    # 需要保留的有效标签（包含正文内容）
    VALID_TAGS = [
        "p",
        "div",
        "span",
        "article",
        "section",
        "main",
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
        "li",
        "td",
        "th",
        "blockquote",
    ]

    # 短文本阈值（少于此字符数的文本将被过滤）
    MIN_TEXT_LENGTH = 20

    # 常见的广告/无关内容关键词
    AD_KEYWORDS = [
        "广告",
        "推广",
        "赞助",
        "声明",
        "免责声明",
        "版权所有",
        "关注我们",
        "扫码关注",
        "微信公众号",
        "新浪微博",
        "合作伙伴",
        "loading",
        "loading...",
        "加载中",
        "更多精彩内容",
        "copyright",
        "all rights reserved",
        "沪ICP备",
        "京ICP备",
        "浙ICP备",
        "鄂ICP备",
    ]

    def __init__(self, timeout=30, user_agent=None):
        """
        初始化爬取器

        Args:
            timeout: 请求超时时间（秒）
            user_agent: 自定义User-Agent
        """
        self.timeout = timeout
        self.user_agent = user_agent or (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )

    def detect_encoding(self, response):
        """
        自动检测网页编码

        Args:
            response: requests响应对象

        Returns:
            编码字符串
        """
        # 首先尝试从响应头获取编码
        encoding = response.encoding

        # 如果响应头没有编码或编码不明确，使用chardet检测
        if not encoding or encoding.lower() in ["iso-8859-1", "latin1"]:
            detected = chardet.detect(response.content)
            encoding = detected.get("encoding", "utf-8")

        # 常见编码映射
        encoding_map = {"gb2312": "gbk", "gb18030": "gbk", "ascii": "utf-8"}
        return encoding_map.get(encoding.lower(), encoding)

    def fetch_page(self, url):
        """
        获取网页内容

        Args:
            url: 网页URL

        Returns:
            包含状态和内容的字典
        """
        try:
            # 验证URL格式
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                return {"success": False, "error": "无效的URL格式"}

            headers = {
                "User-Agent": self.user_agent,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
                "Accept-Encoding": "gzip, deflate",
                "Connection": "keep-alive",
            }

            response = requests.get(url, headers=headers, timeout=self.timeout)
            response.encoding = self.detect_encoding(response)

            return {
                "success": True,
                "content": response.text,
                "status_code": response.status_code,
                "url": response.url,
                "encoding": response.encoding,
            }

        except requests.exceptions.Timeout:
            return {"success": False, "error": "请求超时"}
        except requests.exceptions.ConnectionError:
            return {"success": False, "error": "连接失败，请检查网络或URL是否正确"}
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": f"请求异常: {str(e)}"}

    def extract_title(self, soup):
        """
        提取网页标题

        Args:
            soup: BeautifulSoup对象

        Returns:
            标题字符串
        """
        # 尝试多种方式获取标题
        title_tag = soup.find("title")
        if title_tag:
            return title_tag.get_text(strip=True)

        # 查找h1标签
        h1_tag = soup.find("h1")
        if h1_tag:
            return h1_tag.get_text(strip=True)

        # 查找meta标题
        meta_title = soup.find("meta", attrs={"name": "title"})
        if meta_title and meta_title.get("content"):
            return meta_title["content"]

        return "无标题"

    def is_ad_content(self, text):
        """
        判断是否为广告/无关内容

        Args:
            text: 文本内容

        Returns:
            True表示是广告内容，False表示正常内容
        """
        text_lower = text.lower()

        # 检查是否包含广告关键词
        for keyword in self.AD_KEYWORDS:
            if keyword in text:
                return True

        # 检查是否全为特殊字符
        if re.match(r"^[\s\d\W]+$", text):
            return True

        return False

    def extract_text(self, soup):
        """
        提取网页正文内容

        Args:
            soup: BeautifulSoup对象

        Returns:
            过滤后的正文文本列表
        """
        # 克隆soup，避免修改原对象
        soup_copy = BeautifulSoup(str(soup), "lxml")

        # 移除不需要的标签
        for tag in soup_copy.find_all(self.IGNORE_TAGS):
            tag.decompose()

        # 提取有效标签的内容
        paragraphs = []
        for tag in soup_copy.find_all(self.VALID_TAGS):
            text = tag.get_text(strip=True)

            # 过滤短文本和广告内容
            if len(text) >= self.MIN_TEXT_LENGTH and not self.is_ad_content(text):
                # 清理多余空白
                text = re.sub(r"\s+", " ", text)
                paragraphs.append(text)

        # 去重（保留首次出现）
        seen = set()
        unique_paragraphs = []
        for p in paragraphs:
            # 使用前50个字符作为去重键
            key = p[:50]
            if key not in seen:
                seen.add(key)
                unique_paragraphs.append(p)

        return unique_paragraphs

    def crawl(self, url):
        """
        执行爬取

        Args:
            url: 网页URL

        Returns:
            爬取结果字典
        """
        # 获取网页
        fetch_result = self.fetch_page(url)
        if not fetch_result["success"]:
            return fetch_result

        # 解析HTML
        try:
            soup = BeautifulSoup(fetch_result["content"], "lxml")
        except Exception as e:
            return {"success": False, "error": f"HTML解析失败: {str(e)}"}

        # 提取标题
        title = self.extract_title(soup)

        # 提取正文
        paragraphs = self.extract_text(soup)
        full_text = "\n\n".join(paragraphs)

        # 检查是否有足够的内容
        if len(full_text) < 100:
            return {"success": False, "error": "网页无足够有效正文进行分析"}

        return {
            "success": True,
            "url": url,
            "final_url": fetch_result.get("url", url),
            "title": title,
            "text": full_text,
            "paragraphs": paragraphs,
            "paragraph_count": len(paragraphs),
            "text_length": len(full_text),
            "encoding": fetch_result.get("encoding", "utf-8"),
            "crawl_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="网页舆情分析 - 网页爬取工具")
    parser.add_argument("url", help="要爬取的网页URL")
    parser.add_argument("-o", "--output", help="输出JSON文件路径")
    parser.add_argument(
        "-t", "--timeout", type=int, default=30, help="请求超时时间（秒）"
    )

    args = parser.parse_args()

    # 执行爬取
    crawler = WebCrawler(timeout=args.timeout)
    result = crawler.crawl(args.url)

    # 输出结果
    if result["success"]:
        print(f"✅ 爬取成功")
        print(f"📄 标题: {result['title']}")
        print(f"📝 正文长度: {result['text_length']} 字符")
        print(f"📑 段落数: {result['paragraph_count']}")

        # 保存到文件
        if args.output:
            output_data = {
                "url": result["url"],
                "final_url": result["final_url"],
                "title": result["title"],
                "text": result["text"],
                "paragraphs": result["paragraphs"],
                "paragraph_count": result["paragraph_count"],
                "text_length": result["text_length"],
                "crawl_time": result["crawl_time"],
            }
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(output_data, f, ensure_ascii=False, indent=2)
            print(f"💾 已保存到: {args.output}")
    else:
        print(f"❌ 爬取失败: {result['error']}")
        sys.exit(1)


if __name__ == "__main__":
    main()
