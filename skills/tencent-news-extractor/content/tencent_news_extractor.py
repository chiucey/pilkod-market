#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tencent News Structured Data Extractor
Extract title, author, publish time, and body from Tencent News HTML pages
"""

import re
import json
from html.parser import HTMLParser
from typing import Dict, List, Optional
from pathlib import Path


class TencentNewsExtractor(HTMLParser):
    """Tencent News HTML Parser"""

    def __init__(self):
        super().__init__()
        self.title = ""
        self.author = ""
        self.publish_time = ""
        self.body = []
        self.current_text = ""
        self.in_article_title = False
        self.in_media_name = False
        self.in_media_meta = False
        self.in_article_content = False
        self.in_rich_media_content = False
        self.in_paragraph = False
        self.paragraph_count = 0
        self.skip_current_text = False

    def handle_starttag(self, tag: str, attrs: List[tuple]) -> None:
        attrs_dict = dict(attrs)

        if tag == "h1" and attrs_dict.get("id") == "article-title":
            self.in_article_title = True
            self.current_text = ""
        elif tag == "p" and attrs_dict.get("class") == "media-name":
            self.in_media_name = True
            self.current_text = ""
            self.skip_current_text = False
        elif tag == "p" and attrs_dict.get("class") == "media-meta":
            self.in_media_meta = True
            self.paragraph_count = 0
            self.current_text = ""
        elif tag == "span" and self.in_media_meta:
            if self.paragraph_count == 0:
                self.current_text = ""
        elif tag == "div" and attrs_dict.get("id") == "article-content":
            self.in_article_content = True
        elif tag == "div" and attrs_dict.get("class") == "rich_media_content":
            self.in_rich_media_content = True
        elif tag == "p" and self.in_rich_media_content:
            self.in_paragraph = True
            self.current_text = ""
        elif tag == "a" and self.in_media_name:
            self.skip_current_text = False
        elif tag == "img" and self.in_media_name:
            self.skip_current_text = True

    def handle_endtag(self, tag: str) -> None:
        if tag == "h1" and self.in_article_title:
            if self.current_text.strip():
                self.title = self.current_text.strip()
            self.in_article_title = False
        elif tag == "p" and self.in_media_name:
            if not self.skip_current_text:
                text = self.current_text.strip()
                if text and "媒体" not in text and "发布" not in text:
                    self.author = text
            self.in_media_name = False
        elif tag == "p" and self.in_media_meta:
            self.in_media_meta = False
        elif tag == "span" and self.in_media_meta and self.paragraph_count == 0:
            self.publish_time = self.current_text.strip()
            self.paragraph_count += 1
        elif tag == "div" and self.in_rich_media_content:
            self.in_rich_media_content = False
        elif tag == "div" and self.in_article_content:
            self.in_article_content = False
        elif tag == "p" and self.in_paragraph:
            text = self.current_text.strip()
            if text and len(text) > 5:
                self.body.append(text)
            self.in_paragraph = False

    def handle_data(self, data: str) -> None:
        if self.skip_current_text:
            return
        if self.in_article_title or self.in_media_name or self.in_media_meta or self.in_paragraph:
            self.current_text += data

    def get_result(self) -> Dict:
        """Get extraction result"""
        return {
            "title": self.title,
            "author": self.author,
            "publish_time": self.publish_time,
            "body": self.body
        }


def extract_from_html(html_content: str) -> Dict:
    """
    Extract structured data from Tencent News HTML content

    Args:
        html_content: HTML string content

    Returns:
        Dictionary containing title, author, publish_time, body
    """
    parser = TencentNewsExtractor()
    parser.feed(html_content)
    result = parser.get_result()

    if not result["title"]:
        title_match = re.search(r'<title>([^<]+)</title>', html_content)
        if title_match:
            result["title"] = title_match.group(1).replace("_腾讯新闻", "")

    return result


def extract_from_file(file_path: str) -> Dict:
    """
    Extract structured data from Tencent News HTML file

    Args:
        file_path: HTML file path

    Returns:
        Dictionary containing title, author, publish_time, body
    """
    file_path = Path(file_path)
    with open(file_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    return extract_from_html(html_content)


def to_json(result: Dict, indent: int = 2) -> str:
    """
    Convert extraction result to JSON format string

    Args:
        result: Extraction result dictionary
        indent: JSON indentation spaces

    Returns:
        JSON format string
    """
    return json.dumps(result, ensure_ascii=False, indent=indent)


def main():
    """Main function: CLI entry point"""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python tencent_news_extractor.py <html_file>")
        print("Example: python tencent_news_extractor.py news.html")
        sys.exit(1)

    file_path = sys.argv[1]

    try:
        result = extract_from_file(file_path)
        print(to_json(result))
    except FileNotFoundError:
        print(f"Error: File not found: {file_path}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()