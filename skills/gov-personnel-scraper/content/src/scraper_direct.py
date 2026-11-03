#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
直接抓取版政府人事任免信息爬虫
直接访问已知的国务院公报任免页面
"""

import re
import json
import csv
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from pathlib import Path
import requests
from bs4 import BeautifulSoup


class DirectGovScraper:
    """直接访问爬虫 - 用于抓取已知的任免公报页面"""

    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    }

    def __init__(self, timeout: int = 30):
        self.session = requests.Session()
        self.timeout = timeout

    def get_recent_gongbao_urls(self) -> List[Dict]:
        """
        获取最近几期的国务院公报任免页面URL
        """
        urls = []

        # 尝试从公报索引页面获取
        base_url = "https://www.gov.cn/gongbao"
        try:
            response = self.session.get(
                f"{base_url}/currentissue.htm",
                headers=self.HEADERS,
                timeout=self.timeout
            )

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')

                # 查找任免相关的链接
                links = soup.find_all('a', href=True)
                for link in links:
                    href = link.get('href', '')
                    text = link.get_text(strip=True)

                    if '任免' in text and 'content' in href:
                        full_url = href if href.startswith('http') else f"{base_url}/{href}"
                        urls.append({
                            'title': text,
                            'url': full_url
                        })

        except Exception as e:
            print(f"[爬虫] 获取公报索引失败: {e}")

        # 如果没有找到，返回默认的近期页面
        if not urls:
            # 使用已知的近期任免公报页面
            urls = [
                {'title': '中华人民共和国国务院任免人员 (2026年3月)', 'url': 'https://www.gov.cn/gongbao/2026/issue_12606/202603/content_7061748.html'},
                {'title': '中华人民共和国国务院任免人员 (2026年2月28日)', 'url': 'https://www.gov.cn/gongbao/2026/issue_12586/202602/content_7059932.html'},
                {'title': '中华人民共和国国务院任免人员 (2026年2月20日)', 'url': 'https://www.gov.cn/gongbao/2026/issue_12566/202602/content_7057932.html'},
                {'title': '中华人民共和国国务院任免人员 (2026年2月10日)', 'url': 'https://www.gov.cn/gongbao/2026/issue_12546/202602/content_7057446.html'},
                {'title': '中华人民共和国国务院任免人员 (2026年1月30日)', 'url': 'https://www.gov.cn/gongbao/2026/issue_12526/202601/content_7056482.html'},
            ]

        return urls

    def parse_article(self, url: str, title: str = '') -> List[Dict]:
        """
        解析国务院公报任免文章

        Args:
            url: 文章URL
            title: 文章标题

        Returns:
            提取的人事信息列表
        """
        try:
            response = self.session.get(
                url,
                headers=self.HEADERS,
                timeout=self.timeout
            )

            if response.status_code != 200:
                print(f"[爬虫] 页面访问失败 {response.status_code}: {url}")
                return []

            soup = BeautifulSoup(response.text, 'html.parser')

            # 获取文章正文
            content = soup.find('div', class_=re.compile('content|article|TRS_Editor|zoom'))
            if not content:
                content = soup.find('body')

            if not content:
                print(f"[爬虫] 未找到文章内容: {url}")
                return []

            text = content.get_text(separator='\n', strip=True)

            # 提取任免信息
            records = self._extract_renmian(text, url, title)

            time.sleep(0.5)
            return records

        except Exception as e:
            print(f"[爬虫] 解析失败 {url}: {e}")
            return []

    def _extract_renmian(self, text: str, source_url: str, title: str) -> List[Dict]:
        """
        从文本中提取任免信息
        """
        records = []

        # 按日期分段处理
        # 格式: 2026年2月10日\n任命XXX为YYY。\n任命XXX为YYY。
        lines = text.split('\n')

        current_date = ''

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # 检查是否是日期行
            date_match = re.match(r'(\d{4})年(\d{1,2})月(\d{1,2})日', line)
            if date_match:
                current_date = f"{date_match.group(1)}-{date_match.group(2).zfill(2)}-{date_match.group(3).zfill(2)}"
                continue

            # 处理任命
            if '任命' in line and '为' in line:
                parsed = self._parse_renming(line, current_date, source_url)
                records.extend(parsed)

            # 处理免职
            if '免去' in line:
                parsed = self._parse_mianzhi(line, current_date, source_url)
                records.extend(parsed)

        return records

    def _parse_renming(self, line: str, date: str, source_url: str) -> List[Dict]:
        """解析任命信息"""
        records = []

        # 分割多个人员的任命（可能有分号分隔）
        sentences = re.split(r'[；;]', line)

        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence or '任命' not in sentence:
                continue

            # 格式: 任命XXX为YYY
            match = re.search(r'任命(.+?)为(.+?)[。.]?$', sentence)
            if match:
                name = match.group(1).strip()
                position = match.group(2).strip()

                # 清理职务
                position = re.sub(r'[。；，,]', '', position)

                if self._is_valid_name(name) and position and len(position) > 1:
                    records.append({
                        'name': name,
                        'position': position,
                        'action': '任命',
                        'date': date,
                        'doc_no': '',
                        'source_url': source_url
                    })

        return records

    def _parse_mianzhi(self, line: str, date: str, source_url: str) -> List[Dict]:
        """解析免职信息"""
        records = []

        # 分割可能的多个人员
        sentences = re.split(r'[；;]', line)

        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence or '免去' not in sentence:
                continue

            # 格式: 免去XXX的YYY职务
            match = re.search(r'免去(.+?)(?:的|)(.+?)(?:职务|)[。.]?$', sentence)
            if match:
                name = match.group(1).strip()
                position = match.group(2).strip()

                # 清理
                position = re.sub(r'[。；，,]', '', position)

                if self._is_valid_name(name) and position and len(position) > 1:
                    records.append({
                        'name': name,
                        'position': position,
                        'action': '免去',
                        'date': date,
                        'doc_no': '',
                        'source_url': source_url
                    })

        return records

    def _is_valid_name(self, name: str) -> bool:
        """验证是否为有效姓名"""
        if not name or len(name) < 2 or len(name) > 8:
            return False

        # 排除常见非姓名词
        exclude_words = ['会议', '通知', '决定', '文件', '规定', '条例', '办法']
        if any(word in name for word in exclude_words):
            return False

        return True

    def scrape(self, state_file: str = None, last_24h_only: bool = True) -> List[Dict]:
        """
        执行爬取任务

        Args:
            state_file: 状态文件路径（未使用，保留接口）
            last_24h_only: 是否只抓取最近的数据

        Returns:
            爬取到的人事信息列表
        """
        print("[爬虫] 开始爬取国务院公报任免信息...")
        print("[爬虫] 直接访问已知的任免公报页面")

        all_records = []

        # 获取近期任免页面
        urls = self.get_recent_gongbao_urls()
        print(f"[爬虫] 找到 {len(urls)} 个任免公报页面")

        for item in urls:
            url = item['url']
            title = item['title']
            print(f"[爬虫] 正在解析: {title}")

            records = self.parse_article(url, title)
            print(f"[爬虫] 从 {title} 提取到 {len(records)} 条记录")

            all_records.extend(records)

        # 去重
        unique_records = []
        seen = set()
        for record in all_records:
            key = (record['name'], record['action'], record['position'], record['date'])
            if key not in seen:
                seen.add(key)
                unique_records.append(record)

        print(f"[爬虫] 去重后共 {len(unique_records)} 条人事任免信息")
        return unique_records


def test_direct_scraper():
    """测试直接爬虫"""
    scraper = DirectGovScraper()

    # 获取近期页面
    urls = scraper.get_recent_gongbao_urls()
    print(f"\n获取到 {len(urls)} 个页面")

    for item in urls:
        print(f"  - {item['title']}")

    # 解析第一个页面
    if urls:
        url = urls[0]['url']
        print(f"\n解析: {url}")
        records = scraper.parse_article(url)

        print(f"\n提取到 {len(records)} 条记录:")
        for rec in records:
            print(f"  {rec['date']} | {rec['action']} | {rec['name']} | {rec['position']}")

    # 全量爬取
    print("\n" + "=" * 50)
    print("执行全量爬取")
    print("=" * 50)

    all_records = scraper.scrape()

    print(f"\n最终结果: {len(all_records)} 条")
    for rec in all_records:
        print(f"  {rec['date']} | {rec['action']} | {rec['name']} | {rec['position']}")


if __name__ == '__main__':
    test_direct_scraper()
