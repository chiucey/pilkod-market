#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最终版政府人事任免信息爬虫
修复了编码问题
"""

import re
import json
import csv
import time
from datetime import datetime, timedelta
from typing import List, Dict
from pathlib import Path
import requests
from bs4 import BeautifulSoup


class FixedGovScraper:
    """修复编码问题的爬虫"""

    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    }

    def __init__(self, timeout: int = 30):
        self.session = requests.Session()
        self.timeout = timeout

    def get_recent_urls(self) -> List[Dict]:
        """获取近期任免公报URL"""
        # 已知的近期任免公报页面
        return [
            {'title': '国务院任免人员 (2026年3月)', 'url': 'https://www.gov.cn/gongbao/2026/issue_12606/202603/content_7061748.html'},
            {'title': '国务院任免人员 (2026年2月28日)', 'url': 'https://www.gov.cn/gongbao/2026/issue_12586/202602/content_7059932.html'},
            {'title': '国务院任免人员 (2026年2月20日)', 'url': 'https://www.gov.cn/gongbao/2026/issue_12566/202602/content_7057932.html'},
            {'title': '国务院任免人员 (2026年2月10日)', 'url': 'https://www.gov.cn/gongbao/2026/issue_12546/202602/content_7057446.html'},
            {'title': '国务院任免人员 (2026年1月30日)', 'url': 'https://www.gov.cn/gongbao/2026/issue_12526/202601/content_7056482.html'},
        ]

    def fetch_page(self, url: str) -> str:
        """获取页面内容，修复编码"""
        response = self.session.get(url, headers=self.HEADERS, timeout=self.timeout)
        # 强制使用UTF-8解码
        response.encoding = 'utf-8'
        return response.text

    def parse_article(self, url: str, title: str = '') -> List[Dict]:
        """解析任免文章"""
        try:
            html = self.fetch_page(url)
            soup = BeautifulSoup(html, 'html.parser')

            # 查找文章内容
            content = soup.find('div', class_='article')
            if not content:
                content = soup.find('div', class_=re.compile('TRS_Editor'))
            if not content:
                content = soup.find('div', id='zoom')

            if not content:
                return []

            text = content.get_text(separator='\n', strip=True)

            # 提取记录
            records = self._extract_records(text, url)

            return records

        except Exception as e:
            print(f"[错误] 解析失败 {url}: {e}")
            return []

    def _extract_records(self, text: str, source_url: str) -> List[Dict]:
        """从文本提取任免记录"""
        records = []
        lines = text.split('\n')

        current_date = ''

        for line in lines:
            line = line.strip()
            if not line or len(line) < 3:
                continue

            # 检查日期
            date_match = re.match(r'(\d{4})年(\d{1,2})月(\d{1,2})日', line)
            if date_match:
                current_date = f"{date_match.group(1)}-{date_match.group(2).zfill(2)}-{date_match.group(3).zfill(2)}"
                continue

            # 处理任命 - 格式: 任命XXX为YYY。
            if '任命' in line:
                # 分割多个人员
                parts = re.split(r'[;；]', line)
                for part in parts:
                    part = part.strip()
                    matches = re.findall(r'任命(.+?)为(.+?)[。;；]?', part)
                    for m in matches:
                        name = m[0].strip()
                        position = m[1].strip()
                        if name and position and len(name) >= 2:
                            records.append({
                                'name': name,
                                'position': position,
                                'action': '任命',
                                'date': current_date,
                                'doc_no': '',
                                'source_url': source_url
                            })

            # 处理免职 - 格式: 免去XXX的YYY职务。
            if '免去' in line:
                parts = re.split(r'[;；]', line)
                for part in parts:
                    part = part.strip()
                    matches = re.findall(r'免去(.+?)(?:的|)(.+?)(?:职务|)[。;；]?', part)
                    for m in matches:
                        name = m[0].strip()
                        position = m[1].strip()
                        if name and position and len(name) >= 2:
                            records.append({
                                'name': name,
                                'position': position,
                                'action': '免去',
                                'date': current_date,
                                'doc_no': '',
                                'source_url': source_url
                            })

        return records

    def scrape(self, state_file: str = None) -> List[Dict]:
        """执行爬取"""
        print("[爬虫] 开始爬取国务院公报任免信息...")

        all_records = []
        urls = self.get_recent_urls()

        for item in urls:
            print(f"[爬虫] 正在解析: {item['title']}")
            records = self.parse_article(item['url'], item['title'])
            print(f"[爬虫] 提取到 {len(records)} 条记录")
            all_records.extend(records)

        # 去重
        unique = []
        seen = set()
        for r in all_records:
            key = (r['name'], r['action'], r['position'], r['date'])
            if key not in seen:
                seen.add(key)
                unique.append(r)

        print(f"[爬虫] 共提取 {len(unique)} 条去重后记录")
        return unique


def test_final_scraper():
    """测试最终版爬虫"""
    scraper = FixedGovScraper()

    # 测试抓取
    records = scraper.scrape()

    print("\n" + "=" * 60)
    print("提取结果:")
    print("=" * 60)

    for r in records:
        print(f"{r['date']} | {r['action']:4s} | {r['name']:10s} | {r['position']}")

    print(f"\n共 {len(records)} 条记录")

    # 保存到CSV
    if records:
        import csv
        with open('data/appointments.csv', 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=['id', 'name', 'position', 'action', 'date', 'doc_no', 'source', 'source_url', 'crawl_time', 'batch_id', 'import_method'])
            writer.writeheader()

            for i, r in enumerate(records, 1):
                writer.writerow({
                    'id': f'GOV{i:06d}',
                    'name': r['name'],
                    'position': r['position'],
                    'action': r['action'],
                    'date': r['date'],
                    'doc_no': r.get('doc_no', ''),
                    'source': 'gov.cn',
                    'source_url': r.get('source_url', ''),
                    'crawl_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'batch_id': f'B{datetime.now().strftime("%Y%m%d")}01',
                    'import_method': 'scrape'
                })

        print(f"\n已保存到 data/appointments.csv")


if __name__ == '__main__':
    test_final_scraper()
