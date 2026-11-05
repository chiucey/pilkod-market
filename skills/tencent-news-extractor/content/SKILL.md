---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 94a159ca17b89d8fcba0c9598a57fcce
    PropagateID: 94a159ca17b89d8fcba0c9598a57fcce
    ReservedCode1: 3044022039b371fc68398e0035432e2b485ddacbeca1b4e2270e406965337412722abffa022041d49ef25f24498f831413c949e035a0684d2351aab537ce5c355d0023a7d0ce
    ReservedCode2: 30460221009f040d6d910456bfc78921231dcc16207450dd0a7102f3f988b154c501a3c663022100bb393ad54bf69199a9b2ebfc4db96ef7aecbd7ea9eca7cd52350f635da0f12ae
description: Extract structured data (title, author, publish_time, body) from Tencent News web pages. Use when users need to extract article content, parse news metadata, or batch process Tencent News pages.
name: tencent-news-extractor
---

# Tencent News Structured Data Extractor

## Overview

This skill extracts structured data from Tencent News web pages and outputs in JSON format. Extracted fields include:

- **Title**: Article main title
- **Author**: Article author or publishing media name
- **Publish Time**: Article publication date and time
- **Body**: List of article body paragraphs

## HTML Structure Analysis

Tencent News page HTML structure:

```html
<!-- Title -->
<title>Article Title_Tencent News</title>
<h1 id="article-title">Article Title</h1>

<!-- Author Info -->
<div id="article-author">
    <div class="media-info">
        <p class="media-name">Author/Media Name</p>
        <p class="media-meta">
            <span>2026-05-29 08:21</span>  <!-- Publish Time -->
            <span>Published in Beijing</span>
            <span>Official Account</span>
       </p>
    </div>
</div>

<!-- Body Content -->
<div id="article-content">
    <div class="rich_media_content">
        <p>Paragraph 1</p>
        <p>Paragraph 2</p>
        ...
    </div>
</div>
```

## Extraction Logic

### 1. Title Extraction

- Prefer using text content from `<h1 id="article-title">`
- Fallback: Use `<title>` tag and remove trailing "_腾讯新闻" suffix

### 2. Author Extraction

- Extract text from `<p class="media-name">`
- This element is inside `<div id="article-author">`

### 3. Publish Time Extraction

- Extract from the first `<span>` element inside `<p class="media-meta">`
- Format: `YYYY-MM-DD HH:MM`

### 4. Body Extraction

- Extract from `<div class="rich_media_content">` inside `<div id="article-content">`
- Collect direct text content from all `<p>` tags
- Filter out image captions and empty paragraphs
- Preserve original paragraph order

## Output Format

```json
{
  "title": "Article Title",
  "author": "Author/Media Name",
  "publish_time": "2026-05-29 08:21",
  "body": [
    "Paragraph text 1",
    "Paragraph text 2",
    "Paragraph text 3"
  ]
}
```

## Python Implementation

```python
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
    from pathlib import Path
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
```

## Usage Examples

### Command Line Usage

```bash
python tencent_news_extractor.py news.html
```

### Output Example

```json
{
  "title": "从各省份"十五五"规划纲要看全国发展一盘棋",
  "author": "新华社全媒报道平台",
  "publish_time": "2026-05-29 08:21",
  "body": [
    ""十五五"规划恢弘起笔，高质量发展击鼓催征。",
    "近日，河南省国民经济和社会发展第十五个五年规划纲要对外发布。至此，全国31个省份的"十五五"规划纲要全部发布。",
    "各省份"十五五"规划纲要根据党的二十届四中全会通过的"十五五"规划建议..."
  ]
}
```

## Notes

1. **Encoding**: HTML files should use UTF-8 encoding
2. **Paragraph Filtering**: Automatically filters short paragraphs (less than 5 characters) and image captions
3. **Author Detection**: Prioritizes author info in `<p class="media-name">`
4. **Time Format**: Publish time format is `YYYY-MM-DD HH:MM`

## Dependencies

- Python 3.6+
- No additional dependencies required, uses only standard library