#!/usr/bin/env python3
"""
微信公众号文章爬虫
通过模拟手机UA绕过反爬，提取文章标题、描述和正文
"""

import re
import sys
import json
import argparse
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
from html.parser import HTMLParser


# 手机端User-Agent
MOBILE_UA = (
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
    "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 "
    "Mobile/15E148 Safari/604.1"
)

# 备用User-Agent列表
USER_AGENTS = [
    MOBILE_UA,
    "Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; U; Android 13; zh-cn; Pixel 7 Build/TP1A.220624.014) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/100.0.4896.58 Mobile Safari/537.36",
]


class WechatContentParser(HTMLParser):
    """解析微信公众号文章HTML，提取正文内容"""

    def __init__(self):
        super().__init__()
        self.title = ""
        self.description = ""
        self.author = ""
        self.content = []
        self.current_tag = None
        self.in_article = False
        self.in_script = False
        self.in_style = False
        self.in_title = False
        self.in_meta = False
        self.current_attrs = {}

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)

        if tag == "meta":
            # 提取og标签
            if attrs_dict.get("property") == "og:title":
                self.title = attrs_dict.get("content", "")
            elif attrs_dict.get("property") == "og:description":
                self.description = attrs_dict.get("content", "")
            elif attrs_dict.get("name") == "author":
                self.author = attrs_dict.get("content", "")

        elif tag == "title":
            self.in_title = True

        elif tag == "script":
            self.in_script = True

        elif tag == "style":
            self.in_style = True

        elif tag == "article" or attrs_dict.get("id") == "js_content":
            self.in_article = True
            self.current_tag = tag

        elif self.in_article and tag in ("p", "section", "h1", "h2", "h3", "h4", "blockquote"):
            self.current_tag = tag

    def handle_endtag(self, tag):
        if tag == "script":
            self.in_script = False
        elif tag == "style":
            self.in_style = False
        elif tag == "title":
            self.in_title = False
        elif tag in ("article", "section") and self.in_article:
            self.in_article = False
            self.current_tag = None
        elif self.in_article and tag == self.current_tag:
            self.current_tag = None

    def handle_data(self, data):
        if self.in_script or self.in_style:
            return

        text = data.strip()
        if not text:
            return

        if self.in_title:
            if not self.title:
                self.title = text

        if self.in_article:
            # 过滤微信干扰元素
            if "opr" in text or "javascript" in text.lower():
                return
            self.content.append(text)

    def get_result(self):
        return {
            "title": self.title.strip(),
            "description": self.description.strip(),
            "author": self.author.strip(),
            "content": "\n\n".join(self.content),
            "word_count": len("".join(self.content))
        }


def fetch_article(url: str, user_agent: str = None) -> str:
    """
    获取微信文章HTML源码

    Args:
        url: 文章URL
        user_agent: 自定义UA，默认使用手机UA

    Returns:
        HTML源码字符串
    """
    ua = user_agent or MOBILE_UA

    headers = {
        "User-Agent": ua,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }

    try:
        req = Request(url, headers=headers)
        with urlopen(req, timeout=15) as response:
            # 处理编码
            content = response.read()
            charset = response.headers.get_content_charset() or "utf-8"
            return content.decode(charset, errors="replace")
    except HTTPError as e:
        raise RuntimeError(f"HTTP错误: {e.code} - {e.reason}")
    except URLError as e:
        raise RuntimeError(f"URL错误: {e.reason}")
    except Exception as e:
        raise RuntimeError(f"请求失败: {str(e)}")


def parse_article(html: str) -> dict:
    """
    解析HTML提取文章内容

    Args:
        html: HTML源码

    Returns:
        包含title/description/content的字典
    """
    parser = WechatContentParser()
    parser.feed(html)
    return parser.get_result()


def scrape_wechat_article(url: str, output_format: str = "json", output_file: str = None) -> dict:
    """
    主函数：爬取微信公众号文章

    Args:
        url: 微信文章链接
        output_format: 输出格式 (json/text/markdown)
        output_file: 输出文件路径

    Returns:
        解析后的文章数据
    """
    # 验证URL
    if not url:
        raise ValueError("URL不能为空")

    if "mp.weixin.qq.com" not in url:
        raise ValueError("仅支持微信公众号文章链接 (mp.weixin.qq.com)")

    print(f"正在爬取: {url}")

    # 获取HTML
    html = fetch_article(url)

    # 解析内容
    article = parse_article(html)

    # 验证结果
    if not article["title"] and not article["content"]:
        raise RuntimeError("未能提取到文章内容，可能需要登录或链接已失效")

    # 格式化输出
    if output_format == "text":
        output = f"# {article['title']}\n\n作者: {article['author']}\n\n{article['content']}"
    elif output_format == "markdown":
        output = f"# {article['title']}\n\n> {article['description']}\n\n**作者**: {article['author']}\n\n---\n\n{article['content']}"
    else:
        output = article

    # 保存到文件
    if output_file:
        ext = output_file.split(".")[-1] if "." in output_file else "txt"
        with open(output_file, "w", encoding="utf-8") as f:
            if ext == "json":
                json.dump(article, f, ensure_ascii=False, indent=2)
            else:
                f.write(str(output) if isinstance(output, str) else json.dumps(output, ensure_ascii=False, indent=2))
        print(f"已保存到: {output_file}")

    return article


def main():
    parser = argparse.ArgumentParser(description="微信公众号文章爬虫")
    parser.add_argument("url", help="微信文章链接")
    parser.add_argument("-o", "--output", help="输出文件路径")
    parser.add_argument("-f", "--format", choices=["json", "text", "markdown"], default="json", help="输出格式")

    args = parser.parse_args()

    try:
        result = scrape_wechat_article(args.url, args.format, args.output)

        if not args.output:
            print("\n" + "=" * 50)
            print(f"标题: {result['title']}")
            print(f"作者: {result['author']}")
            print(f"字数: {result['word_count']}")
            print("=" * 50)
            print("\n正文预览:")
            print(result["content"][:500] + "..." if len(result["content"]) > 500 else result["content"])

    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
