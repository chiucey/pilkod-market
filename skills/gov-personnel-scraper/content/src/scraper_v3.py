#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最终版政府人事任免信息爬虫 v3
修复职务提取不完整的问题
"""

import re
import json
import csv
import time
from datetime import datetime
from typing import List, Dict
import requests
from bs4 import BeautifulSoup


class FinalGovScraper:
    """最终版爬虫"""

    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9",
        "Accept-Language": "zh-CN,zh;q=0.9",
    }

    def get_recent_urls(self) -> List[Dict]:
        """获取近期任免公报URL"""
        return [
            {'title': '国务院任免人员 (2026年3月)', 'url': 'https://www.gov.cn/gongbao/2026/issue_12606/202603/content_7061748.html'},
            {'title': '国务院任免人员 (2026年2月28日)', 'url': 'https://www.gov.cn/gongbao/2026/issue_12586/202602/content_7059932.html'},
            {'title': '国务院任免人员 (2026年2月20日)', 'url': 'https://www.gov.cn/gongbao/2026/issue_12566/202602/content_7057932.html'},
            {'title': '国务院任免人员 (2026年2月10日)', 'url': 'https://www.gov.cn/gongbao/2026/issue_12546/202602/content_7057446.html'},
            {'title': '国务院任免人员 (2026年1月30日)', 'url': 'https://www.gov.cn/gongbao/2026/issue_12526/202601/content_7056482.html'},
        ]

    def parse_article(self, url: str) -> List[Dict]:
        """解析任免文章"""
        try:
            response = requests.get(url, headers=self.HEADERS, timeout=30)
            response.encoding = 'utf-8'
            html = response.text

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
        """从文本提取任免记录 - 修复版"""
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

            # 跳过标题行
            if '中华人民共和国' in line or '国务院任免' in line:
                continue

            # 处理任命 - 格式: 任命XXX为YYY。
            # 问题：正则 `(.+?)` 太贪婪会匹配到句号前的字
            # 修复：使用更精确的模式
            if '任命' in line and '为' in line:
                # 分割多个人员（可能有分号或句号分隔）
                sentences = re.split(r'[；;。]', line)
                for sentence in sentences:
                    sentence = sentence.strip()
                    if '任命' not in sentence or '为' not in sentence:
                        continue

                    # 提取 任命XXX为YYY
                    # 使用贪婪匹配，但确保是完整的职务
                    match = re.search(r'任命(.+?)为(.+)', sentence)
                    if match:
                        name = match.group(1).strip()
                        position = match.group(2).strip()

                        # 验证姓名有效性
                        if name and len(name) >= 2 and len(name) <= 8:
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
                sentences = re.split(r'[；;。]', line)
                for sentence in sentences:
                    sentence = sentence.strip()
                    if '免去' not in sentence:
                        continue

                    # 提取 免去XXX的YYY职务 或 免去XXX的YYY
                    match = re.search(r'免去(.+?)(?:的|)(.+?)(?:职务|)$', sentence)
                    if match:
                        name = match.group(1).strip()
                        position = match.group(2).strip()

                        if name and len(name) >= 2 and len(name) <= 8:
                            records.append({
                                'name': name,
                                'position': position,
                                'action': '免去',
                                'date': current_date,
                                'doc_no': '',
                                'source_url': source_url
                            })

        return records

    def scrape(self) -> List[Dict]:
        """执行爬取"""
        print("[爬虫] 开始爬取国务院公报任免信息...")

        all_records = []
        urls = self.get_recent_urls()

        for item in urls:
            print(f"[爬虫] 正在解析: {item['title']}")
            records = self.parse_article(item['url'])
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


def main():
    """主函数"""
    scraper = FinalGovScraper()
    records = scraper.scrape()

    print("\n" + "=" * 80)
    print("提取结果:")
    print("=" * 80)

    for r in records:
        print(f"{r['date']} | {r['action']:4s} | {r['name']:12s} | {r['position']}")

    # 保存到CSV
    if records:
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
    main()
