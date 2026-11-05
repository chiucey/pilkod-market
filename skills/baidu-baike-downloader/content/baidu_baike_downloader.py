#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
百度百科下载器 - 下载百度百科页面并解析为JSON格式
"""

import requests
from bs4 import BeautifulSoup
import json
import re
import sys
import argparse
from urllib.parse import quote


class BaiduBaikeDownloader:
    """百度百科页面下载和解析器"""

    BASE_URL = "https://baike.baidu.com/item/{item_name}"
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": self.USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
        })

    def download(self, item_name, max_retries=3):
        """
        下载百度百科页面

        Args:
            item_name: 词条名称
            max_retries: 最大重试次数

        Returns:
            原始HTML内容
        """
        encoded_name = quote(item_name)
        url = self.BASE_URL.format(item_name=encoded_name)

        for attempt in range(max_retries):
            try:
                response = self.session.get(url, timeout=30)
                response.raise_for_status()

                # 尝试多种编码
                encodings = ['utf-8', 'gbk', 'gb2312', 'gb18030']
                content = response.content

                for encoding in encodings:
                    try:
                        content = response.content.decode(encoding)
                        break
                    except (UnicodeDecodeError, LookupError):
                        continue

                return content, url

            except requests.RequestException as e:
                if attempt < max_retries - 1:
                    continue
                raise Exception(f"下载失败: {str(e)}")

        return None, url

    def parse(self, html_content, item_name):
        """
        解析HTML内容为JSON结构

        Args:
            html_content: HTML内容
            item_name: 词条名称

        Returns:
            解析后的JSON数据
        """
        soup = BeautifulSoup(html_content, 'lxml')

        result = {
            "title": item_name,
            "url": self.BASE_URL.format(item_name=quote(item_name)),
            "summary": "",
            "categories": [],
            "sections": [],
            "images": [],
            "references": []
        }

        # 提取标题
        title_elem = soup.find('h1', class_='lemmaTitle_BIG__Gair2') or \
                     soup.find('h1', class_='lemma-title') or \
                     soup.find('div', class_='lemma-title')
        if title_elem:
            result["title"] = title_elem.get_text(strip=True)

        # 提取简介
        summary_elem = soup.find('div', class_='lemma-summary') or \
                       soup.find('div', class_='description')
        if summary_elem:
            result["summary"] = self._clean_text(summary_elem.get_text())

        # 提取分类标签
        category_elems = soup.find_all('a', class_='tag-link')
        result["categories"] = [self._clean_text(cat.get_text()) for cat in category_elems]

        # 提取章节内容
        sections = []
        content_elem = soup.find('div', class_='content')
        if content_elem:
            # 查找所有标题和内容对
            current_section = {"title": "", "content": ""}

            for elem in content_elem.find_all(['h2', 'h3', 'h4', 'p', 'ul', 'ol']):
                if elem.name in ['h2', 'h3', 'h4']:
                    # 保存上一个章节
                    if current_section["title"] or current_section["content"]:
                        sections.append(current_section)

                    current_section = {
                        "title": self._clean_text(elem.get_text()),
                        "content": ""
                    }
                elif elem.name in ['p', 'ul', 'ol']:
                    text = self._clean_text(elem.get_text())
                    if text:
                        current_section["content"] += text + "\n\n"

            # 添加最后一个章节
            if current_section["title"] or current_section["content"]:
                sections.append(current_section)

        result["sections"] = sections

        # 提取图片
        images = []
        for img in soup.find_all('img', class_='picture'):
            img_info = {
                "url": img.get('src', img.get('data-src', '')),
                "caption": img.get('alt', '')
            }
            if img_info["url"]:
                images.append(img_info)

        # 如果没有找到，尝试其他图片
        if not images:
            for img in soup.find_all('img'):
                src = img.get('src', img.get('data-src', ''))
                if src and 'baike' in src.lower():
                    images.append({
                        "url": src,
                        "caption": img.get('alt', '')
                    })

        result["images"] = images[:10]  # 限制图片数量

        # 提取参考资料
        references = []
        ref_list = soup.find('ol', class_='references')
        if ref_list:
            for ref in ref_list.find_all('li'):
                link = ref.find('a')
                if link:
                    references.append({
                        "title": self._clean_text(ref.get_text()),
                        "url": link.get('href', '')
                    })
        result["references"] = references[:20]  # 限制参考数量

        return result

    def _clean_text(self, text):
        """清理文本内容"""
        if not text:
            return ""
        # 移除多余空白
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def run(self, item_name, output_file=None):
        """
        运行下载和解析流程

        Args:
            item_name: 词条名称
            output_file: 可选的输出文件路径

        Returns:
            解析后的JSON数据
        """
        print(f"正在下载: {item_name}")

        html_content, url = self.download(item_name)
        if not html_content:
            raise Exception("下载页面失败")

        print(f"正在解析: {item_name}")
        data = self.parse(html_content, item_name)

        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"结果已保存到: {output_file}")

        return data


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='百度百科下载器 - 下载并解析百度百科页面')
    parser.add_argument('item', help='词条名称')
    parser.add_argument('-o', '--output', help='输出JSON文件路径')
    parser.add_argument('-p', '--pretty', action='store_true', help='美化输出')

    args = parser.parse_args()

    downloader = BaiduBaikeDownloader()

    try:
        data = downloader.run(args.item, args.output)

        if args.pretty or not args.output:
            print(json.dumps(data, ensure_ascii=False, indent=2))
        elif not args.pretty:
            print(json.dumps(data, ensure_ascii=False))

    except Exception as e:
        print(f"错误: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
